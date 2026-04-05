"""Pedagogy KB repository (read-only)."""

from __future__ import annotations

from app.schemas.pedagogy import PedagogyItem


class PedagogyRepository:
    def __init__(self, items: list[PedagogyItem]) -> None:
        self._items = list(items)

    def get_by_item_id(self, item_id: str) -> PedagogyItem | None:
        for x in self._items:
            if x.item_id == item_id:
                return x
        return None

    def list_items(self) -> list[PedagogyItem]:
        return list(self._items)

    def get_by_type(self, item_type: str) -> list[PedagogyItem]:
        it = item_type.lower().strip()
        return [x for x in self._items if x.item_type.lower() == it]

    def filter(
        self,
        *,
        category: str | None = None,
        tags: list[str] | None = None,
        language: str | None = None,
        top_k: int | None = None,
    ) -> list[PedagogyItem]:
        out: list[PedagogyItem] = []
        tag_set = {t.lower() for t in (tags or []) if t}
        for x in self._items:
            if category and (x.category or "").lower() != category.lower():
                continue
            if language and (x.language or "").lower() != language.lower():
                continue
            if tag_set:
                xt = {t.lower() for t in x.tags}
                if not tag_set.intersection(xt):
                    continue
            out.append(x)
            if top_k is not None and len(out) >= top_k:
                break
        return out if top_k is None else out[: top_k]
