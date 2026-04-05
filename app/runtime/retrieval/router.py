"""Role-based context assembly (rule retrieval + optional local indexes)."""

from __future__ import annotations

from pathlib import Path

from app.indexing.config import retrieval_section
from app.indexing.constants import MODE_RULE
from app.runtime.enums import RoleType
from app.runtime.repositories.document_repo import DocumentRepository
from app.runtime.repositories.evidence_repo import EvidenceRepository
from app.runtime.repositories.pedagogy_repo import PedagogyRepository
from app.runtime.repositories.source_repo import SourceRepository
from app.runtime.repositories.topic_repo import TopicRepository
from app.runtime.retrieval import ranker
from app.runtime.retrieval.index_loader import SnapshotIndexes, try_load_indexes
from app.runtime.retrieval.search_pipeline import resolve_query_embedder, search_store
from app.runtime.schemas.context_packet import RoleContextPacket
from app.runtime.schemas.query import EvidenceQuery, PedagogyQuery
from app.schemas.topic_card import TopicCard
from app.runtime.schemas.transcript import TranscriptTurn
from app.runtime.snapshot_loader import SnapshotBundle
from app.runtime.prompt_loader import prompt_template_id_for_role
from app.runtime.render.transcript_window import format_transcript_window


def effective_top_k(role: str, retrieval: dict | None, fallback: int) -> int:
    if not retrieval:
        return fallback
    by = retrieval.get("top_k_by_role") or {}
    r = role.lower().strip()
    if r in by:
        return int(by[r])
    return int(by.get(role, fallback))


def build_repositories(bundle: SnapshotBundle) -> tuple[
    PedagogyRepository,
    TopicRepository,
    EvidenceRepository,
    DocumentRepository,
    SourceRepository,
]:
    return (
        PedagogyRepository(bundle.pedagogy_items),
        TopicRepository(bundle.topic_cards),
        EvidenceRepository(bundle.evidence_index),
        DocumentRepository(bundle.normalized_docs),
        SourceRepository(bundle.source_catalog),
    )


