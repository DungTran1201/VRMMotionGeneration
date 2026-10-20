# `infra/deployment/` — Deployment Configurations & Containerization

## Purpose
Maintains container configurations, orchestration manifests, and deployment templates for local development and target production environments.

## What Belongs Here
- Container definitions (e.g. Dockerfile for backend services and web frontends).
- Local multi-service compose files (e.g. `docker-compose.yml`).
- Reverse proxy configurations (e.g. Nginx / Caddy templates).

## What Must NOT Belong Here
- Production environment `.env` files with active credentials.
- Container images or raw layer blobs.

## Source-of-Truth Relationship
- Configurations reflect deployment topology specifications in `models/deployment/` and procedures in `docs/12-operations/`.
