# 08. Threat Model & Abuse Case Analysis

This document presents a structured threat model based on the **STRIDE** methodology, analyzing security assets, trust boundaries, abuse cases, threat vectors, mitigations, and residual risks for the Authentication & Account Management platform.

---

## 1. Security Assets & Trust Boundaries

### 1.1 Critical Assets

1. **User Password Hashes**: Salted Argon2id hashes stored in the database.
2. **Web Session Identifiers**: CSPRNG 128-bit session cookies with `HttpOnly; Secure`.
3. **Electron Desktop Refresh Tokens**: Long-lived credentials persisted via OS `safeStorage`.
4. **Password Reset Tokens**: Ephemeral 256-bit hashes with 15-minute TTL.
5. **User AI Provider API Keys**: Third-party credentials encrypted via AES-256-GCM envelope encryption.
6. **Account Identity & Status**: User profile records, authorization state, and audit logs.
7. **Email Delivery Infrastructure**: SMTP/API credentials authorizing outbound password-reset emails.

### 1.2 Trust Boundaries Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TRUST BOUNDARY MAP                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ UNTRUSTED ZONE: Public Internet ]                                        │
│         │                                                                   │
│  ───────┼────────────────────────────────────────────── Trust Boundary 1    │
│         ▼                                                                   │
│  [ PERIMETER ZONE: Edge Reverse Proxy / WAF ]                               │
│         │ (TLS Termination, IP rate limiting)                              │
│  ───────┼────────────────────────────────────────────── Trust Boundary 2    │
│         ▼                                                                   │
│  [ APPLICATION ZONE: Identity & Auth Backend ]                              │
│         │                                                                   │
│         ├──────────────────────────────┬─────────────── Trust Boundary 3    │
│         ▼                              ▼                                    │
│  [ DATA ZONE: Redis Cache ]    [ DATA ZONE: PostgreSQL DB ]                 │
│                                                                             │
│  ───────┼────────────────────────────────────────────── Trust Boundary 4    │
│         ▼                                                                   │
│  [ EXTERNAL SECURE ZONE: Cloud KMS / Email Provider ]                       │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│  [ DESKTOP CLIENT INTERNAL BOUNDARIES ]                                     │
│                                                                             │
│  Renderer Process (Sandboxed)                                               │
│         │                                                                   │
│  ───────┼────────────────────────────────────────────── Trust Boundary 5    │
│         ▼                                                                   │
│  Preload Script (contextBridge) ──► Main Process (Node.js runtime)          │
│                                            │                                │
│  ──────────────────────────────────────────┼─────────── Trust Boundary 6    │
│                                            ▼                                │
│                               [ OS Secure Credential Vault (safeStorage) ]  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. STRIDE Threat & Abuse Case Matrix

