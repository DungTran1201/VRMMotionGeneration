# ADR-0002: Backend Runtime and Database Architecture

- **Status**: Accepted
- **Deciders**: Operation Dev, Software Architect
- **Date**: 2026-10-23
- **Technical Context**: Delivering a shared backend API service and relational persistence layer for the unified Web and Electron desktop applications.

---

## 1. Context and Problem Statement

The unified application requires a robust, secure, and maintainable backend service to manage identity, sessions, credentials, and user data. The backend must:
1. Serve both the Web client (`apps/web`) and Electron Desktop client (`apps/desktop`) using identical business rules and API contracts.
2. Operate deterministically offline during local development and automated CI testing without requiring external cloud accounts or running daemon prerequisites.
3. Enforce strict relational data integrity (unique constraints, foreign keys, cascades, ACID transactions).
4. Provide high testability, sub-millisecond local startup, and seamless integration with existing TypeScript contracts in `packages/platform-contracts`.

---

## 2. Considered Alternatives

### Alternative 1: Python FastAPI + PostgreSQL
- *Pros*: Excellent OpenAPI documentation generation, async IO performance.
- *Cons*: Introduces a secondary language runtime (Python) into a TypeScript monorepo, requiring separate package management (`uv`/`pip`), duplicate contract interfaces, and complex cross-language type synchronization. Requires running a PostgreSQL daemon locally or in Docker.

### Alternative 2: External Backend-as-a-Service (Supabase / Firebase / Auth0)
- *Pros*: Out-of-the-box authentication UI and managed database.
- *Cons*: Violates the deterministic offline requirement; introduces external cloud vendor lock-in; prevents full offline local execution and testing.

### Alternative 3: Node.js TypeScript Service with Dual Relational Driver (SQLite local / PostgreSQL production) (Selected)
- *Pros*:
  - **Single Language Ecosystem**: 100% TypeScript across frontend, desktop shell, shared contracts, and backend. Direct sharing of `@vrm/platform-contracts` and `@vrm/shared`.
  - **Zero-Daemon Offline Determinism**: Node.js 24 provides built-in `node:sqlite` (`DatabaseSync`), providing real persistent SQL, ACID transactions, foreign keys, and indexes without installing native C++ compilers (zero `node-gyp` failure risk on Windows).
  - **PostgreSQL Compatibility**: Schema DDL and SQL dialect are written to standard SQL, allowing direct deployment against PostgreSQL in production via database abstraction.
  - **Fast Execution**: In-process database lookups run in `< 1ms`, enabling instantaneous test suites.

---

## 3. Decision Outcome

**Selected Option:** Implement the backend as `@vrm/backend` in `backend/` using Node.js TypeScript and `node:sqlite` for local development/testing, adhering to the database schema defined in `docs/security/identity-and-account-management/05-account-data-model.md`.

---

## 4. Consequences

### Positive
- Monorepo consistency: single `pnpm install`, single `pnpm test`, unified TypeScript strict checking.
- Automated tests run 100% offline without Docker or PostgreSQL daemons.
- Zero external native binary compilation issues on Windows workstations.

### Negative / Trade-Offs
- Multi-instance horizontal scaling in production requires switching the driver adapter to PostgreSQL and distributed Redis (as documented in operations runbooks).
