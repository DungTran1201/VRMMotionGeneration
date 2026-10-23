# 03. User Flows & Use Cases

This document describes the end-to-end user flows, functional use cases, happy paths, failure conditions, and exception recovery sequences for Web and Electron Desktop clients.

---

## 1. Use Case Catalogue

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AUTHENTICATION & ACCOUNT USE CASES                 │
├─────────────────────┬───────────────────────────────────────────────────────┤
│ UC-01: Registration │ Direct signup without email verification; instant activation. │
│ UC-02: Web Login    │ Credential login with HttpOnly session cookie & CSRF token.  │
│ UC-03: Desktop Auth │ Electron native login with safeStorage / PKCE loopback.      │
│ UC-04: User Logout  │ Active session revocation and global logout-all devices.      │
│ UC-05: Password Reset│ Forgot password via unverified email link; 15-min token.     │
│ UC-06: Profile Mgmt │ View/edit profile; unverified email banner; language/theme.  │
│ UC-07: Session Mgmt │ List active devices; remote session revocation.               │
│ UC-08: Vault Secret │ Store/mask/rotate third-party AI provider API keys.           │
│ UC-09: Deletion     │ Self-service account deletion with password confirmation.     │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 2. Detailed Use Case Specifications

### UC-01: Direct User Registration (No Email Verification)

- **Primary Actor**: Guest / Anonymous User (Web or Electron Desktop).
- **Pre-conditions**: User is unauthenticated; client form is loaded.
- **Post-conditions**: User account is created with `status: active`; session is established immediately or user is redirected to login.
- **Trigger**: User clicks "Create Account" on the registration form.

#### Happy Path Sequence

1. User enters `email` and `password` (and optional `display_name`).
2. Client-side validation checks:
   - Email adheres to RFC 5322 regex.
   - Password meets NIST SP 800-63B-4 minimum length (>= 15 characters, <= 128 characters).
   - Display of advisory notice: _"Please verify your email address spelling carefully. This email will be self-asserted and unverified, and will be required for password recovery."_
3. Client dispatches `POST /api/v1/auth/register` with JSON payload.
4. Edge/Gateway rate limiter verifies request budget for client IP `/24` prefix.
5. Auth Service validates inputs against JSON Schema, normalizes email to lowercase, and checks for account existence.
6. If email is not registered:
   - Computes password hash via Argon2id (`m=64MB, t=3, p=4`).
   - Inserts record into `users` table with `status = 'active'`.
   - **Crucial Invariant**: No verification link, pin, or OTP is sent to the email address.
   - Generates new session token (CSPRNG 128-bit).
   - Stores session record in database and Redis cache.
   - Issues `HttpOnly; Secure; SameSite=Lax` cookie `sid` (Web) or returns access/refresh credentials (Desktop).
   - Dispatches `201 Created` with user profile payload.
7. Client transitions to authenticated application view.

#### Failure & Alternative Paths

- **AF-1.1: Password Policy Failure**:
  - Server returns `HTTP 422 Unprocessable Entity` with `{"error": "password_too_short", "message": "Password must be at least 15 characters long"}`.
  - Client highlights the input field with accessible inline error message.
- **AF-1.2: Email Already Registered (Anti-Enumeration)**:
  - If the email already exists in the database, the server dispatches a generic response or standard validation response: `HTTP 409 Conflict` with `{"error": "registration_failed", "message": "Unable to complete registration with the provided details. If you already have an account, please sign in."}`.
  - Server introduces an artificial timing delay matching Argon2id computation time (~100-200ms) to prevent side-channel timing analysis.
- **AF-1.3: Rate Limit Exceeded**:
  - If an IP exceeds registration limits (e.g., > 5 registrations/hour), gateway responds with `HTTP 429 Too Many Requests`, including `Retry-After: <seconds>` header.

---

### UC-02: Web User Login & Session Establishment

- **Primary Actor**: Registered User on Web Browser (`apps/web`).
- **Pre-conditions**: Account exists in `active` state; user is on `/login`.
- **Post-conditions**: Authenticated session cookie `sid` and CSRF token header are delivered; user lands on Dashboard.

