# `backend/src/` — Backend Application Source

## Purpose
Contains the core backend application packages, business logic, motion processing pipelines, and service orchestrators. The concrete framework (e.g. FastAPI) and library choices will be finalized via discovery and ADRs.

## What Belongs Here
- REST routing and WebSocket streaming session handlers.
- Canonical motion serialization and validation logic.
- Humanoid retargeting engines (e.g., source robot/skeleton to humanoid mapping).
- Source adapters isolating external motion models with clear Mode A (fixture) and Mode B (inference) boundaries.

## What Must NOT Belong Here
- Frontend client components or HTML/CSS assets.
- Unisolated imports from upstream vendor research code.
- Hardcoded absolute paths or direct access to experimental scratch files in `exp/`.

## Source-of-Truth Relationship
- Architecture must align with `docs/05-architecture/` and `models/architecture/`.
- Domain models and transformations must conform to `models/domain/`.
