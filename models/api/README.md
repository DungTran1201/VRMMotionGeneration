# `models/api/` — API Contracts & Schemas

## Purpose
Maintains formal machine-readable OpenAPI (v3.1) and AsyncAPI schemas defining HTTP endpoints, WebSocket frame payloads, status events, and error models.

## What Belongs Here
- OpenAPI YAML/JSON definitions for REST services.
- AsyncAPI specifications for real-time WebSocket streaming channels.
- JSON Schema definitions for canonical motion data formats.

## What Must NOT Belong Here
- Backend web route implementation code.

## Source-of-Truth Relationship
- Canonical source for `docs/07-api/`, `diagrams/sequence/`, and test fixtures in `backend/tests/` and `frontend/tests/`.
