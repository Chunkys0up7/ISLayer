---
name: mda-setup
description: First-time setup for the MDA Intent Layer. Checks prerequisites, installs dependencies, and configures your environment. Use when setting up a new workstation or onboarding a new team member.
allowed-tools: Bash(python *) Bash(pip *) Bash(git *) Bash(where *) Bash(which *)
disable-model-invocation: true
---

# MDA Intent Layer — First-Time Setup

This guide checks your environment and gets everything ready to work with the MDA Intent Layer.

## Environment Check

Python: !`python --version 2>&1 || python3 --version 2>&1 || echo "NOT INSTALLED"`
Git: !`git --version 2>&1 || echo "NOT INSTALLED"`
Current directory: !`pwd`
Requirements installed: !`python -c "import yaml, jsonschema, rich; print('YES')" 2>&1 || echo "NO — need to install"`

## Steps

### 1. Check Prerequisites

Verify Python 3.10+ and Git are installed. If not, guide the user:
- **Python**: Download from https://www.python.org/downloads/ — check "Add to PATH" during install
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
- **Local Ollama**: No key needed — install Ollama from https://ollama.ai

LLM is optional — all commands work without it. `--skip-llm` mode produces template stubs.

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
