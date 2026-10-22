# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-10-22

### Changed — Comprehensive Repository Reset
- **Purged Legacy Experimental Code**:
  - Removed `exp/` experimental workspace entirely (ARDY, MotionStreamer, DiP, MotionBricks, PyTorch, CUDA runtime, and checkpoints).
  - Backed up all uncommitted blueprints (`VRM-StreamLite-Blueprint.md`) and research artifacts to external location `C:\Users\PC\Project\VRMMotionGeneration_pre_reset_backup_20261022` and `E:\VRMMotionGeneration_pre_reset_backup_20261022`.
  - Retired kinematics, humanoid skeleton retargeting, and model training pipelines.
- **Transformed Architecture to Web + Electron Foundation**:
  - Established unified pnpm workspace monorepo.
  - Implemented `@vrm/platform-contracts`: pure TypeScript definitions for IPC, diagnostics, and capabilities.
  - Implemented `@vrm/shared`: application metadata, constants, and formatting utilities.
  - Implemented `@vrm/app-core`: runtime platform detection, fallback capability adapter, and reactive Vue store.
  - Implemented `@vrm/ui`: shared Vue 3 components, views (Overview, Settings, Diagnostics), design tokens (`tokens.css`), and responsive layouts (`ShellLayout`).
  - Implemented `@vrm/web`: browser client application built with Vite 6.
  - Implemented `@vrm/desktop`: hardened Electron 34+ desktop shell with contextBridge, OS sandbox, disabled nodeIntegration, and strict CSP.
- **Redesigned Agent Harness (`.agents/` and `AGENTS.md`)**:
  - Authored new `AGENTS.md` operating contract for Operation Dev.
  - Added 10 specialized agent personas in `.agents/agents/`.
  - Added 9 mandatory engineering rules in `.agents/rules/`.
  - Added 11 actionable, runbook-backed skills in `.agents/skills/`.
  - Added 4 multi-step workflows in `.agents/workflows/`.
  - Added standard engineering templates and policies.
  - Documented skill provenance, licensing, and attribution in `.agents/skill-sources.md`.
- **Adopted `schemas/`**:
  - Created machine-readable JSON Schema definitions (`desktop-ipc.schema.json`, `system-diagnostics.schema.json`, `app-settings.schema.json`).
- **Added Automated Quality Gates & CI**:
  - Configured GitHub Actions workflow (`.github/workflows/ci.yml`).
  - Added Vitest unit, contract, and component test suites.
