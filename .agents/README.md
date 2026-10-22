# Agent Harness — VRMMotionGeneration Web + Electron Foundation

This directory houses the operational agent harness, specialized role personas, engineering rules, runnable workflows, templates, and actionable skills for the Web + Electron Desktop monorepo.

---

## Directory Organization

```text
.agents/
├── README.md               # Overview of harness architecture and usage
├── skill-sources.md        # Provenance, licensing, and attribution for skills
├── agents/                 # Role-specific persona guides
├── rules/                  # Mandatory engineering, architecture, and security rules
├── skills/                 # Actionable, step-by-step technical runbooks
├── workflows/              # Multi-step end-to-end task runbooks
├── templates/              # Standard templates (ADR, Bug Report, Test Plan)
└── config/                 # Policies and skill index configuration
```

---

## Agent Personas (`agents/`)

1. **`operation-dev.md`**: Primary full-lifecycle software engineer and release operator.
2. **`product-ba.md`**: Requirements gathering, scope definition, user stories.
3. **`software-architect.md`**: System design, package boundaries, ADR formulation.
4. **`frontend-engineer.md`**: Vue 3, Vite, responsive UI, design token engineering.
5. **`electron-engineer.md`**: Desktop main process, window lifecycle, preload bridge, native packaging.
6. **`backend-engineer.md`**: Server-side architecture, HTTP/WebSocket contracts (when active).
7. **`qa-test-engineer.md`**: Vitest test coverage, integration tests, E2E validation.
8. **`appsec-reviewer.md`**: Threat modeling, CSP auditing, Electron security verification.
9. **`devops-release-engineer.md`**: GitHub Actions CI, build pipelines, Windows packaging.
10. **`technical-writer.md`**: Architecture documentation, Mermaid diagrams, release notes.

---

## Mandatory Engineering Rules (`rules/`)

- `00-workspace-and-scope.md`: Focus on Web + Electron foundation; legacy motion ML prohibited.
- `01-evidence-not-assumptions.md`: Evidence-based classification of facts.
- `02-architecture-boundaries.md`: Strict separation between apps and shared packages.
- `03-typescript-quality.md`: Strict mode, zero `any`, narrowing external data.
- `04-electron-security.md`: Context isolation, sandboxing, disabled nodeIntegration, CSP.
- `05-testing-and-gates.md`: Passing quality gates QG-01 through QG-08.
- `06-dependencies-and-supply-chain.md`: Reproducible lockfiles, zero vulnerability policy.
- `07-documentation-and-diagrams.md`: Documentation in `docs/`, diagrams in `diagrams/`, schemas in `schemas/`.
- `08-git-and-release.md`: Branch safety, zero force-push, zero commit of secrets.
