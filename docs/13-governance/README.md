# `docs/13-governance/` — Governance & Compliance

## Purpose
Maintains project governance, release readiness criteria, licensing compliance policies, experiment promotion gates, and audit trails.

## What Belongs Here
- Release readiness checklist and sign-off criteria.
- Upstream license compliance reviews (e.g. Apache 2.0 vs NVIDIA Open Model License).
- Experiment promotion criteria (conditions under which an experiment from `exp/` may transition into production).
- Third-party dependency audit records.

## What Must NOT Belong Here
- Stale or contradictory policy declarations.
- Unreviewed claims of full commercial rights when upstream model weights impose non-commercial terms.

## Source-of-Truth Relationship
- Enforces governance across all repository activities and guides phase gate transitions defined in `.agents/config/phase-gates.yaml`.