| ID        | STRIDE Category                 | Threat / Abuse Scenario                                                                                                          | Target Asset                          | Likelihood | Impact   | Risk Level | Mitigation Control                                                                                                                                                                                                        | Verification / Proof                                                               |
| :-------- | :------------------------------ | :------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------ | :--------- | :------- | :--------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :--------------------------------------------------------------------------------- |
| **TM-01** | **Spoofing**                    | **Credential Stuffing & Brute Force**: Automated botnets replay leaked username/password combos.                                 | User Passwords & Sessions             | High       | High     | **HIGH**   | 1. Progressive exponential delay after 3 failed attempts.<br/>2. 15-min cooldown after 10 failed attempts.<br/>3. IP subnet + email rate limits.                                                                          | Rate-limit unit tests; k6 load test simulating 1,000 bad logins.                   |
| **TM-02** | **Spoofing / Identity**         | **Account Squatting via Unverified Email**: Attacker signs up with a victim's email address (`ceo@target.com`).                  | Account Identity                      | High       | Medium   | **HIGH**   | 1. Generic registration responses prevent harvesting.<br/>2. Prominent UI display: _"Unverified self-asserted contact address"_.<br/>3. Rate limit: 5 signups/hour per IP.<br/>4. High-risk domain reservation blocklist. | Unit test verifying unverified status badge and registration rate limiting.        |
| **TM-03** | **Denial of Service**           | **Password Reset Email Bombing**: Attacker repeatedly triggers forgot-password on an unverified email to spam the owner's inbox. | Email Infrastructure & Victim Mailbox | High       | Medium   | **HIGH**   | 1. Strict limit: 3 reset requests / 15 min per email; 10 / hour per IP.<br/>2. Generic HTTP 200 response suppresses outbound mail when quota exceeded.<br/>3. Global email dispatch hourly cap.                           | Forgot-password rate limit test; outbound email queue inspection.                  |
| **TM-04** | **Information Disclosure**      | **User Account Enumeration**: Attacker probes registration or forgot-password to discover if an email exists.                    | User Directory & Privacy              | High       | Medium   | **MEDIUM** | 1. Generic response on forgot-password.<br/>2. Equalized cryptographic response timing (normalizing Argon2id computation time across branches).                                                                           | Statistical timing analysis test (< 50ms variance across valid/invalid emails).    |
| **TM-05** | **Tampering**                   | **Session Hijacking / Fixation**: Attacker obtains session cookie or token and impersonates user.                                | Web Session / Token                   | Medium     | High     | **HIGH**   | 1. Fresh session ID issued on every login.<br/>2. `HttpOnly; Secure; SameSite=Lax` cookie flags.<br/>3. 24h idle / 30d absolute expiry.<br/>4. Session revocation on password reset.                                      | Session rotation tests; cookie header assertions.                                  |
| **TM-06** | **Tampering**                   | **Cross-Site Request Forgery (CSRF)**: Malicious third-party website induces victim's browser to submit mutating requests.       | Account Settings & Profile            | Medium     | High     | **MEDIUM** | 1. `SameSite=Lax` baseline.<br/>2. Mandatory `X-CSRF-Token` header validated via HMAC on all mutating requests (`POST`, `PUT`, `DELETE`).                                                                                 | CSRF test verifying 403 Forbidden when `X-CSRF-Token` is missing or invalid.       |
| **TM-07** | **Information Disclosure**      | **XSS Token Theft**: Injected malicious script in Web client exfiltrates auth credentials.                                       | Web Session Token                     | Medium     | High     | **HIGH**   | 1. Session token stored exclusively in `HttpOnly` cookie (JavaScript cannot access it).<br/>2. Strict Content Security Policy (`script-src 'self'`).<br/>3. Zero token storage in `localStorage`.                         | Browser security test asserting `document.cookie` cannot read `sid`.               |
| **TM-08** | **Elevation of Privilege**      | **Broken Object-Level Auth (BOLA / IDOR)**: Attacker manipulates `sessionId` or `userId` in API calls to access another's data.  | User Secrets, Sessions, Profile       | Medium     | High     | **HIGH**   | 1. Every API handler verifies: `record.user_id === authenticated_session.user_id`.<br/>2. Session lookup indexes scope exclusively to current user.                                                                       | Integration tests attempting to revoke another user's session ID (expect 403/404). |
| **TM-09** | **Elevation of Privilege**      | **Electron IPC Injection**: Compromised renderer script executes arbitrary Node.js commands or exploits IPC bridge.              | Desktop Host System                   | Low        | Critical | **HIGH**   | 1. `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`.<br/>2. Preload script exposes only typed narrow functions.<br/>3. Main process validates `senderFrame` and argument schemas.                      | Automated Electron security audit tests (`tests/security.spec.ts`).                |
| **TM-10** | **Information Disclosure**      | **Desktop Token Theft from Disk**: Malware reads local token files on client machine.                                            | Desktop Refresh Token                 | Medium     | Medium   | **MEDIUM** | 1. Refresh tokens encrypted at rest via Electron `safeStorage` (Windows DPAPI, macOS Keychain).<br/>2. Plaintext token files strictly prohibited.<br/>3. Token rotation on refresh.                                       | File inspection test confirming `%APPDATA%/session.enc` is encrypted binary.       |
| **TM-11** | **Information Disclosure**      | **Database Dump Exposes Stored User AI Keys**: Database compromised; attacker dumps table.                                       | User Third-Party Secrets              | Low        | Critical | **HIGH**   | 1. Envelope encryption via KMS (AES-256-GCM).<br/>2. Database stores only ciphertext and encrypted DEK; master key remains in hardware KMS.                                                                               | DB audit test verifying stored rows cannot be decrypted without KMS access.        |
| **TM-12** | **Server-Side Request Forgery** | **SSRF via Avatar URL**: Attacker sets avatar URL to internal IP (`http://169.254.169.254`) causing backend to fetch metadata.   | Internal Infrastructure               | Low        | High     | **MEDIUM** | 1. Backend never directly fetches external avatar URLs; clients load directly via signed CDN or avatar URLs are restricted to allowlisted domain.                                                                         | Schema validation test rejecting private IP ranges in URL fields.                  |
| **TM-13** | **Denial of Service**           | **Hash Algorithm Resource Exhaustion**: Attacker floods server with 10MB password strings to consume CPU during Argon2id.        | Server CPU & Memory                   | High       | High     | **MEDIUM** | 1. Maximum password length strictly enforced: `128` characters.<br/>2. Request body size limit: `100 KiB`.<br/>3. Gateway rate limits.                                                                                    | Boundary test asserting payload > 128 characters is rejected before hashing.       |

---

## 3. Residual Risks & Penetration Testing Criteria

While the security controls comprehensively mitigate remote exploitation, the following residual risks remain inherent to the product design:

1. **Unverified Email Squatting**: Because email verification is eliminated, early registrants can claim email identifiers they do not own. This cannot be solved purely cryptographically without an external verification loop. _Mitigation: Clear UI labeling, anti-enumeration, and administrative reclamation dispute workflows (P1)._
2. **Host-Level Compromise on Electron Clients**: If an adversary installs root malware or keyloggers on the user's desktop workstation, DPAPI keys and memory access tokens can be extracted. No software-only client can defend against a fully compromised host OS.
3. **Penetration Testing Triggers**:
   - Prior to public general availability (GA).
   - Upon introducing new third-party OAuth providers or Passkeys.
   - Any architectural modification to Electron preload IPC bridge or KMS envelope encryption pipelines.
