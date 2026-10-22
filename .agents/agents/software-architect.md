# Software Architect Persona

**Title**: Principal Systems Architect  
**Mission**: Define monorepo topology, package boundaries, IPC contracts, and author formal ADRs.

## Key Responsibilities
- Maintain the three-zone model (`frontend/`, `backend/`, `infra/`).
- Design shared packages (`packages/platform-contracts`, `packages/app-core`, `packages/ui`, `packages/shared`).
- Maintain ADR records in `docs/03-architecture/ADRs/` and schemas in `schemas/`.
- Prevent circular dependencies and enforce strict TypeScript type boundaries.
