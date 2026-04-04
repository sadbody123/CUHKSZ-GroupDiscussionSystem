"""Role-based context assembly (rule retrieval, no LLM)."""

from __future__ import annotations

from app.runtime.enums import RoleType
from app.runtime.repositories.document_repo import DocumentRepository
from app.runtime.repositories.evidence_repo import EvidenceRepository
from app.runtime.repositories.pedagogy_repo import PedagogyRepository
from app.runtime.repositories.source_repo import SourceRepository
from app.runtime.repositories.topic_repo import TopicRepository
from app.runtime.retrieval import ranker
from app.runtime.schemas.context_packet import RoleContextPacket
from app.runtime.schemas.query import EvidenceQuery, PedagogyQuery
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
    ) -> None:
        self.pedagogy = pedagogy
        self.topics = topics
        self.evidence = evidence
        self.documents = documents

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
    ) -> RoleContextPacket:
        tk = effective_top_k(role, retrieval, top_k)
        phase = session_phase or "discussion"
        topic_card_dict: dict | None = None
        card = self.topics.get_topic(topic_id) if topic_id else None
        if card:
            topic_card_dict = card.model_dump()

        ped_items: list = []
        ev_items: list = []
        meta: dict = {"role": role, "phase": phase, "topic_id": topic_id}
        if user_stance:
            meta["user_stance"] = user_stance
        if recent_turns:
            meta["transcript_window"] = format_transcript_window(recent_turns)
        if feedback_signals is not None:
            meta["feedback_signals"] = feedback_signals

        r = role.lower().strip()

        if r == RoleType.MODERATOR.value:
            pq = PedagogyQuery(item_type="rule", top_k=tk)
            ped_items.extend([p.model_dump() for p in ranker.rank_pedagogy(self.pedagogy.list_items(), pq)])
            pq2 = PedagogyQuery(item_type="language_bank", top_k=tk)
            lang = ranker.rank_pedagogy(self.pedagogy.list_items(), pq2)
            ped_items.extend([p.model_dump() for p in lang[:tk]])
            # light evidence
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
            # user: summary prep
            meta["hint"] = "preparation and summary materials"
            if card:
                ped_items = []
                ev_items = []

        pid = prompt_template_id_for_role(r)
        ped_slice = ped_items[: max(8, tk * 3)]
        ev_slice = ev_items[: max(8, tk * 3)]
        used_p = [str(x["item_id"]) for x in ped_slice if x.get("item_id")]
        used_e = [str(x["evidence_id"]) for x in ev_slice if x.get("evidence_id")]
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
            metadata=meta,
        )
