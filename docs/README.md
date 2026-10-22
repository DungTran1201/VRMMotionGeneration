# Engineering Lifecycle Documentation Index

This directory contains human-readable engineering documentation, Architecture Decision Records (ADRs), specifications, and operational runbooks for the Web + Electron Desktop application foundation.

---

## Documentation Sections

| Section | Title | Primary Artifacts | Description |
| :--- | :--- | :--- | :--- |
| **`00-discovery/`** | Discovery & Audit | [`reset-inventory.md`](file:///c:/Users/PC/Project/VRMMotionGeneration/docs/00-discovery/reset-inventory.md)<br/>[`reset-decisions.md`](file:///c:/Users/PC/Project/VRMMotionGeneration/docs/00-discovery/reset-decisions.md) | Audit of purged experimental code, backup verification, and reset decisions. |
| **`01-planning/`** | Target Planning | [`target-architecture.md`](file:///c:/Users/PC/Project/VRMMotionGeneration/docs/01-planning/target-architecture.md) | High-level system context, package boundaries, and execution roadmap. |
| **`02-requirements/`** | Requirements | [`system-requirements.md`](file:///c:/Users/PC/Project/VRMMotionGeneration/docs/02-requirements/system-requirements.md) | Functional and non-functional requirements for the app shell. |
| **`03-architecture/`** | Architecture & ADRs | [`ADR-0001-web-desktop-monorepo.md`](file:///c:/Users/PC/Project/VRMMotionGeneration/docs/03-architecture/ADRs/ADR-0001-web-desktop-monorepo.md) | Formal ADR establishing Vue 3, Vite, Electron, and pnpm workspaces. |
| **`04-security/`** | Security Baseline | [`electron-security-baseline.md`](file:///c:/Users/PC/Project/VRMMotionGeneration/docs/04-security/electron-security-baseline.md) | Electron security invariants, CSP policy, and IPC channel hardening. |
| **`05-testing/`** | Quality Strategy | [`quality-gates.md`](file:///c:/Users/PC/Project/VRMMotionGeneration/docs/05-testing/quality-gates.md) | Automated quality gates (QG-01 to QG-08) and test execution matrix. |
| **`06-operations/`** | Operations & Runbook | [`development-and-release.md`](file:///c:/Users/PC/Project/VRMMotionGeneration/docs/06-operations/development-and-release.md) | Development server launch, builds, packaging, and debugging runbooks. |
| **`07-governance/`** | Release Governance | [`release-governance.md`](file:///c:/Users/PC/Project/VRMMotionGeneration/docs/07-governance/release-governance.md) | Branch protection, versioning policy, and release acceptance criteria. |
