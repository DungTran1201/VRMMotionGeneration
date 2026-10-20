---
name: feature-implementation
description: Implement a bounded website feature with tests, docs and evidence.
---

\
# Feature Implementation

1. Translate the request into user-visible behavior and acceptance criteria.
2. Find existing modules/routes/schema/tests before choosing placement.
3. Identify contract, migration, backward-compatibility, security, UX and performance effects.
4. Implement the smallest cohesive diff. Avoid unrelated renames/refactors.
5. Add tests first for bug fixes where practical; add success and failure cases for features.
6. Update API/schema docs and Mermaid diagrams if boundaries or sequence changed.
7. Run relevant backend/frontend tests, frontend build, validator and diff check.
8. Report actual results, skipped checks and remaining risk.

Do not mark the task done if the main acceptance criteria are unverified.
