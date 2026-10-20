# `docs/12-operations/` — Operations & Runbooks

## Purpose
Maintains operational documentation, deployment runbooks, local development setup guides, troubleshooting procedures, and incident recovery protocols.

## What Belongs Here
- Local developer environment setup instructions (Windows and Linux).
- Service start/stop and debugging procedures.
- Container build and execution runbooks.
- Backup, recovery, and data rollback procedures.

## What Must NOT Belong Here
- Production secrets or unencrypted credentials.
- Infrastructure automation code (belongs in `infra/`).

## Source-of-Truth Relationship
- Accompanies infrastructure implementations in `infra/` and topology models in `models/deployment/`.
