---
name: electron-secure-shell
description: Configure and verify a hardened Electron desktop shell and IPC bridge
---

# Electron Secure Shell Skill

## 1. Purpose & When to Use
Use when configuring Electron main process, preload contextBridge scripts, IPC handlers, or desktop window lifecycle.

## 2. Inputs
- Desktop requirements and capability definitions in `@vrm/platform-contracts`.
- Electron security baseline (`docs/04-security/electron-security-baseline.md`).

## 3. Step-by-Step Runbook
1. **Configure WebPreferences**:
   Ensure `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`, and `webSecurity: true`.
2. **Setup Preload**:
   Use `contextBridge.exposeInMainWorld('desktopAPI', apiObject)` with narrow, typed functions.
3. **Handle IPC in Main**:
   Use `ipcMain.handle` with sender validation (`event.senderFrame === mainWindow.webContents.mainFrame`).
4. **Enforce Navigation Policy**:
   Set `setWindowOpenHandler` to intercept external links and open via `shell.openExternal`.
5. **Set CSP**:
   Inject strict Content Security Policy headers in session responses.
6. **Execute Smoke Tests**:
   Run `pnpm --filter @vrm/desktop test` to verify security assertions.

## 4. Acceptance Criteria & Checklist
- [ ] Context isolation and sandbox verified enabled.
- [ ] Direct `ipcRenderer` or Node built-ins prohibited in renderer.
- [ ] All IPC channels allowlisted and tested.

## 5. Sources
- Electron Security Checklist: https://www.electronjs.org/docs/latest/tutorial/security/
- Electron Context Isolation Tutorial: https://www.electronjs.org/docs/latest/tutorial/context-isolation
