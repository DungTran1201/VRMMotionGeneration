# Workflow: Feature Delivery

Runbook for developing and delivering a bounded website or desktop capability.

---

## Phases

1. **Requirements & Modeling**: Formulate user story, acceptance criteria, and update contracts in `schemas/`.
2. **Component Implementation**: Implement component in `@vrm/ui` or adapter in `@vrm/app-core`.
3. **Automated Testing**: Write unit/component tests in Vitest.
4. **Build Validation**: Verify `pnpm build:web` and `pnpm build:desktop`.
5. **Documentation**: Update user guide in `docs/` and add Mermaid sequence diagram if IPC flow changed.
6. **PR Readiness**: Pass all quality gates and submit Pull Request.
