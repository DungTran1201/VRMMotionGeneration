# `frontend/` — Client Application Workspace

## Purpose
The `frontend/` directory contains all client-side code, user interfaces, 3D viewport components, and frontend-specific unit and integration tests. It is dedicated strictly to presentation, user interaction, local avatar rendering, and consuming backend APIs.

## What Belongs Here
- Client application packages under `apps/` (such as `apps/web/`).
- Static public web assets (under `public/`).
- Client-side unit, component, and end-to-end tests (under `tests/`).
- Format loaders and scene management for VRM and rigged glTF/GLB models.
- Client state management and network client adapters (REST / WebSocket).

## What Must NOT Belong Here
- Backend server logic, database interactions, or direct Python script executions.
- Direct upstream research dependencies (such as PyTorch or NVIDIA MotionBricks native libraries).
- Shared dependencies or symlinks connecting directly into `exp/`.
- Pretrained model checkpoints or oversized binary test vectors.

## Source-of-Truth Relationship
- UI interactions and designs must reflect canonical specifications in `models/ux/` and documentation in `docs/10-ux/`.
- Network calls must adhere strictly to the API contracts defined in `models/api/` and `docs/07-api/`.
