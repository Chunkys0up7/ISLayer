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
   - They can continue working — new changes go into a new submission

## If Something Goes Wrong

- **"No changes to submit"** — You haven't modified any files since your last commit
- **"Push failed"** — Check your Git remote is configured: `git remote -v`
- **"No Bitbucket credentials"** — Ask your admin to set BITBUCKET_TOKEN in your environment
