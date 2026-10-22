# Reset Decisions and Architectural Rationale

**Date**: 2026-10-22  
**Status**: APPROVED & EXECUTED  
**Author**: Operation Dev  

---

## 1. Context and Problem Statement

The repository `VRMMotionGeneration` originally embarked on exploratory implementations for AI humanoid motion generation (including ARDY, MotionStreamer, and DiP text-to-motion pipelines) alongside VRM avatar retargeting. These exploratory lines introduced heavy deep learning dependencies (PyTorch, CUDA, HuggingFace Transformers, Sentence-T5, diffusion models), large checkpoints (~13 GB), and complex python runtime environments.

The product directive has decisively pivoted: **eliminate all experimental motion generation, kinematic retargeting, model training, and ML inference pipelines.**

The target architecture is a **clean, production-grade Web + Electron Desktop application foundation** with a shared codebase, strict security posture, reproducible package management, and evidence-backed quality gates.

---

## 2. Key Decisions

### Decision 1: Full Purge of Experimental Code (`exp/`)

- **Choice**: Completely remove the `exp/` directory from the repository working tree and Git tracking.
- **Rationale**: Retaining placeholder stubs or partial experimental scripts creates cognitive dissonance and falsely implies that motion experimentation remains an active milestone.
- **Mitigation**: All experimental checkpoints, code, and uncommitted proposals (`VRM-StreamLite-Blueprint.md`) were backed up to `C:\Users\PC\Project\VRMMotionGeneration_pre_reset_backup_20261022` and `E:\VRMMotionGeneration_pre_reset_backup_20261022`. Previous Git commits preserve the full historical implementation.

### Decision 2: Adoption of `schemas/` in Place of `models/`

- **Choice**: Replace the ambiguous `models/` directory with `schemas/`.
- **Rationale**: In modern AI/ML software engineering, the term "models" routinely confuses developers, who expect model checkpoints, weights, or neural architecture definitions. Renaming this zone to `schemas/` makes it unambiguous that the directory holds machine-readable JSON Schema and contract definitions.

### Decision 3: Technology Stack — TypeScript, Vue 3, Vite, Electron, pnpm Workspaces

- **Choice**:
  - **Language**: TypeScript 5.7+ (strict mode enabled across all packages).
  - **Framework**: Vue 3 (Composition API + `<script setup>`).
  - **Bundler / Dev Server**: Vite 6+ for Web; Vite + Rollup for Electron main/preload.
  - **Desktop Shell**: Electron 34+ with hardened security defaults.
  - **Package Manager**: pnpm 12+ using monorepo workspaces (`pnpm-workspace.yaml`).
  - **Testing**: Vitest 3+ for unit, contract, and component testing.
- **Rationale**: Vue 3 provides exceptional performance, minimal bundle overhead, clean reactive primitives, and first-class TypeScript support. Vite enables sub-second HMR for both Web and Desktop development.

### Decision 4: Strict Electron Security Model

- **Choice**:
  - `contextIsolation: true`
  - `nodeIntegration: false`
  - `sandbox: true`
  - `webSecurity: true`
  - Content Security Policy (CSP) injected on all web contents.
  - Navigation locked to internal bundles; external URLs opened exclusively via allowlisted `shell.openExternal`.
  - Minimal, strongly typed IPC surface exposed through `contextBridge.exposeInMainWorld('desktopAPI', ...)`. Direct `ipcRenderer` or Node built-in access is prohibited in the renderer.

### Decision 5: Non-Destructive Git Strategy

- **Choice**: Perform the reset entirely on a dedicated branch `chore/web-electron-foundation-reset`.
- **Rationale**: Prevents accidental disruption of `main`. Zero force-push, zero rebase of public history. All changes are cleanly staged and committed.

---

## 3. Rollback Procedures

If an operator needs to restore the repository to the pre-reset experimental state:

1. **Git State Rollback**:
   ```bash
   git checkout main
   # Or switch back to commit 1338d4b
   git checkout 1338d4b
   ```
2. **Experimental Assets Restoration**:
   To recover uncommitted blueprints and downloaded weights:
   ```powershell
   Copy-Item -Path "C:\Users\PC\Project\VRMMotionGeneration_pre_reset_backup_20261022\VRM-StreamLite-Blueprint.md" -Destination ".\VRM-StreamLite-Blueprint.md"
   Copy-Item -Path "C:\Users\PC\Project\VRMMotionGeneration_pre_reset_backup_20261022\motionstreamer" -Destination ".\exp\motionstreamer" -Recurse
   Copy-Item -Path "C:\Users\PC\Project\VRMMotionGeneration_pre_reset_backup_20261022\dip-viser" -Destination ".\exp\dip-viser" -Recurse
   ```
