# `infra/ci/` — Continuous Integration Workflows

## Purpose
Maintains portable continuous integration workflow templates, automated test execution pipelines, build checks, and quality gate triggers.

## What Belongs Here
- Pipeline templates for GitHub Actions or other standard CI runners.
- Automated linting, test execution, and layout validation stage configurations.
- Matrix definitions for multi-platform test execution (e.g. Windows / Linux).

## What Must NOT Belong Here
- Production private keys, signing certificates, or deployment credentials.
- Ad-hoc scripts that fail without network connectivity to proprietary servers.

## Source-of-Truth Relationship
- CI gates must enforce the quality metrics defined in `models/testing/` and `docs/11-testing/`.
