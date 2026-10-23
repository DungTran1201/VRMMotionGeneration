# 09. Quality Assurance & Security Test Plan

This document establishes the comprehensive test strategy, test case specifications, validation matrices, and acceptance criteria for verifying the Authentication & Account Management implementation.

---

## 1. Test Strategy & Scope Overview

Testing spans six distinct dimensions to guarantee functional accuracy, robust security invariants, platform parity, and defense against automated abuse:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TEST SUITE TAXONOMY                              │
├─────────────────────┬───────────────────────────────────────────────────────┤
│ 1. Functional Tests │ Happy paths, direct registration, session issuance,   │
│                     │ password reset lifecycle, profile updates.            │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 2. Negative Tests   │ Malformed payloads, expired tokens, reused tokens,    │
│                     │ duplicate emails, invalid current passwords.          │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 3. Security Tests   │ Anti-enumeration timing, brute-force progressive delay│
│                     │ CSRF enforcement, XSS token isolation, BOLA checks.   │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 4. Electron Hardening│ Sandbox enforcement, contextIsolation, safeStorage   │
│                     │ encryption verification, IPC channel allowlists.      │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 5. Cross-Platform   │ Identity sharing between Web and Desktop, multi-device│
│    Parity Tests     │ session revocation propagation.                       │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ 6. Accessibility    │ WCAG 2.1 AA keyboard flow, aria-live error regions,   │
│    & Usability      │ autofill and password manager paste validation.       │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 2. Test Case Specifications & Traceability Matrix

### 2.1 Functional Test Cases

| Test Case ID   | Target Requirement | Description                                    | Test Steps                                                                                    | Expected Result                                                                                                                                                    | Pass Criteria                                                                |
| :------------- | :----------------- | :--------------------------------------------- | :-------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------- |
| **TC-FUNC-01** | `FR-AUTH-001`      | Direct Registration without email verification | Submit `POST /api/v1/auth/register` with valid email (`user1@test.com`) and 16-char password. | 1. Account created with `status: active`.<br/>2. Zero emails dispatched in mock mailer.<br/>3. Returns HTTP 201 Created.<br/>4. User can immediately authenticate. | Database confirms `status == 'active'` and zero verification tokens created. |
| **TC-FUNC-02** | `FR-AUTH-004`      | Web Login & Cookie Issuance                    | Submit `POST /api/v1/auth/login` with correct credentials.                                    | 1. Response status is HTTP 200.<br/>2. `Set-Cookie` contains `sid` with `HttpOnly; Secure; SameSite=Lax`.<br/>3. `X-CSRF-Token` header is present.                 | Cookie attributes strictly match security baseline.                          |
| **TC-FUNC-03** | `FR-AUTH-005`      | Single Device Logout                           | Call `POST /api/v1/auth/logout` with active session.                                          | 1. Response status is HTTP 200.<br/>2. Session is marked revoked in DB.<br/>3. Subsequent request with old cookie returns HTTP 401.                                | Session record has `revoked_at != NULL`.                                     |
| **TC-FUNC-04** | `FR-ACCT-001`      | Password Reset Request (Forgot Password)       | Call `POST /api/v1/auth/forgot-password` with registered email.                               | 1. Returns generic HTTP 200 message.<br/>2. Mock mailer captures 1 email containing reset token link.<br/>3. Database stores `SHA256(token)` with 15-min TTL.      | Reset token generated and delivered; raw token not stored in DB.             |
| **TC-FUNC-05** | `FR-ACCT-002`      | Password Reset Execution                       | Call `POST /api/v1/auth/reset-password` with valid token and new 15-char password.            | 1. Returns HTTP 200 OK.<br/>2. Token marked `used_at = NOW()`.<br/>3. All pre-existing user sessions revoked.<br/>4. User can log in with new password.            | Prior session tokens return HTTP 401.                                        |

---

### 2.2 Negative & Boundary Test Cases

| Test Case ID  | Target Requirement | Description                      | Test Steps                                                                                    | Expected Result                                                | Pass Criteria                                      |
| :------------ | :----------------- | :------------------------------- | :-------------------------------------------------------------------------------------------- | :------------------------------------------------------------- | :------------------------------------------------- |
| **TC-NEG-01** | `SEC-PWD-001`      | Short Password Rejection         | Submit registration with 14-character password.                                               | HTTP 422 Unprocessable Entity with error `password_too_short`. | Account is not created.                            |
| **TC-NEG-02** | `SEC-PWD-001`      | Long Password Boundary           | Submit registration with 129-character password.                                              | HTTP 422 Unprocessable Entity with error `password_too_long`.  | Protects hashing engine against memory exhaustion. |
| **TC-NEG-03** | `FR-ACCT-002`      | Reused Reset Token               | Submit `POST /api/v1/auth/reset-password` using a token where `used_at` is already populated. | HTTP 400 Bad Request (`invalid_or_expired_token`).             | Password remains unchanged.                        |
| **TC-NEG-04** | `FR-ACCT-002`      | Expired Reset Token              | Submit reset request using a token generated 16 minutes prior.                                | HTTP 400 Bad Request (`invalid_or_expired_token`).             | Expired token rejected.                            |
| **TC-NEG-05** | `FR-ACCT-004`      | Wrong Current Password on Change | Attempt `POST /api/v1/users/me/change-password` with incorrect `currentPassword`.             | HTTP 401 Unauthorized (`invalid_current_password`).            | Password remains unchanged.                        |

