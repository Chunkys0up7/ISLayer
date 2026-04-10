# MDA Intent Layer -- User Onboarding & Workflow Recreation Specification

*Recreation spec: an agent reading this document can rebuild every file described
from scratch and produce functionally identical output.*

---

## 1. Overview

This specification covers the user-facing onboarding layer of the MDA Intent Layer
CLI. It documents six artifacts:

| Artifact | Path | Purpose |
|----------|------|---------|
| User Guide | `docs/user-guide.md` | Step-by-step guide for non-technical document owners |
| Corpus Loader | `cli/pipeline/corpus_loader.py` | Load knowledge corpus from local filesystem or S3 |
| Submit Command | `cli/commands/submit_cmd.py` | Branch, commit, push, create PR in one command |
| Setup Skill | `.claude/skills/mda-setup/SKILL.md` | First-time environment setup for Claude Code |
| Submit Skill | `.claude/skills/mda-submit/SKILL.md` | Guided change submission for Claude Code |
| Config Defaults | `cli/config/defaults.py` | Default values including corpus and bitbucket blocks |

**Target users:** Non-technical business document owners using VS Code. They
understand Word and Excel but not programming. They may or may not have an AI
coding assistant (Claude Code, GitHub Copilot, Cursor).

**Agent-agnostic:** All functionality works from the command line. AI assistant
integration is optional and treats all assistants equally.

---

## 2. Configuration Extensions

### 2.1 Corpus Configuration Block

Added to `mda.config.yaml` and to `DEFAULTS` in `cli/config/defaults.py`:

```yaml
corpus:
  source: "local"
  local_path: "../../corpus"
  s3:
    bucket: ""
    prefix: "corpus/"
    region: "us-east-1"
    sync_to: ".corpus-cache/"
```

Field reference:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `corpus.source` | `str` | `"local"` | Corpus source: `"local"` or `"s3"` |
| `corpus.local_path` | `str` | `"../../corpus"` | Path to local corpus directory (absolute or relative to project root) |
| `corpus.s3.bucket` | `str` | `""` | S3 bucket name (required when source is `"s3"`) |
| `corpus.s3.prefix` | `str` | `"corpus/"` | S3 key prefix for corpus objects |
| `corpus.s3.region` | `str` | `"us-east-1"` | AWS region for the S3 bucket |
| `corpus.s3.sync_to` | `str` | `".corpus-cache/"` | Local directory for S3 cache (relative to project root) |

### 2.2 Bitbucket Configuration Block

Added to `mda.config.yaml` and to `DEFAULTS` in `cli/config/defaults.py`:

```yaml
bitbucket:
  url: ""
  project: ""
  repo: ""
  default_reviewers: []
```

Field reference:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `bitbucket.url` | `str` | `""` | Bitbucket Server base URL (e.g., `https://bitbucket.example.com`) |
| `bitbucket.project` | `str` | `""` | Bitbucket project key (e.g., `MYPROJ`) |
| `bitbucket.repo` | `str` | `""` | Bitbucket repository slug (e.g., `intent-specs`) |
| `bitbucket.default_reviewers` | `list[str]` | `[]` | List of usernames added as reviewers when `--reviewers` is not passed |

### 2.3 Environment Variables

| Variable | Used By | Purpose |
|----------|---------|---------|
| `BITBUCKET_TOKEN` | `submit_cmd.py` | Bearer token for Bitbucket Server REST API. Takes precedence over basic auth. |
| `BITBUCKET_USER` | `submit_cmd.py` | Username for Bitbucket basic auth. Used only when `BITBUCKET_TOKEN` is not set. |
| `BITBUCKET_PASSWORD` | `submit_cmd.py` | Password for Bitbucket basic auth. Used only when `BITBUCKET_TOKEN` is not set. |
| `ANTHROPIC_API_KEY` | `cli/llm/anthropic_provider.py` | API key for Anthropic Claude LLM provider |
| `OPENAI_API_KEY` | `cli/llm/openai_provider.py` | API key for OpenAI GPT LLM provider |
| `OLLAMA_BASE_URL` | `cli/llm/ollama_provider.py` | Base URL for local Ollama server (default: `http://localhost:11434`) |
| `MDA_LLM_PROVIDER` | `cli/config/loader.py` | Override `llm.provider` config at runtime (values: `anthropic`, `openai`, `ollama`) |
| `MDA_LLM_MODEL` | `cli/config/loader.py` | Override `llm.model` config at runtime (e.g., `claude-sonnet-4-20250514`, `gpt-4o`) |

