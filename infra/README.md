# `infra/` — Infrastructure, Operations & Automation

## Purpose
The `infra/` directory owns deployment automation, CI/CD pipelines, developer operations scripts, container configurations, and operational observability. It is decoupled from product business logic.

## What Belongs Here
- Operational scripts and environment validation tools under `scripts/`.
- CI/CD workflow definitions under `ci/`.
- Deployment manifests, Dockerfiles, and compose files under `deployment/`.
- Monitoring, metrics, and health check configurations under `observability/`.

## What Must NOT Belong Here
- Application domain logic, kinematic transformation code, or frontend components.
- Hardcoded secrets, API tokens, or production credentials.
- Untracked large build output archives.

## Source-of-Truth Relationship
- Infrastructure definitions must reflect deployment topologies modeled in `models/deployment/` and runbooks documented in `docs/12-operations/`.
