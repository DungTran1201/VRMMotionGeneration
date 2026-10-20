# `models/` — Canonical Structured Models

> **Notice: Machine-Readable Specifications, NOT Model Weights**  
> The `models/` directory contains machine-readable YAML/JSON schemas and structured definitions representing system specifications (requirements, processes, architectures, domain entities, APIs, security policies, and deployments).  
> **Pretrained deep learning weights, checkpoints (`.ckpt`, `.pt`), and binary tensors must NEVER be placed here.**

## Purpose
Serves as the canonical machine-readable single source of truth for all system contracts, specifications, and architecture boundaries. Documentation in `docs/` and diagrams in `diagrams/` are synchronized with or derived from these models.

## Organization
- `context/`: System boundary and external actor structured models.
- `requirements/`: Machine-readable requirement models (IDs, categories, acceptance criteria).
- `process/`: Structured workflow and lifecycle state definitions.
- `architecture/`: Component definitions, interfaces, and decoupling rules.
- `domain/`: Kinematic models, humanoid skeleton hierarchies, and coordinate systems.
- `api/`: OpenAPI and AsyncAPI schemas for REST and WebSocket interfaces.
- `interaction/`: State transition and protocol sequence definitions.
- `security/`: Threat models, asset validation limits, and authorization rules.
- `ux/`: UI design tokens, component schemas, and layout configurations.
- `testing/`: Canonical test vectors, validation matrices, and benchmark thresholds.
- `deployment/`: Infrastructure topology and container configuration models.

## What Belongs Here
- Valid, parseable YAML or JSON schema and model files.
- Versioned specifications adhering to project schema standards.

## What Must NOT Belong Here
- Machine learning model weights, checkpoints, or binary tensors.
- Application code, compiled libraries, or runtime caches.

## Source-of-Truth Relationship
- Canonical source of truth: `models/` outranks narrative docs and derived diagrams.
- Active implementation code and passing automated tests outrank stale models.
