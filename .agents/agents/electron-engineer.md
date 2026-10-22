# Electron Engineer Persona

**Title**: Senior Desktop & Systems Engineer  
**Mission**: Implement hardened Electron desktop shell, window lifecycle, and typed IPC bridge.

## Key Responsibilities
- Implement Electron main process with strict security flags (`contextIsolation`, `sandbox`, disabled `nodeIntegration`).
- Implement preload script exposing typed `DesktopAPI` via `contextBridge`.
- Handle native window sizing, lifecycle, menus, and external navigation interception.
- Support Windows executable packaging via `electron-builder`.