### 2.4 Complete defaults.py

File: `cli/config/defaults.py`

```python
"""Default configuration values and path constants for the MDA Intent Layer CLI."""

from pathlib import Path

# Default config values used when no mda.config.yaml is found
DEFAULTS = {
    "mda": {"version": "1.0.0"},
    "paths": {
        "bpmn": "bpmn/",
        "triples": "triples/",
        "decisions": "decisions/",
        "graph": "graph/",
        "gaps": "gaps/",
        "audit": "audit/",
        "corpus": "../../corpus",
    },
    "llm": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "api_key_env": "ANTHROPIC_API_KEY",
        "temperature": 0.2,
        "max_tokens": 4096,
    },
    "pipeline": {
        "schemas": "../../schemas/",
        "ontology": "../../ontology/",
    },
    "corpus": {
        "source": "local",
        "local_path": "../../corpus",
        "s3": {
            "bucket": "",
            "prefix": "corpus/",
            "region": "us-east-1",
            "sync_to": ".corpus-cache/",
        },
    },
    "bitbucket": {
        "url": "",
        "project": "",
        "repo": "",
        "default_reviewers": [],
    },
    "defaults": {
        "status": "draft",
        "binding_status": "unbound",
        "audit_retention_years": 7,
    },
}

# Schema file names
SCHEMA_NAMES = {
    "capsule": "capsule.schema.json",
    "intent": "intent.schema.json",
    "contract": "contract.schema.json",
    "corpus_document": "corpus-document.schema.json",
    "triple_manifest": "triple-manifest.schema.json",
}

# Ontology file names
ONTOLOGY_NAMES = {
    "goal_types": "goal-types.yaml",
    "status_lifecycle": "status-lifecycle.yaml",
    "bpmn_element_mapping": "bpmn-element-mapping.yaml",
    "id_conventions": "id-conventions.yaml",
    "corpus_taxonomy": "corpus-taxonomy.yaml",
}
```

---

## 3. Corpus Loader

File: `cli/pipeline/corpus_loader.py`

### 3.1 Module-Level Setup

```python
"""Corpus loader -- loads knowledge corpus from local filesystem or S3."""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime
```

The module uses the dynamic import pattern shared by all pipeline modules:

```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
def _load_io(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mda_io", f"{name}.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
yaml_io = _load_io("yaml_io")
```

This loads `cli/mda_io/yaml_io.py` without relying on package imports (the CLI
uses `sys.path` manipulation, not installed packages).

### 3.2 Public API

#### `load_corpus(config, force_refresh: bool = False) -> Path`

Main entry point. Returns the local filesystem path to the corpus directory.

**Parameters:**
- `config` -- A `Config` object (from `cli/config/loader.py`) with `.get(dotted_key, default)` and `.project_root` attributes.
- `force_refresh` -- If `True`, bypass cache TTL and force S3 re-sync. Ignored for local mode.

**Returns:** `Path` to the local corpus directory.

**Behavior:**
1. Read `corpus.source` from config (default: `"local"`)
2. If `"s3"`: delegate to `_load_from_s3(config, force_refresh)`
3. Otherwise: delegate to `_load_from_local(config)`

#### `get_corpus_info(config) -> dict`

Returns a dictionary describing the corpus configuration without performing any
loading or syncing.

**Returns for local mode:**
```python
{
    "source": "local",
    "path": "../../corpus",       # raw config value
    "resolved": "/abs/path/to/corpus"  # resolved absolute path
}
```

**Returns for S3 mode:**
```python
{
    "source": "s3",
    "bucket": "my-bucket",
    "prefix": "corpus/",
    "region": "us-east-1",
    "cache": ".corpus-cache/"
}
```

### 3.3 Local Mode (`_load_from_local`)

**Signature:** `_load_from_local(config) -> Path`

**Config key resolution order:**
1. `corpus.local_path`
2. `paths.corpus` (fallback for backward compatibility)
3. `"../../corpus"` (hardcoded fallback)

**Path resolution:**
- If the value is an absolute path, use it directly
- If relative, resolve against `config.project_root`

**Error handling:**
- If the resolved directory does not exist, raise `FileNotFoundError` with the
  resolved path in the message: `f"Corpus directory not found: {corpus_dir}"`

### 3.4 S3 Mode (`_load_from_s3`)

