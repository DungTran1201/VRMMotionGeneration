---
name: discovery-and-planning
description: Plan, audit, and establish evidence-based scope for features and changes
---

# Discovery and Planning Skill

## 1. Purpose & When to Use
Use before initiating complex refactorings, feature implementations, or scope resets. Prevents unverified assumptions and ensures safe preservation of user state.

## 2. Inputs
- User requirements and prompt objectives.
- Current Git status (`git status --short --branch`, `git rev-parse --show-toplevel`).
- Filesystem state and active dependencies.

## 3. Step-by-Step Runbook
1. **Audit Working Tree**: Check for uncommitted modifications, untracked files, and active branch.
2. **Classify Facts**: Mark all findings as `VERIFIED`, `OBSERVED`, `INFERRED`, or `UNVERIFIED`.
3. **Backup Check**: If uncommitted changes exist, copy/move them to an external location outside the repo root and verify readability.
4. **Draft Inventory**: Enumerate files to be modified, created, or purged in `docs/00-discovery/`.
5. **Formulate Acceptance Criteria**: Define binary testable criteria before writing code.

## 4. Acceptance Criteria & Checklist
- [ ] Working directory confirmed as repository root.
- [ ] External backup verified readable.
- [ ] Scope confirmed: Web + Electron shell; legacy motion code excluded.
- [ ] Inventory documented.

## 5. Sources
- Michael Nygard, *Architecture Discovery Practices*
- AgentHarnessBuilderTools repository pattern
