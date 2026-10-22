# Quality Gates and Testing Strategy

**Document**: Quality Gates and Testing Standards  
**Status**: APPROVED  
**Applies to**: Web & Electron Desktop Foundation  

---

## 1. Overview

Quality gates enforce automated validation on all pull requests and branch builds prior to release. No code is merged or published without satisfying every gate.

---

## 2. Gate Definitions

| Gate ID | Name | Tooling | Target Criteria | Blocking? |
| :--- | :--- | :--- | :--- | :--- |
| **QG-01** | Dependency Audit & Install | `pnpm install --frozen-lockfile` | Zero resolution conflicts, lockfile in sync | **YES** |
| **QG-02** | Type Safety | `pnpm typecheck` (`tsc --noEmit`) | Zero TypeScript errors across all packages & apps | **YES** |
| **QG-03** | Lint & Formatting | `pnpm lint` | Zero lint errors; clean formatting | **YES** |
| **QG-04** | Unit & Contract Tests | `pnpm test` (`vitest run`) | 100% test pass rate; zero regressions | **YES** |
| **QG-05** | Web Production Build | `pnpm --filter @vrm/web build` | Clean bundle generation in `dist/` | **YES** |
| **QG-06** | Desktop Production Build | `pnpm --filter @vrm/desktop build` | Clean compilation of main, preload, renderer | **YES** |
| **QG-07** | Electron Security Audit | Automated security test suite | Context isolation, sandbox, disabled nodeIntegration | **YES** |
| **QG-08** | Legacy Scope Cleanliness | Workspace text scan | Zero imports or references to old motion models | **YES** |

---

## 3. Test Suites

### Unit & Component Tests (`frontend/apps/web/tests/`, `frontend/apps/desktop/tests/`, `frontend/tests/`)
- Platform contract validity and schema matching.
- Runtime platform detection (`web` vs `electron`).
- Safe fallback behavior in browser environment when `window.desktopAPI` is absent.
- Vue component mounting, state switching (Overview, Settings, Diagnostics).
- Error, loading, and empty state rendering.
- Electron security flags validation.