**Signature:** `_load_from_s3(config, force_refresh: bool = False) -> Path`

**Config keys:**
- `corpus.s3.bucket` -- Required. Raise `ValueError` if empty:
  `"corpus.s3.bucket is required when corpus.source is 's3'"`
- `corpus.s3.prefix` -- Default `"corpus/"`
- `corpus.s3.region` -- Default `"us-east-1"`
- `corpus.s3.sync_to` -- Default `".corpus-cache/"`

**Cache directory:** Resolved as `(config.project_root / sync_to).resolve()`

**Cache TTL logic:**
1. Check for marker file at `cache_dir / ".last-sync"`
2. If marker exists and `force_refresh` is `False`:
   a. Parse the marker content as an ISO timestamp via `datetime.fromisoformat()`
   b. Calculate age in hours: `(datetime.utcnow() - last_sync).total_seconds() / 3600`
   c. If age < 1.0 hour, return `cache_dir` immediately (skip sync)
3. Otherwise, proceed with sync

**boto3 dependency:**
```python
try:
    import boto3
except ImportError:
    raise ImportError(
        "boto3 is required for S3 corpus loading.\n"
        "Install it: pip install boto3\n"
        "Or switch to local corpus: set corpus.source to 'local' in mda.config.yaml"
    )
```

**Sync procedure:**
1. Create `cache_dir` with `mkdir(parents=True, exist_ok=True)`
2. Create a boto3 S3 client: `boto3.client("s3", region_name=region)`
3. Create subdirectories (8 total):
   ```python
   subdirs = ["procedures", "policies", "regulations", "rules",
               "data-dictionary", "systems", "training", "glossary"]
   ```
   Each created with `(cache_dir / subdir).mkdir(parents=True, exist_ok=True)`
4. Use paginated `list_objects_v2`:
   ```python
   paginator = s3.get_paginator("list_objects_v2")
   for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
       for obj in page.get("Contents", []):
           key = obj["Key"]
           if not key.endswith(".corpus.md"):
               continue
           relative = key[len(prefix):] if key.startswith(prefix) else key
           local_path = cache_dir / relative
           local_path.parent.mkdir(parents=True, exist_ok=True)
           s3.download_file(bucket, key, str(local_path))
   ```
5. Attempt to download `corpus.config.yaml`:
   ```python
   try:
       config_key = prefix.rstrip("/") + "/corpus.config.yaml"
       s3.download_file(bucket, config_key, str(cache_dir / "corpus.config.yaml"))
   except Exception:
       pass  # Index may not exist in S3; will be regenerated
   ```
6. Write sync marker: `marker.write_text(datetime.utcnow().isoformat())`
7. Return `cache_dir`

**Error handling:**
- Missing bucket config: `ValueError`
- Missing boto3: `ImportError` with install instructions
- S3 API errors: propagate unhandled (boto3 `ClientError` etc.)

---

## 4. Submit Command

File: `cli/commands/submit_cmd.py`

### 4.1 CLI Registration

Registered in `cli/mda.py` via argparse:

```python
submit_parser = subparsers.add_parser("submit", help="Submit changes for review (branch, commit, push, PR)")
submit_parser.add_argument("--message", "-m", help="Commit message describing the changes")
submit_parser.add_argument("--reviewers", help="Comma-separated list of reviewers")
submit_parser.add_argument("--target", default="main", help="Target branch for PR (default: main)")
```

The global `--dry-run` flag is inherited from the parent parser.

CLI invocation:
```
python cli/mda.py submit --message "description" [--reviewers user1,user2] [--target main] [--dry-run]
```

### 4.2 Entry Point

**Signature:** `run_submit(args, config)`

**Parameters read from `args`:**
- `args.message` -- Commit message string (required)
- `args.reviewers` -- Comma-separated reviewer usernames (optional)
- `args.target` -- Target branch for PR (default: `"main"`)
- `args.dry_run` -- Boolean, show plan without executing

**Imports (inside function body):**
```python
from output.console import console, print_header, print_success, print_error, print_warning, print_info
```

### 4.3 Workflow Steps

#### Step 1: Check for changes

```python
status = _git("status", "--porcelain", cwd=project_root)
if not status.strip():
    print_warning("No changes to submit. Working tree is clean.")
    return
```

#### Step 2: Display changed files

Parse each line of porcelain output. Show up to 20 files with color coding:

