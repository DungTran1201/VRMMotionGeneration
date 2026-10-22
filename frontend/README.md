# Frontend Monorepo Ecosystem

This directory contains the entire client presentation layer for both the browser Single Page Application (`apps/web`) and the native desktop shell (`apps/desktop`), sharing core domain logic, contracts, and design tokens across modular packages.

---

## Directory Organization

```text
frontend/
├── apps/
│   ├── web/                    # Browser client (Vite SPA)
│   └── desktop/                # Desktop shell (Electron main, preload, renderer)
├── packages/
│   ├── platform-contracts/     # TypeScript interfaces and IPC channel schemas
│   ├── shared/                 # Common metadata and utility functions
│   ├── app-core/               # Platform detection, adapters, and reactive stores
│   └── ui/                     # Shared Vue 3 components, views, and CSS tokens
└── tests/                      # Workspace-level contract tests
```

---

## Shared Architecture Principles

1. **Write Once, Adapt Anywhere**: Shared UI components in `@vrm/ui` run identically in browser and Electron.
2. **Capability Fallback**: When desktop-specific native APIs are unavailable, `@vrm/app-core` provides graceful web fallbacks without crashing.
3. **Hardened Security**: Desktop shell enforces OS sandbox, context isolation, and disabled nodeIntegration.
