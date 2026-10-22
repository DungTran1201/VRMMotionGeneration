# Workflow: Repository Reset

Use when performing an architectural reset of a repository while preserving Git history and backing up uncommitted user assets.

---

## Phases

1. **Phase 1: Verification & Pre-flight**
   - Check repo root, remote origin, and Git LFS.
   - Audit uncommitted changes and tracked experiments.
   - Create external backup of uncommitted user work; verify readability.
   - Create dedicated safety branch (e.g. `chore/web-electron-foundation-reset`).

2. **Phase 2: Legacy Purge**
   - Safely remove deprecated experimental directories (`exp/`, `models/`).
   - Remove out-of-scope dependencies.
   - Document inventory in `docs/00-discovery/reset-inventory.md`.

3. **Phase 3: Scaffold & Foundation**
   - Initialize pnpm monorepo workspace.
   - Create target packages (`platform-contracts`, `shared`, `app-core`, `ui`).
   - Create target apps (`apps/web`, `apps/desktop`).
   - Author ADRs and schemas.

4. **Phase 4: Quality Gate Verification**
   - Run typecheck, lint, tests, and production builds.
   - Audit Electron security invariants.

5. **Phase 5: Commit & Push**
   - Stage verified changes.
   - Commit and push to remote safety branch.
   - Verify remote receipt via `git ls-remote`.