| Status Code | Color | Meaning |
|-------------|-------|---------|
| `M` | `yellow` | Modified |
| `A` | `green` | Added |
| `D` | `red` | Deleted |
| `??` | `dim` | Untracked |

Format: `console.print(f"  [{color}]{status_code}[/{color}] {filepath}")`

If more than 20 files, print: `"  ... and {n} more"`

#### Step 3: Require commit message

If `message` is `None` or empty:
```python
print_error("Please provide a commit message with --message")
print_info('Example: python cli/mda.py submit --message "Updated income verification procedures"')
sys.exit(1)
```

#### Step 4: Generate branch name

```python
process_name = config.get("process.name", project_root.name).lower().replace(" ", "-")
date_str = datetime.now().strftime("%Y%m%d")
slug = re.sub(r'[^a-z0-9-]', '', message.lower().replace(" ", "-"))[:30]
branch_name = f"feature/{process_name}/{date_str}-{slug}"
```

Pattern: `feature/{process-name}/{YYYYMMDD}-{slug}`

The slug is the message lowercased, spaces replaced with hyphens, non-alphanumeric
characters (except hyphens) stripped, truncated to 30 characters.

#### Step 5: Dry-run check

If `dry_run` is `True`, print the planned actions and return without executing:
```
Dry run -- would perform:
  1. Create branch: feature/income-verification/20260410-updated-procedures
  2. Stage 5 files
  3. Commit: Updated procedures
  4. Push to origin/feature/income-verification/20260410-updated-procedures
  5. Create PR on Bitbucket -> main   (or "Print PR URL for manual creation")
```

#### Step 6: Create branch

Only create a new branch if the current branch is `main`, `master`, or `develop`:
```python
current_branch = _git("branch", "--show-current", cwd=project_root).strip()
if current_branch in ("main", "master", "develop"):
    _git("checkout", "-b", branch_name, cwd=project_root)
else:
    branch_name = current_branch  # reuse the current feature branch
```

#### Step 7: Stage all changes

```python
_git("add", "-A", cwd=project_root)
```

Note: The code defines a `safe_paths` list but does not use it -- it stages
everything with `-A`. This is intentional; `.gitignore` handles exclusions.

#### Step 8: Commit

```python
_git("commit", "-m", message, cwd=project_root)
print_success("Changes committed")
```

#### Step 9: Push

```python
_git("push", "-u", "origin", branch_name, cwd=project_root)
print_success(f"Pushed to origin/{branch_name}")
```

On `RuntimeError`:
```python
print_error(f"Push failed: {e}")
print_info("You may need to configure git remote: git remote add origin <url>")
sys.exit(1)
```

#### Step 10: Create PR or print URL

Check `bitbucket.url`, `bitbucket.project`, `bitbucket.repo` in config:

- **If all three are set:** Call `_create_bitbucket_pr()`
- **Otherwise:** Print manual PR instructions (fallback)

### 4.4 Bitbucket PR Creation (`_create_bitbucket_pr`)

**Signature:**
```python
def _create_bitbucket_pr(bb_url, bb_project, bb_repo, source_branch, target_branch, title, reviewers_str, config)
```

**Additional import (inside function body):** `import requests`

**API endpoint:**
```
POST {bb_url}/rest/api/1.0/projects/{bb_project}/repos/{bb_repo}/pull-requests
```

**Reviewer list construction:**
```python
reviewer_list = []
if reviewers_str:
    for r in reviewers_str.split(","):
        reviewer_list.append({"user": {"name": r.strip()}})
else:
    defaults = config.get("bitbucket.default_reviewers", [])
    for r in defaults:
        reviewer_list.append({"user": {"name": r}})
```

**Request payload:**
```python
{
    "title": title,
    "description": f"Submitted via MDA Intent Layer CLI\n\nBranch: {source_branch}",
    "fromRef": {
        "id": f"refs/heads/{source_branch}",
        "repository": {"slug": bb_repo, "project": {"key": bb_project}},
    },
    "toRef": {
        "id": f"refs/heads/{target_branch}",
        "repository": {"slug": bb_repo, "project": {"key": bb_project}},
    },
    "reviewers": reviewer_list,
}
```

**Authentication (in priority order):**
1. `BITBUCKET_TOKEN` env var: `headers["Authorization"] = f"Bearer {token}"`
2. `BITBUCKET_USER` + `BITBUCKET_PASSWORD` env vars: `auth = (bb_user, bb_pass)` (basic auth via requests)
3. Neither: print info message with manual PR URL and return

