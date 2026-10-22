# Electron Security Baseline

**Status**: ACTIVE & ENFORCED  
**Compliance Target**: Official Electron Security Recommendations (Electron 34+)  
**Audience**: Security Reviewer, Electron Engineer, Frontend Engineer  

---

## 1. Core Principles

All native desktop capabilities in this repository must comply with the official Electron security guidelines. Security is enforced through architecture rather than runtime patching.

---

## 2. Hardened WebPreferences Baseline

In `frontend/apps/desktop/src/main/index.ts`, every `BrowserWindow` instance must be instantiated with the following mandatory security flags:

```typescript
const mainWindow = new BrowserWindow({
  width: 1200,
  height: 800,
  minWidth: 800,
  minHeight: 600,
  webPreferences: {
    contextIsolation: true,       // Mandatory: isolates preload scripts from renderer
    nodeIntegration: false,        // Mandatory: disables Node APIs in renderer
    sandbox: true,                // Mandatory: executes renderer in OS sandbox
    webSecurity: true,            // Mandatory: enforces SOP and blocks file:// access
    allowRunningInsecureContent: false,
    navigateOnDragDrop: false
  }
});
```

---

## 3. Preload Bridge Contract (`contextBridge`)

Preload scripts MUST NEVER expose raw `ipcRenderer`, `require`, `process`, or `Buffer` to the renderer `window` object. 

Only a tightly scoped, strictly typed `desktopAPI` object is published:

```typescript
// frontend/apps/desktop/src/preload/index.ts
import { contextBridge, ipcRenderer } from 'electron';
import type { DesktopAPI } from '@vrm/platform-contracts';

const desktopAPI: DesktopAPI = {
  getAppVersion: () => ipcRenderer.invoke('app:get-version'),
  getDiagnostics: () => ipcRenderer.invoke('app:get-diagnostics'),
  ping: () => ipcRenderer.invoke('app:ping')
};

contextBridge.exposeInMainWorld('desktopAPI', desktopAPI);
```

---

## 4. Navigation & External URL Protection

1. **Window Open Interception**:
   Any call to `window.open` or links with `target="_blank"` are intercepted using `mainWindow.webContents.setWindowOpenHandler`.
   Only external URLs starting with `https://` are allowed to open in the system default browser via `shell.openExternal`.
2. **Will-Navigate Protection**:
   Navigation to any URL outside the local app bundle or authorized local development server (`http://localhost:*`) is blocked.

---

## 5. Content Security Policy (CSP)

A strict Content Security Policy is injected into the session headers:

```text
default-src 'self';
script-src 'self';
style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
font-src 'self' https://fonts.gstatic.com;
img-src 'self' data:;
connect-src 'self';
base-uri 'none';
form-action 'none';
```

---

## 6. IPC Validation and Sanitization

Every IPC listener in the main process must validate:
1. `event.senderFrame`: ensure the invocation originated from the main application frame, not an untrusted frame.
2. Payload schema: parameters are validated before consumption.
3. Errors are masked: internal stack traces or filesystem paths are never returned to the renderer.
