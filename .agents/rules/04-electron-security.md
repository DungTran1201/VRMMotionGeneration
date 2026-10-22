# Rule 04: Electron Security Invariants

1. **Mandatory WebPreferences**:
   - `contextIsolation = true`
   - `nodeIntegration = false`
   - `sandbox = true`
   - `webSecurity = true`
2. **Preload Exposure**:
   - Use `contextBridge.exposeInMainWorld('desktopAPI', ...)`.
   - Never expose `ipcRenderer`, `require`, `process`, or native Node modules directly.
3. **IPC Channel Allowlist**:
   - Main process only listens to typed, predefined channels.
   - Validate `event.senderFrame` on every IPC request.
4. **Navigation Interception**:
   - External links must use `shell.openExternal` after protocol validation (`https:` only).
   - Arbitrary internal navigation is blocked.
5. **Content Security Policy**:
   - A strict CSP must be active on all loaded documents.
