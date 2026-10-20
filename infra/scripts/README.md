# `infra/scripts/` — Developer & Operational Scripts

## Purpose
Maintains cross-platform developer tooling, local environment verification utilities, dependency checkers, and maintenance automation scripts.

## What Belongs Here
- Local development environment bootstrap scripts.
- Port availability and service health check scripts.
- Layout and code style formatting enforcement scripts.

## What Must NOT Belong Here
- Production database drop scripts or destructive automation without safeguard flags.
- Scripts embedding hardcoded user credentials or private paths.

## Source-of-Truth Relationship
- Operational scripts must implement procedures specified in `docs/12-operations/`.
