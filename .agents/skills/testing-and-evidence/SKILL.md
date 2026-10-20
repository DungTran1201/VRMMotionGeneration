---
name: testing-and-evidence
description: Build a reliable, evidence-backed quality gate for the website.
---

\
# Testing and Evidence

## Backend
- Run `python -m pytest backend/tests -v` from repository root with `PYTHONPATH=backend/src` (PowerShell: `$env:PYTHONPATH='backend/src'`).
- Test schemas, reconstruction math, retargeting, API, inference status, upload boundaries and WebSocket lifecycle.

## Frontend
- Run `npm test` and `npm run build` from `frontend/`.
- Test schema validation, avatar load/rig inspection, playback and cleanup.

## Evidence rules
- Capture the exact command and exit status. Never copy a previous report and call it a fresh test.
- Separate unit tests, mocked integrations, checkpoint-backed smoke tests, manual browser tests and benchmark measurements.
- If no checkpoint is available, state real inference was not tested; do not use fixture tests as evidence that it works.
- Update observed metrics only after collecting fresh measurements with environment details.
