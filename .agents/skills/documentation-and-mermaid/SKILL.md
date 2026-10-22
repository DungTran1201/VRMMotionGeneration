---
name: documentation-and-mermaid
description: Maintain synchronized technical documentation and Mermaid diagrams
---

# Documentation and Mermaid Skill

## 1. Purpose & When to Use
Use whenever modifying architecture, introducing new packages, updating schemas, or releasing features.

## 2. Inputs
- Code changes and architecture decisions.
- Schema definitions in `schemas/`.
- Markdown files in `docs/` and Mermaid files in `diagrams/`.

## 3. Step-by-Step Runbook
1. **Identify Changed Concepts**: Determine if the change modifies system boundaries, sequence flows, or deployment stages.
2. **Update Human Documentation**: Document rationale, prerequisites, and instructions in `docs/`.
3. **Synchronize Mermaid Diagrams**: Update or create diagrams in `diagrams/` (`.mmd`).
4. **Cite Sources**: Ensure each diagram explicitly links to its source markdown or schema file.
5. **Verify Syntax**: Ensure valid Mermaid syntax (quote labels containing special characters, avoid unescaped brackets).

## 4. Acceptance Criteria & Checklist
- [ ] Documentation reflects active code; zero outdated references.
- [ ] All diagrams cite source files.
- [ ] No broken markdown file links.

## 5. Sources
- Mermaid Documentation: https://mermaid.js.org/
- Google Technical Writing Guidelines
