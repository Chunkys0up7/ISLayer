"""Corpus loader — loads knowledge corpus from local filesystem or S3."""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
def _load_io(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mda_io", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
yaml_io = _load_io("yaml_io")


def load_corpus(config, force_refresh: bool = False) -> Path:
    """Load corpus from configured source and return the local path.

    Config keys:
        corpus.source: "local" (default) or "s3"
        corpus.local_path: relative or absolute path (used when source=local)
        corpus.s3.bucket: S3 bucket name
        corpus.s3.prefix: S3 key prefix (default: "corpus/")
        corpus.s3.region: AWS region
        corpus.s3.sync_to: local cache directory (default: ".corpus-cache/")

    Returns:
        Path to the local corpus directory (either the configured local path
        or the S3 cache directory after sync).
    """
    source = config.get("corpus.source", "local")

    if source == "s3":
        return _load_from_s3(config, force_refresh)
    else:
        return _load_from_local(config)


def _load_from_local(config) -> Path:
    """Load corpus from a local directory."""
    # Try multiple config key patterns
    local_path = config.get("corpus.local_path") or config.get("paths.corpus") or "../../corpus"

    if os.path.isabs(local_path):
        corpus_dir = Path(local_path)
    else:
        corpus_dir = (config.project_root / local_path).resolve()

    if not corpus_dir.exists():
        raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")

    return corpus_dir


def _load_from_s3(config, force_refresh: bool = False) -> Path:
    """Sync corpus from S3 to local cache."""
    bucket = config.get("corpus.s3.bucket")
    prefix = config.get("corpus.s3.prefix", "corpus/")
    region = config.get("corpus.s3.region", "us-east-1")
    sync_to = config.get("corpus.s3.sync_to", ".corpus-cache/")

    if not bucket:
        raise ValueError("corpus.s3.bucket is required when corpus.source is 's3'")

    cache_dir = (config.project_root / sync_to).resolve()

    # Check if cache exists and is recent (skip sync if < 1 hour old and not forced)
    marker = cache_dir / ".last-sync"
    if not force_refresh and marker.exists():
        last_sync = datetime.fromisoformat(marker.read_text().strip())
        age_hours = (datetime.utcnow() - last_sync).total_seconds() / 3600
        if age_hours < 1.0:
            return cache_dir

    # Import boto3 (optional dependency)
    try:
        import boto3
    except ImportError:
        raise ImportError(
            "boto3 is required for S3 corpus loading.\n"
            "Install it: pip install boto3\n"
            "Or switch to local corpus: set corpus.source to 'local' in mda.config.yaml"
        )

    # Sync from S3
    cache_dir.mkdir(parents=True, exist_ok=True)

    s3 = boto3.client("s3", region_name=region)

    # Recreate subdirectory structure
    subdirs = ["procedures", "policies", "regulations", "rules",
                "data-dictionary", "systems", "training", "glossary"]
    for subdir in subdirs:
        (cache_dir / subdir).mkdir(parents=True, exist_ok=True)

    # List and download all .corpus.md files
    paginator = s3.get_paginator("list_objects_v2")
    downloaded = 0

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.endswith(".corpus.md"):
                continue

            # Derive local path from S3 key
            relative = key[len(prefix):] if key.startswith(prefix) else key
            local_path = cache_dir / relative
            local_path.parent.mkdir(parents=True, exist_ok=True)

            s3.download_file(bucket, key, str(local_path))
            downloaded += 1

    # Also download corpus.config.yaml if it exists
    try:
        config_key = prefix.rstrip("/") + "/corpus.config.yaml"
        s3.download_file(bucket, config_key, str(cache_dir / "corpus.config.yaml"))
    except Exception:
        pass  # Index may not exist in S3; will be regenerated

    # Write sync marker
    marker.write_text(datetime.utcnow().isoformat())

    return cache_dir


def get_corpus_info(config) -> dict:
    """Get information about the corpus configuration without loading it."""
    source = config.get("corpus.source", "local")
    info = {"source": source}

    if source == "s3":
        info["bucket"] = config.get("corpus.s3.bucket", "(not configured)")
        info["prefix"] = config.get("corpus.s3.prefix", "corpus/")
        info["region"] = config.get("corpus.s3.region", "us-east-1")
        info["cache"] = config.get("corpus.s3.sync_to", ".corpus-cache/")
    else:
        local_path = config.get("corpus.local_path") or config.get("paths.corpus") or "../../corpus"
        info["path"] = local_path
        if os.path.isabs(local_path):
            info["resolved"] = local_path
        else:
            info["resolved"] = str((config.project_root / local_path).resolve())

    return info
