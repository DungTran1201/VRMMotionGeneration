# `docs/07-api/` — API Contracts & Protocols

## Purpose
Maintains human-readable specifications of all external and internal communication interfaces, REST endpoints, WebSocket streaming protocols, and serialization schemas.

## What Belongs Here
- RESTful HTTP endpoint definitions (routes, headers, methods, query parameters).
- WebSocket streaming lifecycle specifications (connect, frame stream, status updates, close).
- Standardized request and response payloads, status indicators, and error code catalogs.

## What Must NOT Belong Here
- Backend route handler implementation code.
- Client networking SDK code.

## Source-of-Truth Relationship
- Canonical machine-readable contracts are maintained in `models/api/` (OpenAPI/AsyncAPI) and interactions in `diagrams/sequence/`.