#### Happy Path Sequence

1. User enters email and password, clicks "Sign In".
2. Client sends `POST /api/v1/auth/login` with JSON payload.
3. Gateway verifies rate limit for IP and normalized email.
4. Auth Service queries user by normalized email.
5. Auth Service computes Argon2id hash comparison against stored hash.
6. Upon credential match:
   - If account `status != 'active'`, returns `HTTP 403 Forbidden` (`account_suspended`).
   - Rotates/invalidates any pre-existing session token from the client to eliminate session fixation.
   - Generates a fresh 128-bit CSPRNG session identifier.
   - Stores session in database and Redis with idle TTL = 24 hours, absolute TTL = 30 days.
   - Generates a cryptographic CSRF token.
   - Sets response cookie: `Set-Cookie: sid=<token>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=2592000`.
   - Includes CSRF token in response header `X-CSRF-Token` or JSON response payload.
   - Logs successful authentication event `AUTH_LOGIN_SUCCESS` (redacting credentials).
7. Web application stores CSRF token in memory, sets authenticated state in `@vrm/app-core` store, and navigates to the application overview.

#### Failure & Alternative Paths

- **AF-2.1: Invalid Credentials**:
  - If email not found OR password mismatch:
  - Server increments failed login counter for that IP and email in Redis.
  - Returns `HTTP 401 Unauthorized` with generic message: `{"error": "invalid_credentials", "message": "Invalid email or password"}`.
  - UI displays generic failure message without specifying which field was incorrect.
- **AF-2.2: Progressive Delay / Brute-Force Throttling**:
  - After 3 consecutive failed attempts on an email or IP, server injects exponential progressive delay (1s, 2s, 4s).
  - After 10 consecutive failed attempts, server imposes a 15-minute temporary cooldown on that specific email/IP combination, returning `HTTP 429 Too Many Requests`.

---

### UC-03: Electron Desktop User Login & Secure Storage

- **Primary Actor**: Registered User on Native Desktop Client (`apps/desktop`).
- **Pre-conditions**: Electron app launched; user is unauthenticated.
- **Post-conditions**: Refresh credential encrypted via Electron `safeStorage` in user's OS credential vault; memory-only access token initialized.

#### Implementation Architecture (Native Desktop Direct Flow)

1. User opens Desktop app and enters email and password in the sandboxed renderer login view.
2. Sandboxed renderer invokes typed IPC method: `window.desktopAPI.auth.login({ email, password })`.
3. Preload script forwards payload to Electron Main Process via IPC channel `IPC_CHANNELS.AUTH_LOGIN`.
4. Main Process executes validation and initiates direct HTTPS POST to `AUTH_BASE_URL/api/v1/auth/desktop-login`.
5. Auth Service authenticates credentials and issues:
   - A short-lived Access Token (JWT, 15-minute expiry).
   - A high-entropy Refresh Token (Opaque string, 90-day expiry).
6. Main Process receives the tokens:
   - Evaluates `safeStorage.isEncryptionAvailable()`.
   - If available: Encrypts the Refresh Token buffer using `safeStorage.encryptString(refreshToken)`.
   - Writes encrypted buffer to local application data storage (`%APPDATA%/vrm-desktop/auth.dat` on Windows or OS equivalent).
   - If `safeStorage` is unavailable (e.g. headless Linux without secret-service): Emits a warning and falls back to a restricted memory-only session mode with user confirmation.
   - Keeps the Access Token in Main Process memory.
7. Main Process returns authenticated user profile to renderer via IPC.
8. Renderer updates UI state to Authenticated without ever possessing the persistent refresh token.

#### Alternative Enterprise Architecture (OAuth 2.0 PKCE via System Browser)

