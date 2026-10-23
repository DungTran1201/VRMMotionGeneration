# 04. Authentication & Session Architecture

This document establishes the architecture for sharing a unified identity between the Web client (`apps/web`) and Electron Desktop shell (`apps/desktop`), specifying session strategies, token lifecycles, cryptographic boundaries, and cross-platform credential persistence.

---

## 1. Unified Identity Topology

A single authoritative backend identity service manages account states, credentials, sessions, and security policies for all client form factors.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       UNIFIED IDENTITY TOPOLOGY                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Web Browser Client (apps/web)          Electron Native Desktop (apps/desktop)
│   ┌───────────────────────────┐          ┌───────────────────────────────┐  │
│   │  Vue 3 SPA Sandboxed      │          │  Vue 3 Renderer (Sandboxed)   │  │
│   │  In-Memory CSRF Token     │          │  Zero Token Storage           │  │
│   └─────────────┬─────────────┘          └───────────────┬───────────────┘  │
│                 │ HTTPS + Cookie                         │ Typed IPC Bridge │
│                 │ (SameSite=Lax)                         ▼                  │
│                 │                        ┌───────────────────────────────┐  │
│                 │                        │  Electron Main Process        │  │
│                 │                        │  - safeStorage Credential Box │  │
│                 │                        │  - Memory Access Token        │  │
│                 │                        └───────────────┬───────────────┘  │
│                 │                                        │ HTTPS Bearer     │
│                 ▼                                        ▼                  │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                   EDGE REVERSE PROXY / API GATEWAY                   │  │
│   │   - TLS 1.3 Termination         - Distributed Rate Limiter (Redis)  │  │
│   │   - WAF & DDoS Shield           - Security Headers & Strict CSP     │  │
│   └──────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│                                      ▼                                      │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                 IDENTITY & AUTHENTICATION SERVICE                    │  │
│   │   - Session Manager (Redis)     - Password Engine (Argon2id)         │  │
│   │   - CSRF Validator              - Token Authority (JWT/Opaque)       │  │
│   │   - Vault KMS Adapter           - Audit Event Emitter                │  │
│   └──────────────────────┬───────────────────────────────┬───────────────┘  │
│                          │                               │                  │
│                          ▼                               ▼                  │
│   ┌──────────────────────────────┐       ┌───────────────────────────────┐  │
│   │  REDIS DISTRIBUTED STORE     │       │  POSTGRESQL RELATIONAL DB     │  │
│   │  - Sliding Session Cache     │       │  - users & user_profiles      │  │
│   │  - Rate Limit Sliding Windows│       │  - persistent sessions        │  │
│   │  - Brute Force Counters      │       │  - password_reset_tokens      │  │
│   └──────────────────────────────┘       │  - user_secrets_vault         │  │
│                                          └───────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Platform Session Strategy Comparison & Decision

| Dimension                   | Web Browser Client (`apps/web`)                                                                            | Electron Desktop Client (`apps/desktop`)                                                                                   |
| :-------------------------- | :--------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------- |
| **Authentication Strategy** | **Stateful Cookie Session (BFF Pattern)**                                                                  | **Hybrid Bearer (Access JWT + Encrypted Refresh Token)**                                                                   |
| **Transport Medium**        | `Cookie: sid=<token>` transmitted automatically on origin HTTPS requests.                                  | `Authorization: Bearer <access_token>` injected via Main Process HTTP proxy.                                               |
| **Cookie Attributes**       | `HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=2592000`                                                  | N/A (Main process sends HTTPS API requests directly).                                                                      |
| **CSRF Defense**            | Mandatory: `X-CSRF-Token` header validated against cryptographic session secret.                           | Not applicable to native non-browser IPC calls.                                                                            |
| **Storage Mechanism**       | Managed entirely by the browser engine cookie jar. **Zero storage in `localStorage` or `sessionStorage`**. | Long-lived refresh token encrypted via **Electron `safeStorage`** API in OS credential vault. Access token in memory only. |
| **XSS Blast Radius**        | Cannot extract session token via JavaScript due to `HttpOnly`.                                             | Sandboxed renderer has no Node access, no `safeStorage` access, and no raw persistent tokens.                              |
| **Offline Tolerance**       | Online only.                                                                                               | Cached profile metadata in memory; re-authenticates automatically when network resumes.                                    |

