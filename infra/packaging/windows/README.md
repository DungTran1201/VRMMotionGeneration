# Windows Packaging Specifications

This directory contains specifications and assets for building Windows desktop distributables from `frontend/apps/desktop`.

---

## Target Formats

1. **NSIS Installer**: Standard self-extracting Windows installer (`.exe`) with desktop shortcut and uninstaller.
2. **Portable Executable**: Zero-install standalone executable for evaluation and portable usage.

## Configuration

Packaging is executed via `electron-builder` using the configuration declared in `frontend/apps/desktop/package.json` under the `"build"` block.

Build command:
```bash
pnpm --filter @vrm/desktop package
```
