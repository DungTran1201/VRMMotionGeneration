# `frontend/tests/` — Frontend Automated Test Suite

## Purpose
Maintains all automated unit, component, schema validation, and end-to-end tests for the frontend client application.

## What Belongs Here
- Client-side unit tests for motion playback, interpolation (Slerp), and math utilities.
- Rig inspection and avatar loader adapter capability tests (VRM, rigged glTF).
- In-browser schema validation tests verifying compatibility with backend contracts.
- Component and integration test specs.

## What Must NOT Belong Here
- Backend Python pytest files or server integration tests.
- Untracked binary checkpoints or oversized avatar binaries.

## Source-of-Truth Relationship
- Test expectations are derived from `docs/11-testing/`, `models/testing/`, and API schemas in `models/api/`.