### Architectural Rationale for Bifurcated Strategy

1. **Web Client (Cookie-based BFF)**:
   - _Reference_: RFC 10017 (OAuth 2.0 for Browser-Based Apps) and OWASP Session Management Cheat Sheet recommend server-managed cookies with `HttpOnly` over client-accessible tokens in `localStorage`. Storing bearer tokens in web browser `localStorage` allows any injected XSS payload to immediately exfiltrate full account credentials.
2. **Electron Desktop Client (safeStorage Hybrid Bearer)**:
   - _Reference_: Electron Security Tutorial and RFC 8252 (OAuth for Native Apps). Electron is a distributed native binary executing on the user's host operating system. A native app can securely hold an encrypted refresh token on the file system if encrypted using hardware-backed or OS-backed mechanisms (`safeStorage` utilizing Windows DPAPI, macOS Keychain, or Linux Secret Service). The sandboxed renderer never touches the file system or raw refresh token.

---

## 3. Session Lifecycle & Token Management

### 3.1 Session State Matrix

```
       [ Register / Login ]
                 │
                 ▼
          ┌─────────────┐
          │   ACTIVE    │◄─────────── [ Token Renewal / Sliding Window ]
          └──────┬──────┘
                 │
      ┌──────────┼───────────────┬────────────────────────┬─────────────────────┐
      │          │               │                        │                     │
[ Idle Timeout ] │      [ Absolute Expiry ]     [ User Logout / Revoke ] [ Password Reset ]
      │          │               │                        │                     │
      ▼          ▼               ▼                        ▼                     ▼
 ┌─────────┐┌─────────┐    ┌───────────┐            ┌───────────┐        ┌─────────────┐
 │ EXPIRED ││ REVOKED │    │ TERMINATED│            │ REVOKED   │        │ ALL REVOKED │
 └─────────┘└─────────┘    └───────────┘            └───────────┘        └─────────────┘
```

### 3.2 Timeouts & Expiration Policy

| Metric                | Web Client Session  | Desktop Client Session  | Rationale                                                                                                                    |
| :-------------------- | :------------------ | :---------------------- | :--------------------------------------------------------------------------------------------------------------------------- |
| **Idle Timeout**      | 24 Hours            | 7 Days                  | Web browsers on shared computers require shorter idle windows; desktop personal workstations tolerate longer idle intervals. |
| **Absolute Lifetime** | 30 Days             | 90 Days                 | Hard limit requiring re-authentication to prevent indefinite zombie sessions.                                                |
| **Access Token TTL**  | N/A (Opaque Cookie) | 15 Minutes              | Short-lived JWT minimizes window of vulnerability if memory is inspected.                                                    |
| **Refresh Token TTL** | N/A                 | 90 Days (with rotation) | Rotates upon every renewal; old refresh token is immediately invalidated.                                                    |

### 3.3 Session Rotation Rules

1. **Authentication Rotation**: Upon every successful login, any previous unauthenticated session identifier is destroyed, and a fresh 128-bit CSPRNG token is issued.
2. **Privilege Elevation Rotation**: When modifying critical account properties (password change, email change), the session ID is rotated to prevent concurrent session hijacking.
3. **Desktop Refresh Token Rotation**: When the desktop client exchanges a refresh token for a new 15-minute access token, the auth server returns BOTH a new access token and a newly rotated refresh token. The previous refresh token is marked consumed. If a consumed refresh token is ever submitted again, the server triggers an immediate **Family Revocation**, terminating all sessions associated with that token family under suspicion of theft.

---

## 4. Electron Desktop Security Architecture

