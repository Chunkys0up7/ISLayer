"""Integration tests: MkDocs documentation generator.

Copies a demo process to a temp directory, runs the docs generator,
and verifies output structure.
"""

import shutil
import sys
from pathlib import Path

import pytest
import yaml

_TESTS_DIR = Path(__file__).resolve().parent.parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from conftest import PROJECT_ROOT, CLI_DIR, EXAMPLES_DIR  # noqa: E402


def _copy_process_to_tmp(tmp_path: Path, process_name: str = "income-verification") -> Path:
    """Copy a demo process directory to tmp_path for isolated testing."""
    src = EXAMPLES_DIR / process_name
    dest = tmp_path / process_name
    shutil.copytree(str(src), str(dest))
    return dest


def _load_config(project_root: Path):
    """Load Config from mda.config.yaml in the given project root."""
    # CLI_DIR is already on sys.path via conftest, so config package is importable
    from config.loader import load_config

    config_path = project_root / "mda.config.yaml"
    if config_path.exists():
        return load_config(config_path)
    return load_config()


def _load_docs_generator():
    """Load the docs_generator module."""
    import importlib.util
    file_path = CLI_DIR / "pipeline" / "docs_generator.py"
    spec = importlib.util.spec_from_file_location(
        "pipeline.docs_generator", str(file_path)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestDocsGenerator:
    """Verify MkDocs documentation generation."""

    def test_generate_creates_output(self, tmp_path):
        """Generating docs should create mkdocs.yml in the project root."""
        project_dir = _copy_process_to_tmp(tmp_path)
        docs_gen = _load_docs_generator()
        config = _load_config(project_dir)
        mkdocs_path = docs_gen.generate_docs(
            project_root=project_dir,
            config=config,
            engine_root=PROJECT_ROOT,
        )
        assert mkdocs_path.exists(), f"mkdocs.yml not created at {mkdocs_path}"

    def test_generated_has_index(self, tmp_path):
        """Generated docs should include docs/index.md."""
        project_dir = _copy_process_to_tmp(tmp_path)
        docs_gen = _load_docs_generator()
        config = _load_config(project_dir)
        docs_gen.generate_docs(
            project_root=project_dir,
            config=config,
            engine_root=PROJECT_ROOT,
        )
        index_path = project_dir / "docs" / "index.md"
        assert index_path.exists(), f"docs/index.md not created at {index_path}"

    def test_mkdocs_yml_valid(self, tmp_path):
        """mkdocs.yml should be valid YAML with a site_name key."""
        project_dir = _copy_process_to_tmp(tmp_path)
        docs_gen = _load_docs_generator()
        config = _load_config(project_dir)
        mkdocs_path = docs_gen.generate_docs(
            project_root=project_dir,
            config=config,
            engine_root=PROJECT_ROOT,
        )
        content = mkdocs_path.read_text(encoding="utf-8")

        # mkdocs.yml may contain Python-specific YAML tags
        # (e.g., !!python/name:pymdownx.superfences.fence_code_format)
        # that require the module to be installed. Use a custom loader
        # that resolves unknown Python tags to a placeholder string.
        class _PermissiveLoader(yaml.SafeLoader):
            pass

        def _python_tag_constructor(loader, tag_suffix, node):
            return f"<python:{tag_suffix}>"

        _PermissiveLoader.add_multi_constructor(
            "tag:yaml.org,2002:python/",
            _python_tag_constructor,
        )

        mkdocs_data = yaml.load(content, Loader=_PermissiveLoader)
        assert isinstance(mkdocs_data, dict), "mkdocs.yml did not parse as a dict"
        assert "site_name" in mkdocs_data, "mkdocs.yml missing 'site_name' key"
