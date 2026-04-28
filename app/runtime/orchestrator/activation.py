"""Multi-agent activation strategies adapted from SillyTavern's group-chats.js.

Provides 4 activation modes for determining which agents speak next:
  - NATURAL:  mentions in user text + talkativeness roll + random fallback
  - LIST:     all enabled agents in defined order (cycle through participants)
  - POOLED:   round-robin: agents who haven't spoken since last user turn get priority
  - MANUAL:   user manually designates the next speaker via API
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum

from app.runtime.enums import RoleType
from app.runtime.schemas.session import SessionContext


class ActivationStrategy(Enum):
    NATURAL = "natural"
    LIST = "list"
    POOLED = "pooled"
    MANUAL = "manual"


@dataclass
class ActivationPlan:
    participant_ids: list[str] = field(default_factory=list)
    strategy: ActivationStrategy = ActivationStrategy.LIST
    reason: str = ""


def _agent_participants(session: SessionContext) -> list[dict]:
    if not session.participants:
        return []
    return [
        p for p in session.participants
        if str(p.get("controller_type", "")).lower() != "user"
    ]


def _user_participant_id(session: SessionContext) -> str | None:
    if session.user_participant_id:
        return session.user_participant_id
    for p in session.participants or []:
        if str(p.get("relation_to_user", "")).lower() == "self":
            return str(p.get("participant_id", ""))
    return None


def _talkativeness(p: dict) -> float:
    mem = p.get("participant_memory_state") or {}
    val = mem.get("talkativeness", 0.5)
    try:
        return max(0.0, min(1.0, float(val)))
    except (ValueError, TypeError):
        return 0.5


def _extract_words(text: str) -> list[str]:
    import re
    return [w.lower() for w in re.findall(r"\w+", text)]


def _last_non_user_speaker(session: SessionContext) -> str | None:
    for t in reversed(session.turns):
        if t.speaker_role != RoleType.USER.value:
            pid = getattr(t, "participant_id", None) or (t.metadata or {}).get("participant_id")
            return str(pid) if pid else None
    return None


class ActivationEngine:
    def activate(
        self,
        session: SessionContext,
        strategy: str,
        *,
        user_text: str = "",
        last_role: str | None = None,
    ) -> ActivationPlan:
        st = ActivationStrategy(strategy) if strategy in {s.value for s in ActivationStrategy} else ActivationStrategy.LIST

        if st == ActivationStrategy.NATURAL:
            return self._activate_natural(session, user_text)
        if st == ActivationStrategy.LIST:
            return self._activate_list(session, last_role)
        if st == ActivationStrategy.POOLED:
            return self._activate_pooled(session)
        if st == ActivationStrategy.MANUAL:
            return self._activate_manual(session)
        return ActivationPlan(strategy=ActivationStrategy.LIST, reason="fallback_default")

    def _activate_natural(self, session: SessionContext, user_text: str) -> ActivationPlan:
        agents = _agent_participants(session)
        if not agents:
            return ActivationPlan(strategy=ActivationStrategy.NATURAL, reason="no_agents")

        user_pid = _user_participant_id(session)
        banned = _last_non_user_speaker(session) if not session.allow_consecutive_agent_turns else None

        activated: list[str] = []

        # Step 1: mentions in user text
        if user_text:
            input_words = _extract_words(user_text)
            for agent in agents:
                pid = str(agent.get("participant_id", ""))
                display = str(agent.get("display_name", "")).lower()
                disp_words = _extract_words(display)
                if any(w in input_words for w in disp_words):
                    if pid != banned and pid != user_pid:
                        activated.append(pid)

        # Step 2: talkativeness roll (shuffled, SillyTavern style)
        shuffled = list(agents)
        random.shuffle(shuffled)
        for agent in shuffled:
            pid = str(agent.get("participant_id", ""))
            if pid in activated or pid == banned or pid == user_pid:
                continue
            roll = random.random()
            if _talkativeness(agent) >= roll:
                activated.append(pid)

        # Step 3: random fallback if no one activated
        if not activated and agents:
            chatty = [a for a in agents if _talkativeness(a) > 0]
            pool = chatty if chatty else agents
            retries = 0
            while not activated and retries < len(pool) * 2:
                retries += 1
                pick = random.choice(pool)
                pid = str(pick.get("participant_id", ""))
                if pid != banned and pid != user_pid:
                    activated.append(pid)

        seen = set[str]()
        deduped = [pid for pid in activated if not (pid in seen or seen.add(pid))]
        return ActivationPlan(
            participant_ids=deduped,
            strategy=ActivationStrategy.NATURAL,
            reason=f"natural: mentions/talkativeness -> {len(deduped)} speakers",
        )

    def _activate_list(self, session: SessionContext, last_role: str | None) -> ActivationPlan:
        agents = _agent_participants(session)
        if not agents:
            return ActivationPlan(strategy=ActivationStrategy.LIST, reason="no_agents")

        sorted_agents = sorted(agents, key=lambda a: str(a.get("participant_id", "")))
        all_pids = [str(a.get("participant_id", "")) for a in sorted_agents]

        if not session.turns:
            return ActivationPlan(
                participant_ids=all_pids,
                strategy=ActivationStrategy.LIST,
                reason="list: first round, all agents",
            )

        last_speaker = None
        for t in reversed(session.turns):
            pid = getattr(t, "participant_id", None) or (t.metadata or {}).get("participant_id")
            if pid and t.speaker_role != RoleType.USER.value:
                last_speaker = str(pid)
                break

        if not last_speaker or last_speaker not in all_pids:
            return ActivationPlan(
                participant_ids=all_pids,
                strategy=ActivationStrategy.LIST,
                reason="list: fresh cycle, all agents",
            )

        idx = all_pids.index(last_speaker)
        ordered = all_pids[idx + 1:] + all_pids[:idx + 1]
        return ActivationPlan(
            participant_ids=ordered,
            strategy=ActivationStrategy.LIST,
            reason=f"list: cycle starting after {last_speaker}, {len(ordered)} speakers",
        )

    def _activate_pooled(self, session: SessionContext) -> ActivationPlan:
        agents = _agent_participants(session)
        if not agents:
            return ActivationPlan(strategy=ActivationStrategy.POOLED, reason="no_agents")

        spoken_since_user: set[str] = set()
        for t in reversed(session.turns):
            if t.speaker_role == RoleType.USER.value:
                break
            pid = getattr(t, "participant_id", None) or (t.metadata or {}).get("participant_id")
            if pid:
                spoken_since_user.add(str(pid))

        all_pids = [str(a.get("participant_id", "")) for a in agents]
        unspoken = [pid for pid in all_pids if pid not in spoken_since_user]

        if unspoken:
            pick = random.choice(unspoken)
            return ActivationPlan(
                participant_ids=[pick],
                strategy=ActivationStrategy.POOLED,
                reason=f"pooled: unspoken priority -> {pick}",
            )

        last_ns = _last_non_user_speaker(session)
        pool = [pid for pid in all_pids if pid != last_ns] if last_ns else all_pids
        if pool:
            pick = random.choice(pool)
            return ActivationPlan(
                participant_ids=[pick],
                strategy=ActivationStrategy.POOLED,
                reason=f"pooled: random from pool -> {pick}",
            )

        return ActivationPlan(strategy=ActivationStrategy.POOLED, reason="pooled: fallback empty")

    def _activate_manual(self, session: SessionContext) -> ActivationPlan:
        candidates = list(session.next_candidate_participant_ids or [])
        if candidates:
            return ActivationPlan(
                participant_ids=candidates[:1],
                strategy=ActivationStrategy.MANUAL,
                reason=f"manual: designated -> {candidates[0]}",
            )
        return ActivationPlan(strategy=ActivationStrategy.MANUAL, reason="manual: awaiting user designation")
