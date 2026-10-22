# Skill Provenance, Attribution, and Licensing

This document tracks all external references, upstream catalogs, licenses, and adaptations incorporated into the `.agents/skills/` harness.

---

## 1. Upstream Catalogs and References

| Upstream Resource | URL | Commit / Version | License | Usage Mode |
| :--- | :--- | :--- | :--- | :--- |
| **Antigravity Awesome Skills** | `https://github.com/mit-network/Antigravity-awesome-skills` | `main` (Latest) | MIT / Public Domain where specified | Conceptual adaptation of TDD, debugging, documentation, security audit patterns. |
| **AgentHarnessBuilderTools** | `https://github.com/DungTran1201/AgentHarnessBuilderTools` | `main` (Owner repository) | MIT | Structure guidelines for multi-agent persona definitions, rules, and workflows. |
| **Electron Official Security Guide** | `https://www.electronjs.org/docs/latest/tutorial/security/` | Electron 34+ Docs | OpenJS Foundation / CC-BY-4.0 | Foundation for `electron-secure-shell` and `04-electron-security.md`. |
| **Vue 3 Guide & Best Practices** | `https://vuejs.org/guide/` | Vue 3.5+ Docs | MIT | Best practices for Composition API, SFC structure, reactivity. |
| **Vite Guide** | `https://vite.dev/guide/` | Vite 6+ Docs | MIT | Monorepo HMR, asset handling, multi-target builds. |
| **Playwright Documentation** | `https://playwright.dev/docs/intro` | Playwright 1.50+ | Apache 2.0 | Best practices for browser automated testing. |

---

## 2. Adaptation and Attribution Log

Every skill in `.agents/skills/` has been curated and authored specifically for the `VRMMotionGeneration` Web + Electron Desktop architecture to avoid copying monolithic catalogs or unvetted scripts:

1. **`discovery-and-planning/`**: Synthesized from standard agile software discovery runbooks and AgentHarnessBuilderTools patterns.
2. **`architecture-and-adr/`**: Adapted from Michael Nygard ADR format and Google Architecture Review practices.
3. **`vue-typescript-implementation/`**: Derived from official Vue 3 + TypeScript strict guidelines.
4. **`electron-secure-shell/`**: Derived directly from Electron's Checklist of Security Recommendations (Context Isolation, Sandboxing, IPC Allowlisting).
5. **`debugging-root-cause/`**: Synthesized from scientific method root-cause analysis patterns in awesome-skills.
6. **`test-driven-development/`**: Standard Kent Beck TDD red-green-refactor loop adapted for Vitest.
7. **`browser-e2e-playwright/`**: Modern E2E smoke and regression testing patterns.
8. **`appsec-review/`**: OWASP Desktop Security Top 10 + Electron Threat Model checks.
9. **`accessibility-ui-review/`**: W3C WCAG 2.1 AA checklist for accessible components.
10. **`documentation-and-mermaid/`**: Architecture-as-code documentation and Mermaid diagram standards.
11. **`release-and-git-hygiene/`**: Trunk-based release checklist, zero-force-push, semantic versioning.
