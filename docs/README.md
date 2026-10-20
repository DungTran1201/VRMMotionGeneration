# `docs/` — Engineering Lifecycle Documentation

## Purpose
The `docs/` directory is the human-readable repository of technical documentation, architectural decision records (ADRs), requirements, analysis, and operational guides. It mirrors the canonical models in `models/` in a human-accessible, narrative form.

## Organization
- `00-discovery/`: System baseline audits, exploratory findings, technology evaluations, and research reports.
- `01-planning/`: Project roadmap, milestone plans, and sprint backlogs.
- `02-requirements/`: Functional and non-functional requirement specifications.
- `03-business-process/`: Business workflows, avatar onboarding, and motion generation processes.
- `04-use-cases/`: Formal use case walk-throughs and scenario definitions.
- `05-architecture/`: System design, component boundary definitions, and Architecture Decision Records (ADRs).
- `06-domain/`: Humanoid kinematics, skeletal hierarchies, coordinate systems, and avatar standards (VRM/glTF).
- `07-api/`: REST endpoints, WebSocket streaming protocols, request/response models, and error codes.
- `08-behavior/`: System behavior, streaming lifecycle, and state machine transition rules.
- `09-security/`: Threat modeling, asset validation rules, authentication policies, and data handling.
- `10-ux/`: UI component design, viewport controls, camera interaction, and user flows.
- `11-testing/`: Test strategy, synthetic test vectors, QA benchmarks, and quality gate definitions.
- `12-operations/`: Deployment runbooks, container operations, environment setups, and troubleshooting.
- `13-governance/`: Release readiness criteria, upstream licensing compliance, and experiment promotion rules.

## What Belongs Here
- Markdown documents authored or validated by engineering roles.
- Clear statements supported by verified code paths and test evidence.

## What Must NOT Belong Here
- Application source code, compiled binaries, or model weights.
- Unverifiable marketing claims or fabricated benchmark figures.

## Source-of-Truth Relationship
- Synchronized with machine-readable specifications in `models/`.
- Active code and passing automated tests always outrank outdated documentation.
