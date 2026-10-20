# Documentation and Modeling Rules

## 1. Evidence-First Principle
- Base technical documentation on reproducible facts, inspected code, and verified command outputs.
- Explicitly classify technical statements where appropriate: `VERIFIED`, `OBSERVED`, `INFERRED`, `UNVERIFIED`, `BLOCKED`, or `NOT APPLICABLE`.
- Cite source URLs, commit SHAs, and access dates for external references.

## 2. Modeling vs Documentation vs Diagrams
- **`models/` (Structured Source of Truth)**: Machine-readable YAML/JSON models for requirements, processes, domain concepts, API contracts, security policies, and deployment configurations.
- **`docs/` (Human-Readable Evidence)**: Comprehensive lifecycle documentation structured from discovery (00) to governance (13). Keep documentation in sync with canonical models.
- **`diagrams/` (Derived Visualizations)**: Visual artifacts (Mermaid / SVG) providing projection views of models and documentation. Every diagram must explicitly reference its source model or requirement ID.

## 3. Truth Hierarchy
- Current active code and passing executable tests outrank stale documentation.
- Canonical structured models (`models/`) outrank derived diagrams (`diagrams/`).
- When conflicts arise between documentation and actual implementation, capture the discrepancy as an audit finding and resolve it through an explicit ADR before coding.