---

### 2.3 Security & Anti-Abuse Test Cases

| Test Case ID  | Target Requirement | Description                         | Test Steps                                                                                                                     | Expected Result                                                                                                     | Pass Criteria                                                  |
| :------------ | :----------------- | :---------------------------------- | :----------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------- |
| **TC-SEC-01** | `FR-AUTH-002`      | Timing Attack Resistance on Login   | Measure response latency for 100 requests to `/auth/login` across: A) existing email with bad password; B) non-existent email. | Mean latency difference across both sets is `< 20ms`.                                                               | Defeats statistical timing side-channel account enumeration.   |
| **TC-SEC-02** | `SEC-RATE-001`     | Login Progressive Delay & Cooldown  | Submit 12 consecutive failed login attempts on a single account.                                                               | 1. Attempts 4-9 experience progressive delay (1s, 2s, 4s).<br/>2. Attempt 10+ triggers HTTP 429 with `Retry-After`. | Account is NOT permanently locked; temporary cooldown expires. |
| **TC-SEC-03** | `SEC-CSRF-001`     | Mutating Request without CSRF Token | Send `POST /api/v1/users/me` with valid session cookie but omitted `X-CSRF-Token`.                                             | HTTP 403 Forbidden (`csrf_validation_failed`).                                                                      | Request rejected before controller execution.                  |
| **TC-SEC-04** | `SEC-SESS-001`     | XSS Cookie Inaccessibility          | Execute `document.cookie` within sandboxed Web client context.                                                                 | `document.cookie` string does NOT contain `sid`.                                                                    | Proves `HttpOnly` protection.                                  |
| **TC-SEC-05** | `TM-08`            | BOLA / IDOR Session Revocation      | User A calls `DELETE /api/v1/users/me/sessions/{sessionIdOfUserB}`.                                                            | HTTP 404 Not Found or HTTP 403 Forbidden.                                                                           | User B's session remains active.                               |

---

### 2.4 Electron Desktop Hardening Tests

| Test Case ID   | Target Requirement | Description                       | Test Steps                                                                | Expected Result                                                                                               | Pass Criteria                                            |
| :------------- | :----------------- | :-------------------------------- | :------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------- |
| **TC-ELEC-01** | `SEC-ELEC-002`     | webPreferences Invariants         | Inspect `BrowserWindow` creation arguments in `src/main/security.ts`.     | Assert: `contextIsolation === true`, `nodeIntegration === false`, `sandbox === true`.                         | Automated Vitest spec passes (`tests/security.spec.ts`). |
| **TC-ELEC-02** | `SEC-ELEC-001`     | safeStorage Credential Encryption | Call desktop store token method, inspect `%APPDATA%/session.enc` on disk. | 1. File exists and contains high-entropy binary buffer.<br/>2. Text string of raw refresh token is NOT found. | Verified encrypted at rest via DPAPI/Keychain.           |
| **TC-ELEC-03** | `SEC-ELEC-002`     | Navigation Interception           | Attempt renderer navigation to `https://malicious-site.com`.              | Navigation blocked; external URLs routed to `shell.openExternal` after HTTPS validation.                      | Window remains on app bundle origin.                     |

---

### 2.5 Accessibility & Usability Tests

| Test Case ID   | Target Standard     | Description                       | Test Steps                                                                        | Expected Result                                                                     |
| :------------- | :------------------ | :-------------------------------- | :-------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------- |
| **TC-A11Y-01** | WCAG 2.1 AA (2.1.1) | Keyboard Navigation               | Navigate registration and login forms using only `Tab`, `Shift+Tab`, and `Enter`. | All inputs, buttons, and links receive visible focus indicators; no keyboard traps. |
| **TC-A11Y-02** | WCAG 2.1 AA (4.1.3) | Screen Reader Error Announcements | Submit an empty login form with screen reader active (NVDA/VoiceOver).            | Validation errors are announced via `aria-live="polite"` or `role="alert"`.         |
| **TC-A11Y-03** | NIST SP 800-63B-4   | Paste & Password Manager Support  | Paste a 40-character generated password into the password input field.            | Paste succeeds without interruption or truncation.                                  |