**Request:** `requests.post(api_url, json=payload, headers=headers, auth=auth, timeout=30)`

**Response handling:**
- Status 200 or 201: extract `pr_data["id"]` and `pr_data["links"]["self"][0]["href"]`, print success
- Other status: `print_error(f"Bitbucket API error ({resp.status_code}): {resp.text[:200]}")`
- `requests.RequestException`: print error and fallback manual PR URL

### 4.5 GitHub/Manual Fallback

When Bitbucket config is not set, get the remote URL and construct a manual link:

```python
remote_url = _git("remote", "get-url", "origin", cwd=project_root).strip()
if "bitbucket" in remote_url.lower():
    pr_url = f"{remote_url.rstrip('.git')}/pull-requests?create&source={branch_name}&dest={target}"
elif "github" in remote_url.lower():
    pr_url = f"{remote_url.rstrip('.git')}/compare/{target}...{branch_name}"
else:
    # Print remote URL and branch info
    console.print(f"  Push URL: {remote_url}")
    console.print(f"  Branch: {branch_name} -> {target}")
```

If `reviewers` is set, also print: `"  Reviewers: {reviewers}"`

### 4.6 Helper: `_git()`

```python
def _git(*args, cwd=None) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git"] + list(args),
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and "error" in result.stderr.lower():
        raise RuntimeError(result.stderr.strip())
    return result.stdout
```

**Key behavior:** Only raises `RuntimeError` if BOTH `returncode != 0` AND the
word `"error"` appears in stderr (case-insensitive). This allows git warnings
(which go to stderr but return 0) to pass through silently.

### 4.7 Module Imports

