# `.agents` — Project Agent Harness

This directory is the portable source of truth for AI coding-agent guidance in `VRMMotionGeneration`. It implements the **Operation Dev** baseline: cross-functional software engineering governance, evidence-backed execution, strict product boundaries, and isolated experiment management.

## Contents
- **`rules/`**: Persistent constraints, architectural boundaries, modeling rules, security standards, and testing policies.
- **`skills/`**: Task playbooks in portable `SKILL.md` format (YAML frontmatter + step-by-step instructions).
- **`agents/`**: Specialist role profiles (architect, product analyst, frontend engineer, backend engineer, devops engineer, QA reviewer, security reviewer).
- **`config/`**: Lifecycle policies, change classification (`change-types.yaml`), artifact matrices (`artifact-matrix.yaml`), document mapping (`document-map.yaml`), and phase gates (`phase-gates.yaml`).
- **`templates/`**: Document, model, and report templates (ADR, use case, model, report).
- **`scripts/`**: Deterministic validators, including `validate_layout.py`.
- **`hooks/`**: Portable quality gate runners and Git hooks.
- **`hooks.json`**: Conservative hook automation configuration (disabled by default until official host runtime support is verified).

## Governance Workflow
1. **Intake & Discovery**: Classify change, audit existing state, verify facts in `docs/00-discovery/`.
2. **Modeling**: Author or update canonical machine-readable models in `models/`.
3. **Documentation & Diagrams**: Maintain human-readable specs in `docs/` and derived views in `diagrams/`.
4. **Implementation**: Build within designated boundaries (`frontend/`, `backend/`, `infra/`), keeping `exp/` isolated.
5. **Quality Gate**: Execute `python .agents/scripts/validate_layout.py` and automated test suites before delivery.
