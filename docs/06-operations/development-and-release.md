# Development and Operations Runbook

**Scope**: Local Development, Testing, Building, and Packaging  
**Platform**: Web (Modern Browsers) + Electron Desktop (Windows, macOS, Linux)  

---

## 1. Prerequisites

- **Node.js**: v20.x or v22.x or v24.x LTS (Current environment: `v24.18.0`)
- **Package Manager**: `pnpm` v10+ or v12+ (`12.14.0`)
- **Git**: 2.30+ with LFS support

---

## 2. Common Workspace Commands

All commands are executed from the repository root:

```bash
# 1. Install all dependencies across workspace
pnpm install

# 2. Run Web app in local development server (Vite HMR on http://localhost:5173)
pnpm dev:web

# 3. Run Electron Desktop app in local development mode
pnpm dev:desktop

# 4. Run TypeScript typecheck across all packages and apps
pnpm typecheck

# 5. Run linting
pnpm lint

# 6. Run unit and contract tests (Vitest)
pnpm test

# 7. Build Web app for production
pnpm build:web

# 8. Build Electron Desktop app for production
pnpm build:desktop

# 9. Clean all build artifacts
pnpm clean
```

---

## 3. Desktop Packaging (Windows)

Packaging recipes reside in `infra/packaging/windows/`.
Production executable packaging uses `electron-builder` targeting 64-bit Windows portable and NSIS installers:

```bash
pnpm --filter @vrm/desktop package
```
