# `backend/tests/` — Backend Automated Test Suites

## Purpose
Maintains unit, integration, contract, and lifecycle tests for all backend services, retargeting engines, and API endpoints.

## What Belongs Here
- Unit tests for kinematic math, coordinate transforms, and rotation representations.
- Canonical motion schema validation tests using synthetic test vectors.
- Retargeting verification tests comparing input joint states against target humanoid hierarchies.
- API lifecycle tests (REST endpoints, WebSocket connection handling, and error codes).
- Source adapter tests verifying Mode A (fixture) deterministic execution and Mode B inference contract isolation.

## What Must NOT Belong Here
- Frontend browser tests or DOM assertions.
- Tests requiring gigabytes of proprietary pretrained weights to pass basic CI gates.

## Source-of-Truth Relationship
- Tests enforce compliance against `models/api/`, `models/domain/`, and the QA test strategy in `docs/11-testing/`.
