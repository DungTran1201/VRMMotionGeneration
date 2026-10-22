# ADR-0001: Web and Electron Desktop Monorepo Foundation

- **Status**: Accepted
- **Deciders**: Operation Dev, Software Architect
- **Date**: 2026-10-22
- **Technical Context**: Repository reset from AI motion research to production-grade Web + Electron Desktop application foundation.

---

## 1. Context and Problem Statement

We require a modern, maintainable, and type-safe architecture capable of delivering both a Web client (browser SPA) and a native Desktop application (Windows, macOS, Linux) from a single shared repository.

The architecture must:
1. Share core presentation logic, design system, and business state across Web and Desktop without code duplication.
2. Ensure strict security boundaries in Electron (no arbitrary Node API exposure to the renderer).
3. Provide fast developer iteration (HMR) and reliable production builds.
4. Eliminate all legacy motion generation and machine learning dependencies.

---

## 2. Decision Drivers

- **Code Reusability**: Maximum reuse of UI views, components, and application logic between Web and Electron shells.
- **Security by Design**: Adherence to official Electron security recommendations (Context Isolation, Sandbox, No Node Integration, CSP, Typed IPC).
- **Developer Ergonomics**: Sub-second builds, TypeScript strictness, instant HMR, clear monorepo boundaries.
- **Maintainability**: Low operational overhead, zero micro-package sprawl, standard pnpm workspaces.

---

## 3. Considered Alternatives

### Alternative 1: Electron-only without Web targeting
- *Pros*: Simpler build pipeline.
- *Cons*: Prevents browser-accessible deployment, restricts user adoption, breaks web-first capability requirement.

### Alternative 2: Tauri + Rust
- *Pros*: Smaller binary footprint, memory efficient.
- *Cons*: Requires Rust toolchain and platform dependencies on development runners; team expertise is focused on TypeScript full-stack ecosystem.

### Alternative 3: Vue 3 + TypeScript + Vite + Electron via pnpm Workspaces (Selected)
- *Pros*:
  - Single language (TypeScript) throughout the stack.
  - Vue 3 Composition API provides outstanding reactive architecture and component encapsulation.
  - Vite delivers blazing fast development cycles.
  - Electron 34+ provides mature, stable cross-platform desktop integration.
  - pnpm workspaces offer fast, disk-efficient dependency resolution.
- *Cons*:
  - Desktop package size is larger than Tauri (~80MB vs ~15MB), acceptable for desktop distribution.

---

## 4. Decision Outcome

**Chosen Option**: Vue 3 + TypeScript 5.7+ + Vite 6+ + Electron 34+ in a pnpm monorepo workspace.

### Core Architectural Layers:

1. **`frontend/packages/platform-contracts`**:
   Pure TypeScript interfaces defining `DesktopAPI`, `DiagnosticsInfo`, `PlatformType`, and IPC channel enumerations. Zero runtime dependencies.
2. **`frontend/packages/shared`**:
   Common utility functions, application metadata, and constants.
3. **`frontend/packages/app-core`**:
   Platform detection (`getPlatform(): 'web' | 'electron'`), platform-specific capability adapters, and reactive application stores.
4. **`frontend/packages/ui`**:
   Vue 3 presentation layer: design system, CSS design tokens, navigation, views (Overview, Settings, Diagnostics), and empty/loading/error state views.
5. **`frontend/apps/web`**:
   Standard Vite single-page application entrypoint mounting the shared UI.
6. **`frontend/apps/desktop`**:
   Hardened Electron shell with separate `main`, `preload`, and `renderer` processes. Exposes typed `window.desktopAPI` via `contextBridge`.

---

## 5. Security Principles Enforced

1. `webPreferences.contextIsolation = true`: Mandatory context isolation between preload and renderer.
2. `webPreferences.nodeIntegration = false`: Node.js runtime disabled in renderer.
3. `webPreferences.sandbox = true`: Renderer process executed in an OS sandbox.
4. `webPreferences.webSecurity = true`: Same-origin policy strictly enforced.
5. IPC Allowlist: Only typed, registered IPC channels (`app:ping`, `app:get-diagnostics`, `app:get-version`) are handled.
6. External Navigation Guard: All `window.open` and external navigation events are validated against an allowlist and delegated to `shell.openExternal`.

---

## 6. Official References

- [Electron Security Tutorial](https://www.electronjs.org/docs/latest/tutorial/security/)
- [Electron Context Isolation](https://www.electronjs.org/docs/latest/tutorial/context-isolation/)
- [Vue 3 Documentation](https://vuejs.org/guide/)
- [Vite Guide](https://vite.dev/guide/)
- [pnpm Workspaces](https://pnpm.io/workspaces/)
- [Vitest Documentation](https://vitest.dev/guide/)
