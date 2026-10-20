---
name: repository-audit
description: Audit an unfamiliar repository and establish verified facts, gaps, risks, and a safe change plan.
---

\
# Repository Audit

## Procedure
1. Record branch, clean/dirty working tree, top-level tree, lockfiles, package manifests, build/test commands and CI.
2. Trace user-visible entry points through API routes, services/adapters, schemas and tests.
3. Inspect README claims against executable code, especially TODO/NotImplemented, placeholder returns, mocked inference and silent fallbacks.
4. Map current architecture into: generation source, decoder/reconstruction, canonical contract, retargeting, transport, frontend rendering and asset lifecycle.
5. Check format capability reality: loadable asset vs rigged skeleton vs humanoid retarget-ready vs export-ready.
6. Inspect security boundaries for upload, paths, URLs, CORS, WebSocket, dependency and model loading.
7. Produce a short report: verified facts, gaps ranked P0-P3, evidence paths/line ranges, tests to run, minimal proposed changes.

## Acceptance
- Do not infer “implemented” merely from a README/table/diagram.
- Cite source paths and distinguish verified behavior from docs claims.
- Do not modify files during a read-only audit unless asked to fix findings.