### 4.1 Electron Native Preload & Main Process Separation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   ELECTRON PROCESS SECURITY BOUNDARY                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   RENDERER PROCESS (Sandboxed, WebPreferences Enforced)                     │
│   - contextIsolation: true                                                  │
│   - nodeIntegration: false                                                  │
│   - sandbox: true                                                           │
│   - CSP: default-src 'self'; script-src 'self'; connect-src https://...     │
│   - Interacts ONLY via: window.desktopAPI.auth.*                            │
│                                                                             │
│   ═══════════════════════════════════════════════════════════════════════   │
│   PRELOAD SCRIPT (contextBridge.exposeInMainWorld)                          │
│   - Validates IPC payload schemas before sending to Main                    │
│   - Never exposes ipcRenderer, require, or Buffer to Renderer               │
│                                                                             │
│   ═══════════════════════════════════════════════════════════════════════   │
│   MAIN PROCESS (Node.js Execution Context)                                  │
│   - Validates event.senderFrame on all incoming IPC messages                │
│   - Holds short-lived Access Token in Memory                                │
│   - Encrypts / Decrypts Refresh Token using safeStorage                     │
│   - Manages OS Credential File: %APPDATA%/vrm-desktop/session.enc           │
│   - Dispatches outgoing HTTPS requests to Identity API                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Electron `safeStorage` Credential Vault

1. **OS Cryptographic Providers**:
   - **Windows**: DPAPI (`CryptProtectData`), tying encryption to the current logged-in Windows user account.
   - **macOS**: Keychain Services, hardware-backed AES key stored in the OS login keychain.
   - **Linux**: Secret Service API / libsecret (GNOME Keyring, KWallet).
2. **Storage Algorithm**:
   ```typescript
   // Main Process Implementation Pattern (Proposed)
   import { safeStorage, app } from "electron";
   import * as fs from "node:fs/promises";
   import * as path from "node:path";

   const CREDENTIAL_PATH = path.join(app.getPath("userData"), "session.enc");

   export async function storeDesktopRefreshToken(
     token: string,
   ): Promise<void> {
     if (!safeStorage.isEncryptionAvailable()) {
       throw new Error("OS_SECURE_STORAGE_UNAVAILABLE");
     }
     const encryptedBuffer = safeStorage.encryptString(token);
     await fs.writeFile(CREDENTIAL_PATH, encryptedBuffer, { mode: 0o600 });
   }

   export async function retrieveDesktopRefreshToken(): Promise<string | null> {
     try {
       const encryptedBuffer = await fs.readFile(CREDENTIAL_PATH);
       return safeStorage.decryptString(encryptedBuffer);
     } catch (err) {
       return null;
     }
   }
   ```
3. **Host Compromise Threat Model**:
   - If an attacker obtains root or full administrative execution privileges in the user's OS user context, DPAPI or Keychain keys can be accessed under that user's identity. `safeStorage` protects against unprivileged offline file theft, casual file inspection, and cross-application reading, but cannot defend against a fully compromised host running kernel keyloggers.

---

## 5. Cross-Site Request Forgery (CSRF) Prevention (Web Client)

Because the Web client relies on `HttpOnly` session cookies, a multi-layered CSRF defense is mandatory:

1. **`SameSite=Lax` Cookie Baseline**:
   - Ensures cookies are withheld on cross-site subrequests (images, iframes, AJAX).
   - Mitigates standard cross-site form posting.
2. **Synchronized Cryptographic Token (`X-CSRF-Token`)**:
   - For all mutating operations (`POST`, `PUT`, `PATCH`, `DELETE`):
   - Upon session creation, server generates a 256-bit random CSRF token tied to the session ID in Redis.
   - Server delivers the token in the `X-CSRF-Token` response header or JSON body.
   - Frontend Vue application stores the CSRF token in an in-memory reactive store (never in `localStorage`).
   - Frontend attaches `X-CSRF-Token: <token>` to all outgoing mutating requests.
   - Server middleware validates: `HMAC_SHA256(received_token, SESSION_SECRET) === stored_token_hash`.
   - Requests lacking a valid token are rejected with `HTTP 403 Forbidden` (`csrf_validation_failed`).