```python
import subprocess
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

---

## 5. Skills

### 5.1 Setup Skill

File: `.claude/skills/mda-setup/SKILL.md`

This is the complete, verbatim content of the file:

````markdown
---
name: mda-setup
description: First-time setup for the MDA Intent Layer. Checks prerequisites, installs dependencies, and configures your environment. Use when setting up a new workstation or onboarding a new team member.
allowed-tools: Bash(python *) Bash(pip *) Bash(git *) Bash(where *) Bash(which *)
disable-model-invocation: true
---

# MDA Intent Layer -- First-Time Setup

This guide checks your environment and gets everything ready to work with the MDA Intent Layer.

## Environment Check

Python: !`python --version 2>&1 || python3 --version 2>&1 || echo "NOT INSTALLED"`
Git: !`git --version 2>&1 || echo "NOT INSTALLED"`
Current directory: !`pwd`
Requirements installed: !`python -c "import yaml, jsonschema, rich; print('YES')" 2>&1 || echo "NO — need to install"`

## Steps

### 1. Check Prerequisites

Verify Python 3.10+ and Git are installed. If not, guide the user:
- **Python**: Download from https://www.python.org/downloads/ -- check "Add to PATH" during install
- **Git**: Download from https://git-scm.com/downloads

### 2. Install Dependencies

```
pip install -r requirements.txt
```

If that fails, try:
```
python -m pip install -r requirements.txt
```

### 3. Verify Installation

```
python cli/mda.py --help
```

This should show all available commands. If it does, the installation is working.

### 4. Configure LLM (Optional)

If the user will be generating triples with LLM assistance, help them set an API key:

- **Anthropic Claude**: `set ANTHROPIC_API_KEY=sk-ant-...` (Windows) or `export ANTHROPIC_API_KEY=sk-ant-...` (Mac/Linux)
- **OpenAI**: `set OPENAI_API_KEY=sk-...`
- **Local Ollama**: No key needed -- install Ollama from https://ollama.ai

LLM is optional -- all commands work without it. `--skip-llm` mode produces template stubs.

### 5. Test With Demo Data

```
cd examples/income-verification
python ../../cli/mda.py test --quick
python ../../cli/mda.py status
python ../../cli/mda.py report --format yaml
```

If all pass, the user is ready to work.

### 6. Next Steps

Suggest the user read the User Guide: docs/user-guide.md
````

**Frontmatter fields explained:**
- `name: mda-setup` -- Skill name, invoked as `/mda-setup`
- `description` -- Shown in skill listings; helps Claude decide when to invoke
- `allowed-tools` -- Restricts the skill to only these Bash patterns: `python *`, `pip *`, `git *`, `where *` (Windows), `which *` (Unix)
- `disable-model-invocation: true` -- Prevents the skill from calling external LLM APIs

**Dynamic context (the `!` backtick syntax):**
Each `!` backtick block executes at skill load time and injects the result inline.
This gives Claude real-time environment information before it starts the steps.

### 5.2 Submit Skill

File: `.claude/skills/mda-submit/SKILL.md`

This is the complete, verbatim content of the file:

````markdown
---
name: mda-submit
description: Submit your changes for review. Creates a feature branch, commits your work, pushes to the remote, and opens a pull request. Use when you're ready to share your changes with reviewers.
argument-hint: [commit message]
allowed-tools: Bash(python *) Bash(git *)
disable-model-invocation: true
---

# Submit Changes for Review

This command packages your changes and submits them for review through your team's Git workflow.

## What's Changed

!`git status --short 2>/dev/null | head -20 || echo "Not in a git repository"`

## Current Branch

!`git branch --show-current 2>/dev/null || echo "unknown"`

## Steps

1. If the user hasn't provided a commit message via `$ARGUMENTS`, ask them to describe what they changed in plain language (e.g., "Updated the income verification procedure to include gig economy workers").

2. Run the submit command:

```
python cli/mda.py submit --message "$ARGUMENTS"
```

3. If using `--dry-run`, show what would happen without making changes:

```
python cli/mda.py submit --message "$ARGUMENTS" --dry-run
```

4. The command will:
   - Create a feature branch from your current branch
   - Stage all your changes (triples, corpus docs, BPMN files)
   - Commit with your message
   - Push to the remote repository
   - Create a pull request (if Bitbucket is configured) or show the URL

5. After submission, remind the user:
   - Their changes are now in a pull request awaiting review
   - Reviewers will check the triples for accuracy
   - They can continue working -- new changes go into a new submission

## If Something Goes Wrong

- **"No changes to submit"** -- You haven't modified any files since your last commit
- **"Push failed"** -- Check your Git remote is configured: `git remote -v`
- **"No Bitbucket credentials"** -- Ask your admin to set BITBUCKET_TOKEN in your environment
````

**Frontmatter fields explained:**
- `name: mda-submit` -- Invoked as `/mda-submit`
- `argument-hint: [commit message]` -- Tells Claude that `$ARGUMENTS` should be a commit message; shown in autocomplete
- `allowed-tools` -- Only `python *` and `git *` Bash commands
- `disable-model-invocation: true` -- No external LLM calls

**Dynamic context:**
- `git status --short` -- Shows the user's current changes (up to 20 lines)
- `git branch --show-current` -- Shows which branch they are on

**`$ARGUMENTS` variable:** When the user types `/mda-submit Updated DTI rules`,
Claude Code sets `$ARGUMENTS` to `"Updated DTI rules"`. The skill uses this as
the commit message. If empty, the skill asks the user interactively.

---

## 6. User Guide

File: `docs/user-guide.md`

### 6.1 Document Structure

The user guide is a single Markdown file, approximately 835 lines, organized into
these sections:

| # | Section | Approx Lines | Content |
|---|---------|-------------|---------|
| 1 | What Is This? | 1-30 | Plain-language explanation of the MDA Intent Layer for non-technical users. Establishes that the user is a business process owner editing plain-English documents. |
| 2 | What You Will Need | 31-105 | Software installation instructions: VS Code, Python (with PATH warning), Git. Each with download URL, install steps, verification command. Optional AI assistant mention. |
| 3 | Get the Project | 106-160 | Clone repo, `cd`, `pip install`, open folder in VS Code, verify with `test --quick`. |
| 4 | Your Workspace | 161-243 | Folder orientation table (`examples/`, `corpus/`, `cli/`, `schemas/`, etc.). Capsule file anatomy with full example showing front matter and content sections. |
| 5 | Working with Your Process | 244-305 | Navigate to process folder, `status`, `graph --format mermaid`, `report --format yaml`. Grade explanation table (A through F). |
| 6 | Ingesting a New BPMN | 306-360 | Two paths: `--skip-llm` (manual templates) and with-LLM (API key setup + `ingest`). Explains what LLM means. |
| 7 | Working with the Corpus | 360-440 | Corpus concept, category table (8 types), `corpus search`, `corpus add`, `corpus index`. S3 config example. |
| 8 | Editing Documents | 441-498 | What to edit (Purpose, Procedure, Business Rules, etc.), what NOT to edit (front matter IDs), saving (Ctrl+S). |
| 9 | Checking Your Work | 499-553 | `test --quick`, `test` (full), `report`, `gaps --severity high`. |
| 10 | Submitting Changes | 554-590 | `submit --message "..."` walkthrough. Four-step explanation (branch, commit, push, PR). What happens after submission. |
| 11 | Browsing as Website | 591-610 | `docs serve`, open localhost:8000, Ctrl+C to stop. |
| 12 | Daily Workflow Cheat Sheet | 611-640 | Table of 10 commands (see below). Note about submit running from project root. |
| 13 | A Typical Day | 641-670 | Narrative 10-step walkthrough of a normal workday. |
| 14 | Using an AI Assistant | 671-705 | Agent-agnostic instructions. Claude Code slash commands mentioned. Important note that AI is optional. |
| 15 | Troubleshooting | 706-790 | 9 common errors with fixes (see below). |
| 16 | Glossary | 791-815 | 16 terms defined in plain language (see below). |
| 17 | Getting Help | 816-835 | 6 help options: this guide, CLI reference, process owner guide, team lead, admin, AI assistant. |

### 6.2 Key Design Principles

1. **Written for Word/Excel users** -- No assumed knowledge of terminals, Git, or programming
2. **Every command explained** -- Each CLI invocation is preceded by a plain-language explanation of what it does
3. **No jargon without definition** -- Terms like "commit", "branch", "CLI", "Markdown" are explained at first use and collected in the glossary
4. **"You" language** -- Second person throughout ("You will see...", "Your job is to...")
5. **Agent-agnostic** -- Claude Code, GitHub Copilot, and Cursor mentioned equally as optional tools; no favoritism
6. **PATH warning emphasized** -- The Python installer PATH checkbox is called out with bold text and a "Why this matters" explainer
7. **Visual cues explained** -- Keyboard shortcuts include the key location ("the backtick key, located above the Tab key on most keyboards")

### 6.3 Cheat Sheet Commands

| What You Want to Do | Command |
|---------------------|---------|
| See all tasks in my process | `python ../../cli/mda.py status` |
| Quick-check my work | `python ../../cli/mda.py test --quick` |
| Full check | `python ../../cli/mda.py test` |
| See health scores | `python ../../cli/mda.py report --format yaml` |
| Find a corpus document | `python ../../cli/mda.py corpus search "keyword"` |
| Add a new procedure | `python ../../cli/mda.py corpus add procedure --title "My Procedure"` |
| View missing information | `python ../../cli/mda.py gaps` |
| View only critical gaps | `python ../../cli/mda.py gaps --severity critical` |
| See the process flow | `python ../../cli/mda.py graph --format mermaid` |
| Browse as a website | `python ../../cli/mda.py docs serve` |
| Rebuild corpus index | `python ../../cli/mda.py corpus index` |
| Submit for review | `python cli/mda.py submit -m "My changes"` (from project root) |

Note: Submit uses `cli/mda.py` (from project root) while all other commands use
`../../cli/mda.py` (from inside a process folder like `examples/income-verification/`).

### 6.4 Troubleshooting Section

9 error scenarios covered:

1. **"python is not recognized"** -- PATH not set; reinstall with checkbox
2. **"No module named 'yaml'" / ModuleNotFoundError** -- Run `pip install -r requirements.txt`
3. **"No changes to submit"** -- Files not saved or already committed
4. **"Push failed" / "remote: Repository not found"** -- Git remote not configured
5. **"Corpus directory not found"** -- Check `paths.corpus` in `mda.config.yaml`
6. **"fatal: not a git repository"** -- Not inside the project folder
7. **Command takes a long time / frozen** -- Ctrl+C, re-run with `--skip-llm`
8. **"Permission denied"** -- Ask IT for write permissions
9. **VS Code does not show files** -- File > Open Folder to the correct project

### 6.5 Glossary Terms

16 terms defined: BPMN, Capsule, CLI, Commit, Corpus, Front matter, Gap, Git,
Intent, LLM, Markdown, MDA, Pull request, Repository, Terminal, Triple.

---

## 7. .gitignore Additions

The following entry must be present in the project root `.gitignore`:

```
# S3 corpus cache
.corpus-cache/
```

This prevents the S3 sync cache from being committed to the repository.

---

## 8. Requirements Addition

The following entry must be present in `requirements.txt`:

```
# S3 corpus loading (optional):
boto3>=1.34
```

Also required for Bitbucket PR creation (already present for Ollama):
```
requests>=2.31
```

---

## 9. Integration Points

### 9.1 CLI Registration (cli/mda.py)

The submit command is registered in `build_parser()` and dispatched in `main()`:

```python
elif args.command == "submit":
    from commands.submit_cmd import run_submit
    run_submit(args, config)