1. Desktop app triggers `window.desktopAPI.auth.startOAuth()`.
2. Main process creates a local HTTP loopback server on `http://127.0.0.1:<random-port>/callback`.
3. Main process generates cryptographic `code_verifier` (RFC 7636) and computes `code_challenge = BASE64URL-ENCODE(SHA256(code_verifier))`.
4. Main process delegates URL opening to external default browser: `shell.openExternal("https://auth.vrm.app/oauth/authorize?response_type=code&client_id=desktop-app&code_challenge=" + challenge + "&code_challenge_method=S256&redirect_uri=http://127.0.0.1:" + port + "/callback")`.
5. User logs in securely inside their system browser.
6. Auth server redirects to loopback callback with `?code=XYZ&state=ABC`.
7. Loopback server captures the authorization code, closes the local port, and Main process sends code + `code_verifier` directly to Auth server `/oauth/token`.
8. Tokens are exchanged and saved in `safeStorage`.

---

### UC-04: User Logout (Single-Device and Global)

- **Primary Actor**: Authenticated User.
- **Pre-conditions**: User has an active session.

#### Happy Path Sequence (Single-Device Logout)

1. User clicks "Sign Out".
2. Client sends `POST /api/v1/auth/logout`.
3. Auth Service marks current session as `revoked_at = NOW()` in database and deletes cache entry in Redis.
4. Server responds with expired session cookie (`Set-Cookie: sid=; Max-Age=0; Path=/`).
5. Desktop client clears memory access token and deletes encrypted `auth.dat` from disk.
6. Client resets store state to unauthenticated and redirects to login view.

#### Global Logout (Revoke All Devices)

1. User navigates to Account Settings -> Security -> clicks "Log Out of All Devices".
2. Client dispatches `POST /api/v1/auth/logout-all`.
3. Server updates all active sessions for `user_id`: `UPDATE sessions SET revoked_at = NOW() WHERE user_id = :id AND revoked_at IS NULL`.
4. Flushes all cached user session keys in Redis.
5. All connected Web and Electron instances are de-authenticated on their subsequent API request.

---

### UC-05: Account Recovery via Forgot Password

- **Primary Actor**: Registered User who forgot their password.
- **Pre-conditions**: User cannot log in; navigates to `/forgot-password`.
- **Important Constraint**: The recovery email is sent to the **unverified contact email** recorded at registration.

#### Happy Path Sequence

1. User inputs email address and clicks "Send Recovery Link".
2. Gateway verifies rate limit (max 3 reset requests / 15 min per email; 10 / hour per IP).
3. Client dispatches `POST /api/v1/auth/forgot-password`.
4. Auth Service queries database for normalized email:
   - If account exists and `status == 'active'`:
     - Generates 256-bit CSPRNG reset token.
     - Computes `token_hash = SHA256(raw_token)`.
     - Inserts record into `password_reset_tokens` with `expires_at = NOW() + INTERVAL '15 minutes'` and `used_at = NULL`.
     - Queues background transactional email job via Email Provider API.
     - Email contains link: `https://app.vrm.com/reset-password?token=<raw_token>`.
   - If account does NOT exist:
     - Dispatches no email, but introduces equalizing execution delay.
5. Server always responds with HTTP 200: `{"message": "If that email address is in our system, we have dispatched a password reset link to it."}`.
6. User opens email and clicks the reset link.
7. Web application renders Reset Password form, validates token format.
8. User enters new password (minimum 15 characters) and submits `POST /api/v1/auth/reset-password` with `{ token, new_password }`.
9. Auth Service computes `SHA256(token)`, checks database:
   - Verifies `token_hash` exists, `used_at IS NULL`, and `expires_at > NOW()`.
   - Computes new Argon2id hash for `new_password`.
   - Updates `users.password_hash`.
   - Marks reset token `used_at = NOW()`.
   - Revokes ALL pre-existing user sessions in database and Redis.
   - Logs `AUTH_PASSWORD_RESET_SUCCESS`.
10. Server returns `HTTP 200 OK` with `{"message": "Password updated successfully. Please log in with your new password."}`.
11. User is redirected to login view.

#### Failure & Alternative Paths

- **AF-5.1: Expired or Reused Reset Token**:
  - If token timestamp expired (> 15 min) or `used_at` is populated:
  - Server returns `HTTP 400 Bad Request` with `{"error": "invalid_or_expired_token", "message": "The password reset link has expired or has already been used. Please request a new one."}`.
