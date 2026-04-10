"""mda submit — Submit changes for review (branch, commit, push, PR)."""

import subprocess
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_submit(args, config):
    """Submit changes: create branch, commit, push, and optionally open PR."""
    from output.console import console, print_header, print_success, print_error, print_warning, print_info

    project_root = config.project_root
    message = getattr(args, 'message', None)
    reviewers = getattr(args, 'reviewers', None)
    target = getattr(args, 'target', 'main') or 'main'
    dry_run = getattr(args, 'dry_run', False)

    print_header("Submit Changes for Review")

    # Step 1: Check for changes
    status = _git("status", "--porcelain", cwd=project_root)
    if not status.strip():
        print_warning("No changes to submit. Working tree is clean.")
        return

    # Show what's changed
    changed_files = [line.strip() for line in status.strip().split("\n") if line.strip()]
    console.print(f"\n[bold]Changes to submit ({len(changed_files)} files):[/bold]")
    for f in changed_files[:20]:
        status_code = f[:2].strip()
        filepath = f[3:]
        color = {"M": "yellow", "A": "green", "D": "red", "??": "dim"}.get(status_code, "white")
        console.print(f"  [{color}]{status_code}[/{color}] {filepath}")
    if len(changed_files) > 20:
        console.print(f"  ... and {len(changed_files) - 20} more")

    # Step 2: Get commit message
    if not message:
        print_error("Please provide a commit message with --message")
        print_info('Example: python cli/mda.py submit --message "Updated income verification procedures"')
        sys.exit(1)

    # Step 3: Determine branch name
    process_name = config.get("process.name", project_root.name).lower().replace(" ", "-")
    date_str = datetime.now().strftime("%Y%m%d")
    slug = re.sub(r'[^a-z0-9-]', '', message.lower().replace(" ", "-"))[:30]
    branch_name = f"feature/{process_name}/{date_str}-{slug}"

    current_branch = _git("branch", "--show-current", cwd=project_root).strip()

    if dry_run:
        console.print(f"\n[bold]Dry run — would perform:[/bold]")
        console.print(f"  1. Create branch: {branch_name}")
        console.print(f"  2. Stage {len(changed_files)} files")
        console.print(f"  3. Commit: {message}")
        console.print(f"  4. Push to origin/{branch_name}")
        bb = config.get("bitbucket.url")
        if bb:
            console.print(f"  5. Create PR on Bitbucket → {target}")
        else:
            console.print(f"  5. Print PR URL for manual creation")
        return

    # Step 4: Create branch (if not already on a feature branch)
    if current_branch in ("main", "master", "develop"):
        console.print(f"\n[dim]Creating branch: {branch_name}[/dim]")
        _git("checkout", "-b", branch_name, cwd=project_root)
    else:
        branch_name = current_branch
        console.print(f"\n[dim]Using current branch: {branch_name}[/dim]")

    # Step 5: Stage changes
    # Stage specific directories (safe — don't stage secrets or cache)
    safe_paths = ["triples/", "decisions/", "gaps/", "corpus-local/", "bpmn/",
                  "graph/", "audit/", "*.cap.md", "*.intent.md", "*.contract.md",
                  "*.corpus.md", "mda.config.yaml", "README.md"]
    _git("add", "-A", cwd=project_root)

    # Step 6: Commit
    console.print(f"[dim]Committing: {message}[/dim]")
    _git("commit", "-m", message, cwd=project_root)
    print_success("Changes committed")

    # Step 7: Push
    console.print(f"[dim]Pushing to origin/{branch_name}...[/dim]")
    try:
        _git("push", "-u", "origin", branch_name, cwd=project_root)
        print_success(f"Pushed to origin/{branch_name}")
    except RuntimeError as e:
        print_error(f"Push failed: {e}")
        print_info("You may need to configure git remote: git remote add origin <url>")
        sys.exit(1)

    # Step 8: Create PR (Bitbucket API or fallback)
    bb_url = config.get("bitbucket.url")
    bb_project = config.get("bitbucket.project")
    bb_repo = config.get("bitbucket.repo")

    if bb_url and bb_project and bb_repo:
        _create_bitbucket_pr(bb_url, bb_project, bb_repo, branch_name, target, message, reviewers, config)
    else:
        # Fallback: print manual PR instructions
        console.print("\n[bold]Next step: Create a Pull Request[/bold]")
        remote_url = _git("remote", "get-url", "origin", cwd=project_root).strip()
        if "bitbucket" in remote_url.lower():
            # Construct Bitbucket PR URL
            pr_url = f"{remote_url.rstrip('.git')}/pull-requests?create&source={branch_name}&dest={target}"
            console.print(f"  Open: {pr_url}")
        elif "github" in remote_url.lower():
            pr_url = f"{remote_url.rstrip('.git')}/compare/{target}...{branch_name}"
            console.print(f"  Open: {pr_url}")
        else:
            console.print(f"  Push URL: {remote_url}")
            console.print(f"  Branch: {branch_name} → {target}")

        if reviewers:
            console.print(f"  Reviewers: {reviewers}")


def _create_bitbucket_pr(bb_url, bb_project, bb_repo, source_branch, target_branch, title, reviewers_str, config):
    """Create a PR via Bitbucket Server REST API."""
    import requests
    from output.console import print_success, print_error, print_info

    api_url = f"{bb_url.rstrip('/')}/rest/api/1.0/projects/{bb_project}/repos/{bb_repo}/pull-requests"

    # Build reviewer list
    reviewer_list = []
    if reviewers_str:
        for r in reviewers_str.split(","):
            reviewer_list.append({"user": {"name": r.strip()}})
    else:
        # Use default reviewers from config
        defaults = config.get("bitbucket.default_reviewers", [])
        for r in defaults:
            reviewer_list.append({"user": {"name": r}})

    payload = {
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

    # Auth: try token from env, then basic auth
    token = os.environ.get("BITBUCKET_TOKEN")
    auth = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        bb_user = os.environ.get("BITBUCKET_USER")
        bb_pass = os.environ.get("BITBUCKET_PASSWORD")
        if bb_user and bb_pass:
            auth = (bb_user, bb_pass)
        else:
            print_info("No Bitbucket credentials found. Set BITBUCKET_TOKEN or BITBUCKET_USER/BITBUCKET_PASSWORD.")
            print_info(f"Manual PR URL: {bb_url}/projects/{bb_project}/repos/{bb_repo}/pull-requests?create")
            return

    try:
        resp = requests.post(api_url, json=payload, headers=headers, auth=auth, timeout=30)
        if resp.status_code in (200, 201):
            pr_data = resp.json()
            pr_url = pr_data.get("links", {}).get("self", [{}])[0].get("href", "")
            pr_id = pr_data.get("id", "")
            print_success(f"Pull Request #{pr_id} created: {pr_url}")
        else:
            print_error(f"Bitbucket API error ({resp.status_code}): {resp.text[:200]}")
    except requests.RequestException as e:
        print_error(f"Failed to create PR: {e}")
        print_info(f"Manual PR URL: {bb_url}/projects/{bb_project}/repos/{bb_repo}/pull-requests?create")


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
