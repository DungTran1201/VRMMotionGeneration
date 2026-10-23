# 01. Business Requirements: Authentication & Account Management

This document establishes the business requirements, user personas, operational scope, and architectural risk analysis for unified Authentication & Account Management across the Web and Electron Desktop applications.

---

## 1. Product Context & Core Objective

The system provides a unified authentication and identity management service shared between:

1. **Web Client** (`apps/web`): Single-page web application accessed through modern standards-compliant web browsers.
2. **Desktop Client** (`apps/desktop`): Native Electron shell operating across Windows, macOS, and Linux.

The overarching goal is to enable frictionless user registration, secure session management, and robust account controls while maintaining enterprise-grade security against automated credential stuffing, token theft, account takeover, and API abuse.

---

## 2. Definitive Product Decision: No Email Verification

### 2.1 Explicit Architectural Baseline

By executive product decision, **email verification is strictly eliminated from user registration and login workflows**:

- **No Email Verification Gate**: No confirmation links, email OTPs, verification pins, resend endpoints, or verification tokens will be generated or sent during registration.
- **Immediate Account Activation**: Newly registered accounts immediately enter the `active` status and are fully authorized to log in.
- **No `email_verified` Requirement**: No API endpoint, database schema constraint, or authorization policy shall require `email_verified == true`.
- **Independent Account Recovery**: The password reset mechanism (which sends a time-limited reset link to the recorded contact address) is an independent recovery flow and shall never be utilized as a backdoor mechanism to enforce registration verification.

### 2.2 Risk Analysis of Unverified Email Identifiers

Operating an identity platform with unverified email addresses introduces specific structural risks that must be acknowledged, monitored, and mitigated:

| Risk Domain                        | Threat Description                                                                                                                     | Business / Operational Impact                                                                                                                                       | Architectural Mitigation                                                                                                                                                                                                                                                   |
| :--------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Account Squatting**              | An attacker registers an account using an email address belonging to an innocent third party (e.g., `target@company.com`).             | The legitimate owner of the email cannot register that address later without account reclamation or conflict resolution.                                            | 1. Generic registration failure messages prevent enumeration.<br/>2. Rigorous per-IP and global registration rate limits prevent automated mass squatting.<br/>3. Future account claiming policy (P1) based on identity challenge.                                         |
| **Typo-Induced Recovery Lockout**  | A user mistypes their email during signup (e.g., `user@gmai.com` instead of `user@gmail.com`).                                         | The user can log in with their password initially, but if they forget their password, recovery is impossible because reset emails are sent to the misspelled inbox. | 1. Clear UI warning at registration confirming email spelling.<br/>2. Re-authentication prompts when modifying account settings.<br/>3. Prominent profile banner explicitly stating: _"This email is self-asserted and unverified. Ensure accuracy for account recovery."_ |
| **Password Reset Bombing**         | An adversary initiates repeated password reset requests for squatted accounts to flood the legitimate mailbox owner with reset emails. | Potential reputation damage to the outbound email domain, spam complaints, and mail provider suspension.                                                            | 1. Strict rate limiting on `/api/v1/auth/forgot-password` (3 requests / 15 minutes per email; 10 / hour per IP).<br/>2. Global hourly email dispatch budget cap.<br/>3. Generic HTTP 200 response regardless of whether the email exists.                                  |
| **Reputational Misrepresentation** | A malicious user claims an authority email (e.g., `security@gov.org`) to deceive peers in multi-user collaboration features.           | Reputational risk and phishing within the platform.                                                                                                                 | 1. Explicit display rule: Emails are **never marked as Verified** in UI.<br/>2. Display names are decoupled from the login email.<br/>3. High-risk domain reservation blocklist for registration.                                                                          |

### 2.3 Evaluation of Identifier Strategies

1. **Option A (Selected Baseline — Email as Login Identifier)**:
   - _Rationale_: Familiar, standard UX; users remember their email easily.
   - _Trade-off_: Exposes the platform to email squatting and typo-induced lockout as analyzed above.
2. **Option B (Alternative Considered — Unique Username + Optional Contact Email)**:
   - _Rationale_: Eliminates email squatting for login; the primary identifier is a unique handle (e.g., `@alex_dev`). An email is only collected optionally for password recovery.
   - _Trade-off_: Higher signup friction due to username collisions and availability checks.
   - _Status_: Open for product review; Option A is adopted as the primary specification.

---

## 3. System Actors

| Actor                               | Description                                                                                            | Trust Boundary                                                  |
| :---------------------------------- | :----------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| **Guest / Anonymous Visitor**       | Unauthenticated user accessing the Web landing page or unconfigured Desktop client.                    | Untrusted Public Zone.                                          |
| **Registered User**                 | Authenticated principal possessing valid credentials and an active account session.                    | Authenticated User Zone.                                        |
| **Web Client (`apps/web`)**         | Browser execution context running Vue 3 SPA under browser sandbox and origin restrictions.             | Partially Untrusted Client Zone (Subject to XSS/CSRF threats).  |
| **Desktop Client (`apps/desktop`)** | Native Electron shell operating with hardened main process, context isolation, and OS secure storage.  | Semi-Trusted Client Device (Physical access / malware threats). |
| **Identity Service / Auth API**     | Authoritative backend application validating credentials, issuing sessions, and enforcing policies.    | Trusted Internal Service Zone.                                  |
| **Data Store (Database / Cache)**   | Relational database (PostgreSQL proposed) and memory cache (Redis proposed) storing identity data.     | High-Security Isolated Zone.                                    |
| **Email Delivery Provider**         | External transactional mail service (e.g., SendGrid, Postmark) used exclusively for password recovery. | External Service Zone (Egress via TLS).                         |

---

## 4. Feature Scope Matrix

| Feature Area             | MVP Scope                                                                                                                                      | Priority 1 (P1)                                                                     | Out of Scope (Future / Optional)                                      |
| :----------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------- | :-------------------------------------------------------------------- |
| **Registration**         | Direct signup via Email + Password; instant activation; no email verification link/OTP; client and server validation; password strength check. | Captcha/PoW step-up on suspicious IP spikes; blocklist of disposable email domains. | Social Sign-In (Google/GitHub OIDC); Passkey registration (WebAuthn). |
| **Login / Logout**       | Email + Password authentication; generic failure response; session issuance; single-device logout; logout-all devices.                         | Progressive login delay on repeated failed attempts; session device fingerprinting. | Multi-Factor Authentication (TOTP authenticator app); Passkey login.  |
| **Account Recovery**     | Forgot password via email reset link; 15-minute single-use token; generic response preventing user enumeration; password update.               | Security notification sent to old contact email on password change.                 | Recovery codes backup; SMS recovery; manual admin account recovery.   |
| **Profile Management**   | View profile; update display name, avatar URL, locale, and timezone; display unverified email status.                                          | Step-up re-authentication for email change; security alert to old email address.    | Account export (GDPR data takeout package).                           |
| **Session Management**   | List active sessions (device type, approximate IP location, last active timestamp); revoke individual remote session.                          | Automatic anomaly termination on geographic teleportation (impossible travel).      | Push notifications on new device login.                               |
| **Account Deletion**     | Self-service account deletion requiring current password confirmation; cascade revocation of all sessions and credentials.                     | 30-day soft-delete grace period before hard purge.                                  | Anonymized audit trail retention compliance.                          |
| **Client Secrets Vault** | Secure storage of user-provided third-party AI provider API keys (Gemini, OpenAI) with envelope encryption via backend KMS.                    | Key validation probe on external provider API upon saving.                          | Per-key granular usage limits and cost caps.                          |
