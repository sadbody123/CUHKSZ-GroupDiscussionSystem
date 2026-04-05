"""Indexing / retrieval CLI (phase 8)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from app.application.config import AppConfig
from app.indexing.schemas.index_manifest import IndexManifest
from app.offline_build.indexes.builder import build_snapshot_indexes
from app.runtime.profile_resolver import resolve_runtime_profile
from app.runtime.retrieval.index_loader import try_load_indexes
from app.runtime.retrieval.search_pipeline import resolve_query_embedder, search_store

def register_flat_index_commands(app: typer.Typer) -> None:
    """Register top-level ``build-index``, ``inspect-index``, etc."""

    @app.command("build-index")
    def build_index_cmd(
        snapshot_id: str = typer.Option(..., "--snapshot-id", "-s"),
        embedder: str = typer.Option("hash", "--embedder", "-e"),
        stores: str = typer.Option("evidence,pedagogy,topics", "--stores"),
        modes: str = typer.Option("lexical,vector", "--modes"),
        dimension: int = typer.Option(128, "--dimension", "-d"),
    ) -> None:
        """Build local indexes under snapshot ``indexes/``."""
        cfg = AppConfig.from_env()
        snap_root = cfg.snapshot_root / snapshot_id
        if not snap_root.is_dir():
            typer.echo(f"snapshot not found: {snap_root}", err=True)
            raise typer.Exit(1)
        store_list = [x.strip() for x in stores.split(",") if x.strip()]
        mode_list = [x.strip().lower() for x in modes.split(",") if x.strip()]
        man = build_snapshot_indexes(snap_root, stores=store_list, modes=mode_list, embedder=embedder, dimension=dimension)
        typer.echo(man.model_dump_json(indent=2))

    @app.command("inspect-index")
    def inspect_index_cmd(
        snapshot_id: str = typer.Option(..., "--snapshot-id", "-s"),
    ) -> None:
        """Show index manifest summary."""
        cfg = AppConfig.from_env()
        mf = cfg.snapshot_root / snapshot_id / "indexes" / "manifest.json"
        if not mf.is_file():
            typer.echo(json.dumps({"has_indexes": False, "snapshot_id": snapshot_id}, indent=2))
            return
        man = IndexManifest.model_validate(json.loads(mf.read_text(encoding="utf-8")))
        typer.echo(
            json.dumps(
                {
                    "has_indexes": True,
                    "snapshot_id": snapshot_id,
                    "embedder_name": man.embedder_name,
                    "dimension": man.dimension,
                    "stores": man.stores,
                    "available_modes": man.available_modes,
                    "item_counts": man.item_counts,
                },
                indent=2,
                ensure_ascii=False,
            )
        )

    @app.command("search-evidence")
    def search_evidence_cmd(
        snapshot_id: str = typer.Option(..., "--snapshot-id", "-s"),
        query: str = typer.Option(..., "--query", "-q"),
        topic_id: Optional[str] = typer.Option(None, "--topic-id", "-t"),
        role: str = typer.Option("ally", "--role", "-r"),
        phase: str = typer.Option("discussion", "--phase", "-p"),
        profile_id: str = typer.Option("default", "--profile-id"),
        top_k: int = typer.Option(5, "--top-k", "-k"),
    ) -> None:
        """Run indexed evidence search (requires indexes)."""
        cfg = AppConfig.from_env()
        snap = cfg.snapshot_root / snapshot_id
        loaded = try_load_indexes(snap)
        if not loaded or not loaded.stores.get("evidence"):
            typer.echo("indexes not available for evidence", err=True)
            raise typer.Exit(1)
        prof = resolve_runtime_profile(profile_id)
        rc = dict(prof.retrieval)
        rc.setdefault("final_top_k", top_k)
        rc.setdefault("lexical_top_k", max(10, top_k))
        rc.setdefault("vector_top_k", max(10, top_k))
        emb = resolve_query_embedder(loaded.manifest.embedder_name, loaded.manifest.dimension)
        st = loaded.stores["evidence"]
        mode = str(rc.get("mode", "hybrid")).lower()
        hits = search_store(st, emb, query, mode=mode, retrieval=rc, query_tags=[], store_name="evidence")
        typer.echo(json.dumps([h.model_dump() for h in hits], ensure_ascii=False, indent=2))

    @app.command("search-pedagogy")
    def search_pedagogy_cmd(
        snapshot_id: str = typer.Option(..., "--snapshot-id", "-s"),
        query: str = typer.Option(..., "--query", "-q"),
        role: str = typer.Option("coach", "--role", "-r"),
        phase: str = typer.Option("feedback", "--phase", "-p"),
        profile_id: str = typer.Option("strict_coach", "--profile-id"),
        top_k: int = typer.Option(5, "--top-k", "-k"),
    ) -> None:
        """Run indexed pedagogy search."""
        cfg = AppConfig.from_env()
        snap = cfg.snapshot_root / snapshot_id
        loaded = try_load_indexes(snap)
        if not loaded or not loaded.stores.get("pedagogy"):
            typer.echo("indexes not available for pedagogy", err=True)
            raise typer.Exit(1)
        prof = resolve_runtime_profile(profile_id)
        rc = dict(prof.retrieval)
        rc.setdefault("final_top_k", top_k)
        emb = resolve_query_embedder(loaded.manifest.embedder_name, loaded.manifest.dimension)
        st = loaded.stores["pedagogy"]
        mode = str(rc.get("mode", "lexical")).lower()
        hits = search_store(st, emb, query, mode=mode, retrieval=rc, query_tags=[], store_name="pedagogy")
        typer.echo(json.dumps([h.model_dump() for h in hits], ensure_ascii=False, indent=2))

    @app.command("benchmark-retrieval")
    def benchmark_retrieval_cmd(
        suite_file: Path = typer.Option(..., "--suite-file", exists=True, dir_okay=False),
        snapshot_dir: Path = typer.Option(..., "--snapshot-dir", exists=True, file_okay=False, dir_okay=True),
        profile_id: str = typer.Option("hybrid_default", "--profile-id"),
        output_dir: Path = typer.Option(..., "--output-dir", "-o"),
    ) -> None:
        """Run retrieval benchmark suite (reuses eval framework)."""
        from app.evals.run_suite import run_eval_suite

        run_eval_suite(suite_file=suite_file, snapshot_dir=snapshot_dir, profile_id=profile_id, output_dir=output_dir)
        typer.echo(f"Wrote reports under {output_dir.resolve()}")
