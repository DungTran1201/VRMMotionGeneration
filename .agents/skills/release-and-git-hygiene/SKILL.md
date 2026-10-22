---
name: release-and-git-hygiene
description: Enforce clean Git operations, branch isolation, and release verification
---

# Release and Git Hygiene Skill

## 1. Purpose & When to Use
Use before creating commits, opening pull requests, and pushing branches to remote repositories.

## 2. Inputs
- Working directory state (`git status --short`).
- Branch name and remote configuration (`git remote -v`).

## 3. Step-by-Step Runbook
1. **Pre-commit Audit**:
   - Run `git status --short` and `git diff --stat`.
   - Ensure zero secrets, build outputs, `.env` files, or large checkpoints are staged.
2. **Quality Gate Pass**:
   - Ensure all quality gates (typecheck, lint, test, build) passed with exit code 0.
3. **Commit Creation**:
   - Author a clear, semantic commit message (e.g. `chore: reset repository for web and electron foundation`).
4. **Push Branch**:
   - Push to origin using `git push -u origin <branch-name>`.
   - Never force-push; never push directly to `main`.
5. **Remote Verification**:
   - Verify branch status using `git ls-remote --heads origin <branch-name>` and record commit SHA.

## 4. Acceptance Criteria & Checklist
- [ ] Working branch is NOT `main`.
- [ ] No force-push executed.
- [ ] Remote push confirmed via `git ls-remote`.
- [ ] Accurate, honest report delivered to operator.

## 5. Sources
- Semantic Versioning 2.0.0: https://semver.org/
- Conventional Commits: https://www.conventionalcommits.org/
