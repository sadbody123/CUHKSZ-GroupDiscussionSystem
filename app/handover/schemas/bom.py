"""Bill of materials."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BillOfMaterialsEntry(BaseModel):
    bom_item_id: str
    kind: str
    ref_id: str | None = None
    path: str
    version: str | None = None
    checksum: str | None = None
    required_for_demo: bool = False
    required_for_handover: bool = False
    status: str = "ok"
    metadata: dict = Field(default_factory=dict)


class BillOfMaterials(BaseModel):
    bom_id: str
    profile_id: str
    created_at: str
    entries: list[BillOfMaterialsEntry] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
