# Technical & UI Reference Review

**Date of Review:** 2026-10-23  
**Reviewer:** Operation Dev  
**Purpose:** Formal evaluation of authoritative UI and technical references to guide the implementation of Web + Electron Desktop + Backend.

---

## 1. UI & Interaction Design References

### 1.1 shadcn-vue — Accessible, Composable Component Architecture
* **Source:** [https://www.shadcn-vue.com/docs/introduction](https://www.shadcn-vue.com/docs/introduction) | Accessed: 2026-10-23
* **Adopted Concepts**:
  - **Copy-and-Own Philosophy**: Direct encapsulation of composable Vue 3 primitives rather than heavy, inflexible third-party runtime component blackboxes.
  - **Design Token Discipline**: Semantic color tokens (`--bg-primary`, `--bg-secondary`, `--border-subtle`, `--accent`, `--text-primary`, `--text-muted`, `--destructive`) ensuring seamless light/dark mode transitions without ad-hoc hex values.
  - **Accessible Form States**: Form input groups with distinct label, description, and error message slots (`aria-describedby`, `aria-invalid`).
* **Implementation Decision**: Implemented clean design tokens and reusable presentation components (`StatusBadge`, `Button`, `Input`, `Card`) in `frontend/packages/ui` adhering to these semantics.

### 1.2 electron-vite-vue — Multi-Process Separation Pattern
* **Source:** [https://github.com/electron-vite/electron-vite-vue](https://github.com/electron-vite/electron-vite-vue) | Accessed: 2026-10-23
* **Adopted Concepts**:
  - **Rigid Three-Tier Process Isolation**: Clean separation between `src/main` (Node.js runtime, OS integrations, lifecycle), `src/preload` (narrow typed bridge via `contextBridge`), and `src/renderer` (sandboxed browser DOM context).
  - **Typed IPC Bridge**: Strict TypeScript interface contracts governing all IPC messages across process boundaries.
* **Implementation Decision**: Maintained strict process boundaries in `frontend/apps/desktop`, exposing only typed methods in `window.desktopAPI.auth` without raw `ipcRenderer` or Node access.

### 1.3 Vercel Web Interface Guidelines — Precision & Restraint
* **Source:** [https://vercel.com/design/guidelines](https://vercel.com/design/guidelines) | Accessed: 2026-10-23
* **Adopted Concepts**:
  - **Restrained Visual Aesthetics**: Monochromatic neutral palettes (slate/zinc) with purposeful accent colors; zero gratuitous 3D gradients, glowing borders, or visual clutter.
  - **Clear Information Density**: Compact, legible typography (system font stack with tabular numeric alignments for timestamps and metrics).
  - **Immediate Interaction Feedback**: Buttons disable immediately during active asynchronous requests to prevent double-submits. Error states persist until user interaction resolves them.
* **Implementation Decision**: Designed the unified Web and Desktop shells around clean navigation rails, subtle borders (`1px solid var(--border-subtle)`), and clear visual hierarchy.

### 1.4 Lucide Icons — Semantic Iconography
* **Source:** [https://lucide.dev/](https://lucide.dev/) | Accessed: 2026-10-23
* **Adopted Concepts**:
  - Consistent 24×24 viewBox, 2px stroke width, monochrome vector styling.
  - Explicit accessible titles and `aria-hidden="true"` attributes for decorative icons.
* **Implementation Decision**: Used curated, clean SVG vector icons adhering to Lucide proportions across the navigation and action bars.

---

## 2. Backend, Authentication & Security References

### 2.1 OWASP Cheat Sheet Series
* **Authentication**: [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
  - *Adopted*: Generic error messages for failed credentials (`"Invalid email or password"`); progressive exponential delays on repeated failures; no distinction between nonexistent account and bad password.
* **Password Storage**: [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
  - *Adopted*: Salted, memory-hard hashing using modern standard algorithms (Argon2id / Scrypt with unique 16-byte cryptographically secure random salts). Plaintext or reversibly encrypted passwords strictly prohibited.
* **Session Management**: [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
  - *Adopted*: 128-bit CSPRNG session identifiers; session rotation upon login; idle timeout (24h Web / 7d Desktop); absolute timeout (30d Web / 90d Desktop); revocation of all sessions on password reset.
* **CSRF Prevention**: [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
  - *Adopted*: Double protection using `SameSite=Lax` cookies combined with synchronized cryptographic `X-CSRF-Token` headers for all state-changing HTTP methods (`POST`, `PATCH`, `DELETE`).
* **REST Security & Rate Limiting**: [OWASP REST Security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html) & [OWASP REST Assessment](https://cheatsheetseries.owasp.org/cheatsheets/REST_Assessment_Cheat_Sheet.html)
  - *Adopted*: Multi-layer rate limiting binding to IP prefix and normalized account keys; `429 Too Many Requests` responses with `Retry-After` header; strict JSON content-type parsing and 100 KiB body limits.

### 2.2 Electron Security Checklist & Context Isolation
* **Source:** [Electron Security Tutorial](https://www.electronjs.org/docs/latest/tutorial/security) & [Context Isolation](https://www.electronjs.org/docs/latest/tutorial/context-isolation) | Accessed: 2026-10-23
* **Adopted Concepts**:
  - `contextIsolation = true`, `nodeIntegration = false`, `sandbox = true`.
  - Content Security Policy (CSP) enforced on all loaded documents.
  - Safe navigation: external links delegated to `shell.openExternal` after protocol validation (`https:` only).
  - Secure credential storage: refresh tokens encrypted via Electron `safeStorage` (Windows DPAPI, macOS Keychain).
