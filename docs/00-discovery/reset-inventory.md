# Reset Inventory — VRMMotionGeneration Pre-Reset Audit

**Date**: 2026-10-22  
**Operator**: Operation Dev  
**Branch**: `chore/web-electron-foundation-reset`  
**Base Commit**: `1338d4b` (incorporating `cae6a60` and `9612a8f`)

---

## 1. Executive Summary

This inventory documents the exhaustive classification of all files, directories, dependencies, and experiments present in `VRMMotionGeneration` prior to the architectural reset into a unified **Web + Electron Desktop Foundation** monorepo.

All legacy motion generation experiments, neural network checkpoints, training scripts, motion retargeting modules, and avatar kinematics have been cataloged and safely purged from the active tree. Uncommitted user work and research assets have been backed up externally with verified readability.

---

## 2. External Backup Verification

Prior to any destructive filesystem modifications, all uncommitted changes, research blueprints, and experimental data were inventoried and safely moved to an external location outside the Git repository root.

- **Primary Backup Path**: `C:\Users\PC\Project\VRMMotionGeneration_pre_reset_backup_20261022`
- **Secondary / Redundant Path**: `E:\VRMMotionGeneration_pre_reset_backup_20261022`
- **Verification Status**: `VERIFIED READABLE` (confirmed via file inspection and directory enumeration)
- **Backed-Up Items**:
  1. `VRM-StreamLite-Blueprint.md` (17,372 bytes) — Uncommitted proposal for causal-latent streaming student motion generator.
  2. `exp/motionstreamer/` (7.83 GB) — MotionStreamer upstream clone, `.venv` PyTorch environment, Sentence-T5 models, and experimental artifacts.
  3. `exp/dip-viser/` (5.24 GB) — DiP (Diffusion Planner) test-to-motion workspace, including checkpoints (`DiP_no-target_10steps_context20_predict40`), `.venv`, and scripts.

---

## 3. Inventory of Purged Legacy Artifacts

### 3.1. Exploratory Motion Experiments (`exp/`) — REMOVED

| Component / Path | Nature / Content | Size / Scope | Disposal Action | Justification |
| :--- | :--- | :--- | :--- | :--- |
| `exp/ardy-vrm-demo/` | ARDY motion generation demo, FastAPI backend, VRM frontend viewer | 63 tracked files | Deleted from Git index & working tree | Legacy motion generation scope no longer supported. Fully preserved in Git history (`cae6a60`). |
| `exp/dip-viser/` | Official DiP text-to-motion model with Viser 3D interactive viewer | 42 tracked files + 221MB weights + 5GB venv | Backed up externally; removed from repo | Motion diffusion models and 3D Viser viewer excluded from new Web + Electron shell foundation. |
| `exp/motionstreamer/` | Upstream MotionStreamer clone and environment | Untracked (7.8 GB) | Backed up externally; removed from repo | Causal latent streaming research out of scope for general desktop/web foundation. |
| `VRM-StreamLite-Blueprint.md` | Architectural proposal for student streaming model | 17 KB markdown | Backed up externally; removed from repo | Motion modeling proposals not relevant to active app shell foundation. |
| `exp/artifacts/`, `exp/checkpoints/`, `exp/datasets/`, `exp/environments/`, `exp/experiments/`, `exp/reports/`, `exp/scripts/` | Scaffold placeholder READMEs and `.gitignore` | 10 tracked files | Removed from Git index & working tree | Legacy experimental workspace removed to prevent confusion. |

### 3.2. Machine Learning / Motion Models (`models/`) — PURGED & RENAMED

| Path | Original Role | Disposal Action | Justification |
| :--- | :--- | :--- | :--- |
| `models/domain/` | Skeleton, joint hierarchy, and kinematics specs | Removed | Kinematic domain removed from product scope. |
| `models/api/` | FastAPI motion generation schemas | Removed | Replaced by machine-readable JSON schemas in `schemas/`. |
| `models/requirements/`, `models/process/`, `models/ux/`, `models/security/`, `models/testing/`, `models/deployment/` | Scaffold specification placeholders | Removed | Renamed to `schemas/` via ADR-0001 to eliminate naming collision with ML weights. |

### 3.3. Legacy Agent Harness (`.agents/`) — REDESIGNED

| Path | Original Role | Disposal Action | Justification |
| :--- | :--- | :--- | :--- |
| `.agents/agents/*` | 7 avatar/motion-specific personas (e.g., `avatar-frontend-engineer.md`, `backend-motion-engineer.md`) | Replaced | Restructured into 10 cross-functional roles for Web + Electron development. |
| `.agents/rules/*` | Avatar formats, rigging, motion data contracts | Replaced | Replaced by 9 strict software engineering and Electron security rules. |
| `.agents/skills/*` | `avatar-format-adapters`, `motion-retargeting`, `motionbricks-real-inference`, `secure-web-assets` | Replaced | Replaced by 11 focused skills (Vue 3, Electron secure shell, TDD, Playwright E2E, AppSec). |

---

## 4. Retained Architectural Concepts & Rationale

| Asset / Boundary | Retention Decision | Rationale |
| :--- | :--- | :--- |
| `.git/` history | **Preserved intact** | No history rewriting, rebase, or force-push. Preserves complete engineering lineage. |
| `frontend/` top-level directory | **Retained & Evolved** | Monorepo layout retains `frontend/` as the home for `apps/web/`, `apps/desktop/`, and shared packages (`packages/ui`, `packages/app-core`, `packages/shared`, `packages/platform-contracts`). |
| `backend/` top-level directory | **Retained as Stub (NOT IMPLEMENTED)** | Retains decoupled architectural zone; marked explicitly as optional/not implemented since the app shell does not currently require server services. |
| `infra/` top-level directory | **Retained & Modernized** | Retains operational zone for CI workflows (`.github/workflows/ci.yml`), build scripts, and desktop packaging configurations. |
| Git Remotes & Branches | **Preserved** | Remote `origin` (`https://github.com/DungTran1201/VRMMotionGeneration.git`) untouched; `main` branch untouched; work conducted on `chore/web-electron-foundation-reset`. |

---

## 5. Safety Checklist Verification

- [x] Working directory verified as repository root.
- [x] Remote URL verified as `DungTran1201/VRMMotionGeneration`.
- [x] Git LFS verified (version 3.7.0).
- [x] All uncommitted user assets backed up outside workspace (`C:\Users\PC\Project\VRMMotionGeneration_pre_reset_backup_20261022`).
- [x] Backup verified readable by independent command executions.
- [x] Safety branch `chore/web-electron-foundation-reset` checked out from clean HEAD.
- [x] Zero force-push, zero `git clean -xfd`, zero destructive wildcard resets.
