# Architecture Boundaries

## 1. Product Code Boundaries
- **`frontend/`**: Browser and client presentation layer only. Hosts web applications (`apps/web`), static public assets, and client unit/integration tests. Must interact with backend services strictly through documented API and WebSocket contracts.
- **`backend/`**: Server-side logic, API routing, data persistence, migrations, and service adapters. Decoupled from frontend frameworks.
- **`infra/`**: CI workflows, deployment scripts, container definitions, monitoring, and operations runbooks. Owns deployment and operational lifecycle, not application business logic.

## 2. Modeling & Documentation Boundaries
- **`models/`**: Canonical machine-readable specifications (YAML/JSON schemas). Single source of truth for requirements, domain entities, APIs, security policies, and deployment topology. Never store binary checkpoints or weights here.
- **`docs/`**: Human-readable engineering evidence and narrative documentation organized across discovery, planning, requirements, business process, use cases, architecture, domain, API, behavior, security, UX, testing, operations, and governance.
- **`diagrams/`**: Visual representations (Mermaid, SVG) derived from `docs/` and `models/`. Never treat diagrams as sole sources of truth; each diagram must cite its source models or doc artifacts.

## 3. Experiment Isolation (`exp/`)
- `exp/` is an independent, isolated exploratory workspace completely decoupled from the production website stack.
- It maintains its own `AGENTS.md`, `.gitignore`, environment manifests, execution scripts, datasets, checkpoints, artifacts, and evaluation reports.
- **Strict Isolation**: No direct code imports, shared runtime libraries, symlinks, submodules, runtime network calls, or shared configs between `exp/` and `frontend/`, `backend/`, or `infra/`.
- Experiment outcomes may only be promoted into production through an approved Architecture Decision Record (ADR), security review, formal API contract, and full automated test coverage.

## 4. Motion Pipeline & Upstream Isolation
- Source motion generation, kinematic decoding, canonical motion contracts, target avatar retargeting, network streaming, and client-side rendering remain distinct concerns.
- Upstream external research repositories (e.g., NVIDIA GR00T MotionBricks) must be treated as read-only references wrapped behind local adapter boundaries.
- Deterministic fixture paths must be maintained independently of GPU or pretrained weight availability.
