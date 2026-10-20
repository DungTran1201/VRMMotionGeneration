# `docs/11-testing/` — Testing Strategy & QA Benchmarks

## Purpose
Maintains the quality assurance strategy, test matrix, automated test pyramid definitions, performance benchmark targets, and verification criteria.

## What Belongs Here
- Test strategy documentation (unit, integration, visual regression, performance).
- Deterministic synthetic test vector specifications.
- Benchmark targets (framerate, memory footprint, WebSocket latency).
- Definition of Done (DoD) and quality gate criteria.

## What Must NOT Belong Here
- Executable Python or JavaScript test files (these belong in `backend/tests/` and `frontend/tests/`).
- Fabricated test results or unverified benchmark reports.

## Source-of-Truth Relationship
- Canonical test matrices and fixture definitions reside in `models/testing/`.