```

The corpus loader is NOT directly registered as a CLI command. It is called by
other commands (corpus search, corpus add, corpus index, ingest, enrich) via:

```python
from pipeline.corpus_loader import load_corpus
corpus_path = load_corpus(config)
```

### 9.2 Config Loader (cli/config/loader.py)

The `Config` class provides:
- `config.get("corpus.source")` -- Dotted-key access to nested config
- `config.project_root` -- `Path` to the directory containing `mda.config.yaml`
- `config.resolve_path("paths.corpus")` -- Resolve relative path against project root
- `config.llm_provider` -- Property that checks `MDA_LLM_PROVIDER` env var first
- `config.llm_model` -- Property that checks `MDA_LLM_MODEL` env var first

Config loading priority:
1. `DEFAULTS` dict from `cli/config/defaults.py` (deep-copied)
2. `mda.config.yaml` values deep-merged on top
3. Environment variable overrides (for LLM provider/model only, checked at access time)

### 9.3 Output Helpers (cli/output/console.py)

The submit command uses Rich console helpers:
- `console` -- `rich.console.Console()` instance
- `print_header(text)` -- Bold header with separator
- `print_success(text)` -- Green checkmark prefix
- `print_error(text)` -- Red X prefix
- `print_warning(text)` -- Yellow warning prefix
- `print_info(text)` -- Blue info prefix

---

## 10. Verification Checklist

These checks confirm a correct recreation:

1. **Dry-run submit:**
   ```
   python cli/mda.py submit --dry-run -m "test"
   ```
   Expected: Prints 5 planned actions without executing any git commands.

2. **Live submit (on a test repo with changes):**
   ```
   python cli/mda.py submit -m "test submission"
   ```
   Expected: Creates branch `feature/{name}/{date}-test-submission`, commits, pushes, prints PR URL.

3. **Local corpus load:**
   ```python
   from cli.config.loader import load_config
   from cli.pipeline.corpus_loader import load_corpus
   config = load_config()
   path = load_corpus(config)
   assert path.exists()
   ```

4. **S3 corpus load (requires boto3 + AWS credentials):**
   Set `corpus.source: "s3"` and `corpus.s3.bucket: "my-bucket"` in config.
   ```python
   path = load_corpus(config)
   assert (path / ".last-sync").exists()
   ```

5. **S3 missing boto3:**
   With `corpus.source: "s3"` and boto3 not installed:
   ```python
   load_corpus(config)  # raises ImportError with install instructions
   ```

6. **Corpus info:**
   ```python
   info = get_corpus_info(config)
   assert info["source"] in ("local", "s3")
   ```

7. **Setup skill:** `/mda-setup` in Claude Code checks Python version, Git version,
   current directory, and requirements status before walking through 6 steps.

8. **Submit skill:** `/mda-submit Updated DTI rules` in Claude Code runs
   `python cli/mda.py submit --message "Updated DTI rules"`.

9. **User guide renders:** `docs/user-guide.md` renders correctly in VS Code
   Markdown preview and in MkDocs (`python ../../cli/mda.py docs serve`).

10. **Existing tests pass:** All 537 existing tests continue to pass:
    ```
    cd examples/income-verification
    python ../../cli/mda.py test
    ```

---

## 11. File Listing

Complete list of files covered by this specification:

```
cli/config/defaults.py          -- DEFAULTS dict with corpus + bitbucket blocks
cli/pipeline/corpus_loader.py   -- load_corpus(), get_corpus_info()
cli/commands/submit_cmd.py      -- run_submit(), _create_bitbucket_pr(), _git()
cli/mda.py                      -- submit subparser registration + dispatch
.claude/skills/mda-setup/SKILL.md   -- First-time setup skill
.claude/skills/mda-submit/SKILL.md  -- Submit workflow skill
docs/user-guide.md              -- Non-technical user guide (~835 lines)
.gitignore                      -- .corpus-cache/ entry
requirements.txt                -- boto3>=1.34 entry
```

---

*End of specification.*
