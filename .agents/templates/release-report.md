# Release Report: [Version / Tag]

**Release Candidate**: [vX.Y.Z]  
**Operator**: Operation Dev  
**Branch**: [branch-name]  
**Commit SHA**: [Git Commit SHA]  
**Date**: [YYYY-MM-DD]  

---

## 1. Summary of Changes
[Summary of improvements, bugfixes, and refactorings]

## 2. Quality Gate Results

| Gate | Check | Command | Exit Code | Result |
| :--- | :--- | :--- | :--- | :--- |
| QG-01 | Dependency Install | `pnpm install --frozen-lockfile` | 0 | PASS |
| QG-02 | Typecheck | `pnpm typecheck` | 0 | PASS |
| QG-03 | Lint | `pnpm lint` | 0 | PASS |
| QG-04 | Unit & Contract Tests | `pnpm test` | 0 | PASS |
| QG-05 | Web Build | `pnpm build:web` | 0 | PASS |
| QG-06 | Desktop Build | `pnpm build:desktop` | 0 | PASS |
| QG-07 | Electron Security | Security test suite | 0 | PASS |
| QG-08 | Legacy Cleanliness | Cleanliness scan | 0 | PASS |

## 3. Remote Verification
- Remote URL: [URL]
- Remote Ref: `refs/heads/[branch-name]`
- Remote Verification Command: `git ls-remote --heads origin [branch-name]`
- Remote Status: VERIFIED
