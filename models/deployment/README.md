# `models/deployment/` — Deployment Models

## Purpose
Maintains structured machine-readable specifications of deployment topologies, container requirements, environment variable schemas, and resource constraints.

## What Belongs Here
- Deployment topology models (services, port mappings, internal networks).
- Environment variable configuration schemas (required vs optional keys, types).
- Hardware resource allocations (minimum RAM, CPU cores, GPU capabilities).

## What Must NOT Belong Here
- Production environment values with active credentials.
- Container image binaries.

## Source-of-Truth Relationship
- Canonical source for `docs/12-operations/`, `diagrams/deployment/`, and configuration manifests in `infra/deployment/`.
