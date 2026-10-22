---
name: architecture-and-adr
description: Formulate, document, and review Architecture Decision Records (ADR)
---

# Architecture and ADR Skill

## 1. Purpose & When to Use
Use when making non-trivial architectural decisions, such as choosing technology stacks, altering monorepo package boundaries, or defining security constraints.

## 2. Inputs
- Architectural problem statement and context.
- Decision drivers and trade-offs.
- Considered alternatives and official reference documentation.

## 3. Step-by-Step Runbook
1. **Identify Architectural Impact**: Determine if the change affects public APIs, package boundaries, security invariants, or runtime dependencies.
2. **Draft ADR**: Follow the format in `.agents/templates/ADR.md`.
3. **Include Alternatives**: Contrast at least two alternatives with pros and cons.
4. **Link Sources**: Reference official documentation URLs.
5. **Update Schemas**: If the ADR modifies contracts, update `schemas/` synchronously.

## 4. Acceptance Criteria & Checklist
- [ ] ADR stored in `docs/03-architecture/ADRs/` with sequential numbering.
- [ ] Context, decision outcome, and consequences articulated clearly.
- [ ] Architecture diagram updated in `diagrams/` if topology changed.

## 5. Sources
- Michael Nygard, *Documenting Architecture Decisions*
- Electron & Vue Architectural Guides
