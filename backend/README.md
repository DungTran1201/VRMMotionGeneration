# Backend Service Zone

**Status**: `NOT IMPLEMENTED / OPTIONAL`

---

## 1. Scope and Rationale

The current application foundation operates entirely as a unified client application across **Web** (SPA) and **Electron Desktop** (Native Shell).

Per ADR-0001:
- Client-side workflows, settings management, and diagnostics run locally within the application runtime.
- No mandatory HTTP/WebSocket backend server or database is required for this base foundation.
- To prevent artificial architectural bloat and misleading placeholder APIs, the server-side backend remains **unimplemented** until explicit business requirements mandate centralized cloud persistence, synchronization, or server-side services.

---

## 2. Future Extension Points

If backend capabilities are introduced in future milestones:
1. They must be governed by a dedicated ADR and OpenAPI/JSON Schema contracts in `schemas/`.
2. Communication between `frontend/` and `backend/` must occur exclusively over documented HTTP REST or WebSocket protocols.
3. Server-side code must reside in `backend/src/` with isolated tests in `backend/tests/`.
