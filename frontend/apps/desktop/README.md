# Desktop Shell Application (`@vrm/desktop`)

Native desktop client built with Electron 34+ and Vue 3.

---

## Capabilities

- Mounts shared presentation views from `@vrm/ui`.
- Native window management, menus, and operating system integration.
- Hardened security baseline: Context Isolation, OS Sandboxing, disabled nodeIntegration, and strict CSP.
- Typed IPC bridge exposing `window.desktopAPI` through preload contextBridge.
- Windows packaging via `electron-builder` (`pnpm --filter @vrm/desktop package`).
