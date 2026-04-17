"""TripleLoader facade.

Spec reference: files/01-triple-loader.md
"""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Optional

from triple_flow_sim.config import Config
from triple_flow_sim.contracts.triple import LoadReport, Triple, TripleSet

from .adapter_mda import discover_triple_dirs, load_mda_triple
from .adapter_native import discover_files, load_triple as load_native_triple
from .normalizer import normalize, validate_identity
from .source_git import clone_or_update
from .source_local import resolve_local

log = logging.getLogger(__name__)


class TripleLoader:
    """Facade for component 01.

    Config keys (spec §Inputs):
      source_format:                  mda_triple_dir | native_yaml | native_json
      source.type:                    local | git
      source.path:                    (for local)
      source.ssh_url, source.branch:  (for git)
      field_mapping:                  dict (unused in Phase 1, reserved)
      content_chunk_extraction.by_section: bool
      strict_mode:                    bool
      ignore_paths:                   list[str]
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.source_format: str = config.get("source_format", "mda_triple_dir")
        self.strict_mode: bool = bool(config.get("strict_mode", False))
        self.ignore_paths: list[str] = list(config.get("ignore_paths", []) or [])
        self.field_mapping: dict = dict(config.get("field_mapping", {}) or {})
        self.cache_root: Path = (
            Path(config.get("cache_root", "")).resolve()
            if config.get("cache_root")
            else (config.project_root / "cache").resolve()
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> tuple[TripleSet, LoadReport]:
        """Execute the load pipeline (steps B1..B8)."""
        report = LoadReport(source_format=self.source_format)

        # B1 — Resolve source.
        source_path = self._resolve_source()
        report.source_path = str(source_path)

        # B2 — Discover files/dirs.
        loaded: list[Triple] = []

        if self.source_format == "mda_triple_dir":
            triple_dirs = discover_triple_dirs(source_path, self.ignore_paths)
            report.total_files_attempted = len(triple_dirs)
            bpmn_content = self._find_bpmn_content(source_path)
            for td in triple_dirs:
                # B3 — Parse (malformed → LoadReport.failed_loads).
                triple, err = load_mda_triple(td, bpmn_content=bpmn_content)
                if err or triple is None:
                    report.failed_loads.append(err or {"path": str(td),
                                                        "error_message": "unknown"})
                    continue
                loaded.append(triple)
        elif self.source_format in ("native_yaml", "native_json"):
            files = discover_files(source_path, self.source_format, self.ignore_paths)
            report.total_files_attempted = len(files)
            for fp in files:
                triple, err = load_native_triple(fp, self.source_format)
                if err or triple is None:
                    report.failed_loads.append(err or {"path": str(fp),
                                                        "error_message": "unknown"})
                    continue
                loaded.append(triple)
        else:
            raise ValueError(f"Unsupported source_format: {self.source_format}")

        # B4 — Field mapping (reserved; no-op in Phase 1).
        report.field_mapping_applied = dict(self.field_mapping)

        # B5/B6 — Validate identity & normalize.
        accepted: list[Triple] = []
        for triple in loaded:
            missing = validate_identity(triple)
            if missing:
                report.identity_failures.append(
                    {
                        "path": triple.source_path or "",
                        "missing_fields": missing,
                    }
                )
                continue
            accepted.append(normalize(triple))

        report.successful_loads = len(accepted)

        # B7 — Corpus version hash: SHA256 of sorted (triple_id, version) pairs.
        corpus_hash = _compute_corpus_hash(accepted)
        report.corpus_version_hash = corpus_hash

        triple_set = TripleSet(
            triples={t.triple_id: t for t in accepted},
            corpus_version_hash=corpus_hash,
        )

        # B8 — Cache each triple as JSON.
        self._write_cache(triple_set, corpus_hash)

        return triple_set, report

    def load_from_cache(self, corpus_version_hash: str) -> TripleSet:
        """Load a previously-cached TripleSet by hash."""
        cache_dir = self.cache_root / "triples" / corpus_version_hash
        if not cache_dir.is_dir():
            raise FileNotFoundError(
                f"No cached triples at {cache_dir}. "
                f"Run load() first or check the hash."
            )
        triples: dict[str, Triple] = {}
        for jf in sorted(cache_dir.glob("*.json")):
            data = jf.read_text(encoding="utf-8")
            triple = Triple.model_validate_json(data)
            triples[triple.triple_id] = triple
        return TripleSet(triples=triples, corpus_version_hash=corpus_version_hash)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_source(self) -> Path:
        source_type = self.config.get("source.type", "local")
        if source_type == "local":
            raw_path = self.config.get("source.path")
            if not raw_path:
                raise ValueError("source.path is required when source.type=local")
            path = Path(raw_path)
            if not path.is_absolute():
                path = (self.config.project_root / path).resolve()
            return resolve_local(path)
        if source_type == "git":
            ssh_url = self.config.get("source.ssh_url") or self.config.get(
                "source.https_url"
            )
            branch = self.config.get("source.branch", "main")
            if not ssh_url:
                raise ValueError("source.ssh_url is required when source.type=git")
            cache_root = self.cache_root / "repos"
            local = clone_or_update(ssh_url, branch=branch, cache_root=cache_root)
            subdir = self.config.get("source.subdir")
            if subdir:
                local = (local / subdir).resolve()
            return resolve_local(local)
        raise ValueError(f"Unsupported source.type: {source_type}")

    def _find_bpmn_content(self, source_path: Path) -> Optional[str]:
        """Find the first .bpmn file under source_path/bpmn/ and return its XML."""
        bpmn_dir = source_path / "bpmn"
        if not bpmn_dir.is_dir():
            # Fallback — any bpmn file in source_path.
            matches = sorted(source_path.rglob("*.bpmn"))
        else:
            matches = sorted(bpmn_dir.glob("*.bpmn"))
        if not matches:
            return None
        try:
            return matches[0].read_text(encoding="utf-8")
        except OSError as exc:
            log.warning("Failed to read BPMN file %s: %s", matches[0], exc)
            return None

    def _write_cache(self, triple_set: TripleSet, corpus_hash: str) -> None:
        """B8 — cache each triple as JSON under cache/triples/<hash>/."""
        if not corpus_hash:
            return
        cache_dir = self.cache_root / "triples" / corpus_hash
        cache_dir.mkdir(parents=True, exist_ok=True)
        for triple_id, triple in triple_set.triples.items():
            safe_name = _safe_filename(triple_id) + ".json"
            (cache_dir / safe_name).write_text(
                triple.model_dump_json(indent=2), encoding="utf-8"
            )


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _compute_corpus_hash(triples: list[Triple]) -> str:
    """SHA256 of sorted (triple_id, version) pairs."""
    pairs = sorted((t.triple_id, t.version) for t in triples)
    h = hashlib.sha256()
    for tid, ver in pairs:
        h.update(f"{tid}\x1f{ver}\x1e".encode("utf-8"))
    return h.hexdigest()


_UNSAFE_FILENAME_CHARS = str.maketrans({
    "/": "_", "\\": "_", ":": "_", "*": "_", "?": "_",
    '"': "_", "<": "_", ">": "_", "|": "_",
})


def _safe_filename(name: str) -> str:
    return (name or "unnamed").translate(_UNSAFE_FILENAME_CHARS)