- **AF-5.2: Typo at Signup Trap**:
  - If user mistyped their email during signup (e.g., `user@gmai.com`), the reset link is dispatched to `gmai.com`. The user will never receive it. This residual risk is documented in [01-business-requirements.md](file:///c:/Users/PC/Project/VRMMotionGeneration/docs/security/identity-and-account-management/01-business-requirements.md).

---

### UC-06: Profile Management & Unverified Email Display

- **Primary Actor**: Authenticated User.
- **Sequence**:
  1. User navigates to Settings -> Profile (`GET /api/v1/users/me`).
  2. UI displays:
     - Display name and Avatar URL.
     - Registered email with a persistent visual badge: **[Unverified Contact Address]**.
     - Explanatory tooltip: _"Email addresses on this platform are self-asserted and unverified. This address is used exclusively for password recovery and critical account security notices."_
  3. User edits display name or timezone, clicks "Save Changes".
  4. Client sends `PATCH /api/v1/users/me` with JSON payload.
  5. Server validates input, updates `user_profiles` table, returns updated profile.

---

### UC-07: Account Security Management (Change Password & Session Listing)

- **Primary Actor**: Authenticated User.
- **Sequence (Password Change)**:
  1. User enters `current_password`, `new_password`, and `confirm_password`.
  2. Client dispatches `POST /api/v1/users/me/change-password`.
  3. Server verifies `current_password` against stored hash using Argon2id.
  4. If invalid: returns `HTTP 401 Unauthorized` (`invalid_current_password`).
  5. If valid: validates `new_password` (>= 15 characters), computes new hash, updates database, invalidates all sessions except current session (or revokes all if requested), logs audit event.

- **Sequence (Active Session Listing & Revocation)**:
  1. User opens Settings -> Security (`GET /api/v1/users/me/sessions`).
  2. Server returns list of sessions: ID, client type (`web` / `desktop`), device user-agent preview, masked IP (`192.168.1.xxx`), created date, last active date, current session boolean flag.
  3. User clicks "Revoke" next to an unfamiliar device session.
  4. Client dispatches `DELETE /api/v1/users/me/sessions/:sessionId`.
  5. Server validates ownership of `sessionId`, marks it revoked in database, deletes Redis cache key.
  6. That remote device is terminated immediately upon its next API request.

---

### UC-08: Third-Party AI Provider API Keys Management

- **Primary Actor**: Authenticated User.
- **Sequence**:
  1. User navigates to Settings -> AI Services (`GET /api/v1/users/me/secrets`).
  2. Server returns list of stored provider keys with masked hints (e.g., `{ provider: "gemini", key_hint: "...4a2f", updated_at: "..." }`). **Plaintext key is never returned.**
  3. User adds new key: selects provider `gemini`, pastes `AIzaSy...`, clicks "Save Secret".
  4. Client sends `POST /api/v1/users/me/secrets` over HTTPS.
  5. Server uses AWS KMS / HashiCorp Vault / Cloud KMS envelope encryption:
     - Generates 256-bit Data Encryption Key (DEK).
     - Encrypts user key with AES-256-GCM using DEK.
     - Encrypts DEK using KMS Master Key.
     - Extracts masked hint (`key_hint = key.slice(-4)`).
     - Stores encrypted payload, nonce, tag, and encrypted DEK in `user_secrets_vault` table.
  6. Server returns HTTP 201 with metadata only.

---

### UC-09: Self-Service Account Deletion

- **Primary Actor**: Authenticated User.
- **Sequence**:
  1. User navigates to Settings -> Danger Zone -> clicks "Delete Account".
  2. Modal prompt requires entering `current_password` and typing `"DELETE MY ACCOUNT"`.
  3. Client dispatches `POST /api/v1/users/me/delete` with payload.
  4. Server validates password.
  5. Upon verification:
     - Cascades deletion or sets `status = 'deactivated'`.
     - Deletes all active sessions, password reset tokens, and encrypted AI provider keys.
     - Clears user session cookie.
     - Writes audit record with pseudonymized user ID.
  6. Server returns `HTTP 200 OK`.
  7. Client redirects to landing page.
