# Release Governance and Compliance

**Scope**: Versioning, Branching, Quality Gates, and Release Readiness  
**Authority**: Operation Dev  

---

## 1. Branching Strategy

- **`main`**: Protected branch. Represents release-ready, fully verified application code. Direct pushes are disabled.
- **`chore/web-electron-foundation-reset`**: Architectural reset branch. Contains the initial Web + Electron foundation.
- **Feature Branches**: `feat/<scope>`, `fix/<scope>`, `chore/<scope>`. Merged only via Pull Request with passing CI gates.

---

## 2. Release Acceptance Criteria

A release candidate may only be tagged when:
1. Every quality gate (QG-01 through QG-08) exits with code 0 in GitHub Actions.
2. Web production build passes without warnings.
3. Desktop build compiles successfully and launches without unhandled exceptions or security violations.
4. No dependencies contain critical vulnerabilities (via `pnpm audit`).
5. Zero references to purged legacy motion models, weights, or datasets exist in the codebase.
