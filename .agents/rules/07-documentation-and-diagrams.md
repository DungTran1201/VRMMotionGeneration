# Rule 07: Documentation, Schemas, and Diagrams

1. **Hierarchy of Truth**:
   - Level 1: Executable code and passing tests.
   - Level 2: Machine-readable specifications in `schemas/`.
   - Level 3: Human-readable documentation in `docs/` and ADRs.
   - Level 4: Visual projections in `diagrams/` (must cite source markdown/schema files).
2. **Synchronization**:
   - Updating code that modifies IPC contracts or schemas requires synchronous updates to `schemas/`, `docs/`, and `diagrams/`.