class RoleRouter:
    """Select pedagogy / evidence / topic slices for a role + phase."""

    def __init__(
        self,
        pedagogy: PedagogyRepository,
        topics: TopicRepository,
        evidence: EvidenceRepository,
        documents: DocumentRepository,
        snapshot_dir: Path | None = None,
    ) -> None:
        self.pedagogy = pedagogy
        self.topics = topics
        self.evidence = evidence
        self.documents = documents
        self._snapshot_dir = snapshot_dir
        self._indexes: SnapshotIndexes | None = try_load_indexes(snapshot_dir) if snapshot_dir else None

    def _query_text(self, card: TopicCard | None, recent_turns: list[TranscriptTurn] | None) -> str:
        parts: list[str] = []
        if card:
            if card.topic:
                parts.append(card.topic)
            parts.extend(card.tags or [])
        if recent_turns:
            t = recent_turns[-1]
            if getattr(t, "speaker_role", "") == "user" and getattr(t, "text", ""):
                parts.append(t.text)
        q = " ".join(p for p in parts if p).strip()
        return q or (card.topic if card else "discussion")

    def _rule_retrieve(
        self,
        r: str,
        tk: int,
        card,
        feedback_signals: list[dict] | None,
    ) -> tuple[list, list]:
        ped_items: list = []
        ev_items: list = []
        if r == RoleType.MODERATOR.value:
            pq = PedagogyQuery(item_type="rule", top_k=tk)
            ped_items.extend([p.model_dump() for p in ranker.rank_pedagogy(self.pedagogy.list_items(), pq)])
            pq2 = PedagogyQuery(item_type="language_bank", top_k=tk)
            lang = ranker.rank_pedagogy(self.pedagogy.list_items(), pq2)
            ped_items.extend([p.model_dump() for p in lang[:tk]])
            ev_items.extend(
                [e.model_dump() for e in ranker.rank_evidence(self.evidence.list_evidence(), EvidenceQuery(top_k=2))]
            )
        elif r == RoleType.COACH.value:
            for it in ("rubric", "coaching_tip", "rule"):
                pq = PedagogyQuery(item_type=it, top_k=tk)
                ped_items.extend([p.model_dump() for p in ranker.rank_pedagogy(self.pedagogy.list_items(), pq)])
            if feedback_signals:
                tags = [str(s.get("id", "")) for s in feedback_signals if s.get("id")]
                pq = PedagogyQuery(item_type="coaching_tip", tags=tags[:5], top_k=tk)
                ped_items.extend([p.model_dump() for p in ranker.rank_pedagogy(self.pedagogy.list_items(), pq)])
            ev_items.extend(
                [
                    e.model_dump()
                    for e in ranker.rank_evidence(
                        self.evidence.list_evidence(),
                        EvidenceQuery(topic_tag=(card.tags[0] if card and card.tags else None), top_k=min(3, tk)),
                    )
                ]
            )
        elif r == RoleType.ALLY.value:
            tag = card.tags[0] if card and card.tags else None
            evq = EvidenceQuery(
                topic_tag=tag,
                stance_hint="for",
                top_k=tk,
                keyword=card.topic if card else None,
            )
            pool = self.evidence.list_evidence()
            ranked = ranker.rank_evidence(pool, evq)
            if len(ranked) < tk // 2:
                evq2 = EvidenceQuery(topic_tag=tag, top_k=tk)
                ranked = ranker.rank_evidence(pool, evq2)
            ev_items = [e.model_dump() for e in ranked]
            lang = self.pedagogy.get_by_type("language_bank")[:tk]
            ped_items = [p.model_dump() for p in lang]
        elif r == RoleType.OPPONENT.value:
            tag = card.tags[0] if card and card.tags else None
            evq = EvidenceQuery(
                topic_tag=tag,
                stance_hint="against",
                top_k=tk,
                keyword=card.topic if card else None,
            )
            pool = self.evidence.list_evidence()
            ranked = ranker.rank_evidence(pool, evq)
            if len(ranked) < tk // 2:
                evq2 = EvidenceQuery(topic_tag=tag, top_k=tk)
                ranked = ranker.rank_evidence(pool, evq2)
            ev_items = [e.model_dump() for e in ranked]
            lang = self.pedagogy.get_by_type("language_bank")[:tk]
            ped_items = [p.model_dump() for p in lang]
        else:
            ped_items = []
            ev_items = []
        return ped_items, ev_items

    def _try_indexed(
        self,
        *,
        role: str,
        tk: int,
        retrieval: dict | None,
        card,
        recent_turns: list[TranscriptTurn] | None,
        feedback_signals: list[dict] | None,
    ) -> tuple[list, list] | None:
        if not self._indexes:
            return None
        rc = retrieval_section(retrieval or {})
        mode = str(rc.get("mode", MODE_RULE)).lower().strip()
        if mode == MODE_RULE or mode == "rules":
            return None
        if not rc.get("use_indexes_if_available", True):
            return None
        ped_store = self._indexes.stores.get("pedagogy")
        ev_store = self._indexes.stores.get("evidence")
        if not ped_store and not ev_store:
            return None
        emb = resolve_query_embedder(self._indexes.manifest.embedder_name, self._indexes.manifest.dimension)
        qtext = self._query_text(card, recent_turns)
        tags = list(card.tags) if card else []
        r = role.lower().strip()

        def _map_ped(hits):
            out: list = []
            seen: set[str] = set()
            for h in hits:
                p = self.pedagogy.get_by_item_id(h.item_id)
                if not p:
                    continue
                if p.item_id in seen:
                    continue
                seen.add(p.item_id)
                out.append(p.model_dump())
            return out

        def _map_ev(hits):
            out: list = []
            seen: set[str] = set()
            for h in hits:
                e = self.evidence.get_by_evidence_id(h.item_id)
                if not e:
                    continue
                if e.evidence_id in seen:
                    continue
                seen.add(e.evidence_id)
                out.append(e.model_dump())
            return out

        ped_items: list = []
        ev_items: list = []

        if r == RoleType.MODERATOR.value:
            if ped_store:
                hits = search_store(
                    ped_store,
                    emb,
                    qtext,
                    mode=mode,
                    retrieval=rc,
                    query_tags=tags,
                    store_name="pedagogy",
                )
                ped_items.extend(_map_ped(hits)[: tk * 2])
            if ev_store:
                hits = search_store(
                    ev_store,
                    emb,
                    qtext,
                    mode=mode,
                    retrieval={**rc, "final_top_k": 2},
                    query_tags=tags,
                    store_name="evidence",
                )
                ev_items.extend(_map_ev(hits))
        elif r == RoleType.COACH.value:
            if ped_store:
                hits = search_store(
                    ped_store,
                    emb,
                    qtext,
                    mode=mode,
                    retrieval={**rc, "final_top_k": tk * 3},
                    query_tags=tags,
                    store_name="pedagogy",
                )
                mapped = _map_ped(hits)
                allow = {"rubric", "coaching_tip", "rule"}
                ped_items.extend([x for x in mapped if str(x.get("item_type")) in allow][: tk * 3])
            if ev_store:
                hits = search_store(
                    ev_store,
                    emb,
                    qtext,
                    mode=mode,
                    retrieval={**rc, "final_top_k": min(3, tk)},
                    query_tags=tags,
                    store_name="evidence",
                )
                ev_items.extend(_map_ev(hits))
        elif r in (RoleType.ALLY.value, RoleType.OPPONENT.value):
            stance = "for" if r == RoleType.ALLY.value else "against"
            if ev_store:
                hits = search_store(
                    ev_store,
                    emb,
                    f"{qtext} {stance}",
                    mode=mode,
                    retrieval=rc,
                    query_tags=tags,
                    store_name="evidence",
                )
                pool = _map_ev(hits)
                boosted = [x for x in pool if (x.get("stance_hint") or "") == stance] or pool
                ev_items.extend(boosted[:tk])
            if ped_store:
                hits = search_store(
                    ped_store,
                    emb,
                    qtext,
                    mode=mode,
                    retrieval={**rc, "final_top_k": tk},
                    query_tags=tags,
                    store_name="pedagogy",
                )
                mapped = _map_ped(hits)
                ped_items.extend([x for x in mapped if str(x.get("item_type")) == "language_bank"][:tk])
        else:
            return None

        if not ped_items and not ev_items:
            return None
        return ped_items, ev_items

    def build_context_packet(
        self,
        *,
        role: str,
        topic_id: str | None,
        session_phase: str,
        top_k: int = 5,
        retrieval: dict | None = None,
        recent_turns: list[TranscriptTurn] | None = None,
        user_stance: str | None = None,
        feedback_signals: list[dict] | None = None,
        participant_context: dict | None = None,
    ) -> RoleContextPacket:
        tk = effective_top_k(role, retrieval, top_k)
        phase = session_phase or "discussion"
        topic_card_dict: dict | None = None
        card = self.topics.get_topic(topic_id) if topic_id else None
        if card:
            topic_card_dict = card.model_dump()

        meta: dict = {"role": role, "phase": phase, "topic_id": topic_id}
        if user_stance:
            meta["user_stance"] = user_stance
        if recent_turns:
            meta["transcript_window"] = format_transcript_window(recent_turns)
        if feedback_signals is not None:
            meta["feedback_signals"] = feedback_signals

        r = role.lower().strip()

        ped_items: list = []
        ev_items: list = []

        indexed = self._try_indexed(
            role=r,
            tk=tk,
            retrieval=retrieval,
            card=card,
            recent_turns=recent_turns,
            feedback_signals=feedback_signals,
        )
        if indexed is not None:
            ped_items, ev_items = indexed
            rc = retrieval_section(retrieval or {})
            meta["retrieval_mode"] = str(rc.get("mode", "rule"))
            meta["indexed"] = True
        else:
            if r == RoleType.USER.value:
                meta["hint"] = "preparation and summary materials"
            else:
                ped_items, ev_items = self._rule_retrieve(r, tk, card, feedback_signals)
            meta["retrieval_mode"] = str((retrieval or {}).get("mode", "rule"))
            meta["indexed"] = False

        pid = prompt_template_id_for_role(r)
        ped_slice = ped_items[: max(8, tk * 3)]
        ev_slice = ev_items[: max(8, tk * 3)]
        used_p = [str(x["item_id"]) for x in ped_slice if x.get("item_id")]
        used_e = [str(x["evidence_id"]) for x in ev_slice if x.get("evidence_id")]
        pc = participant_context or {}
        if pc:
            meta["participant_context"] = pc
        return RoleContextPacket(
            role=r,
            topic_id=topic_id,
            session_phase=phase,
            topic_card=topic_card_dict,
            pedagogy_items=ped_slice,
            evidence_items=ev_slice,
            used_pedagogy_item_ids=used_p,
            used_evidence_ids=used_e,
            prompt_template_id=pid,
            participant_id=pc.get("participant_id"),
            participant_display_name=pc.get("display_name"),
            seat_label=pc.get("seat_label"),
            team_id=pc.get("team_id"),
            relation_to_user=pc.get("relation_to_user"),
            participant_memory_summary=pc.get("participant_memory_summary"),
            team_memory_summary=pc.get("team_memory_summary"),
            roster_context_summary=pc.get("roster_context_summary"),
            metadata=meta,
        )
