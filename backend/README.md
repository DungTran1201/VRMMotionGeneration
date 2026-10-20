# `backend/` — Backend Service & Kinematic Pipeline

## Purpose
The `backend/` directory hosts server-side services, REST/WebSocket API endpoints, kinematic retargeting logic, model execution adapters, and database migrations.

## What Belongs Here
- Application source packages under `src/`.
- Database schema migrations under `migrations/`.
- Automated backend unit and integration test suites under `tests/`.
- Adapters isolating external motion generation frameworks (e.g. MotionBricks).
- Serialization logic conforming to canonical motion schemas.

## What Must NOT Belong Here
- Frontend browser scripts, WebGL render loops, or DOM manipulation libraries.
- Direct symlinks or imports from `exp/`.
- Checkpoint binary weights committed to version control.
- In-place modifications to upstream vendor repositories.

## Source-of-Truth Relationship
- Backend APIs and endpoints must strictly implement the contracts defined in `models/api/` and `docs/07-api/`.
- Retargeting algorithms and skeleton hierarchies must reflect specifications in `models/domain/` and `docs/06-domain/`.
