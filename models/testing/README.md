# `models/testing/` — Test Models & Test Vectors

## Purpose
Maintains structured machine-readable test matrices, synthetic contract test vectors, validation schemas, and benchmark thresholds.

## What Belongs Here
- Synthetic canonical motion contract test vectors (JSON).
- Joint rotation limit and quaternion normalization test vectors.
- Automated test coverage and performance benchmark acceptance thresholds.

## What Must NOT Belong Here
- Executable test scripts (pytest / vitest).
- Large proprietary motion capture binary files.

## Source-of-Truth Relationship
- Canonical source for `docs/11-testing/` and test suites in `backend/tests/` and `frontend/tests/`.
