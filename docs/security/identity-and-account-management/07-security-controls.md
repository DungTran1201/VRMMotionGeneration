# 07. Security Controls & Anti-Abuse Policy Matrix

This document defines the technical security controls, cryptographic primitives, defense-in-depth policies, and rate-limiting matrices implemented to protect the Authentication and Account Management infrastructure.

---

## 1. Cryptographic Specifications & Password Storage

### 1.1 Password Hashing Specification

In compliance with **OWASP Password Storage Cheat Sheet** and **NIST SP 800-63B-4**, passwords must never be stored in plaintext or reversible encryption.

- **Primary Algorithm**: **Argon2id** (v19).
- **Cryptographic Parameters**:
  - Memory Cost ($m$): `65536 KiB` (64 MiB).
  - Time Cost ($t$): `3` iterations.
  - Parallelism ($p$): `4` threads.
  - Salt Length: `16` bytes (128 bits) derived from a CSPRNG (`crypto.randomBytes`).
  - Output Key Length: `32` bytes (256 bits).
- **Rationale**: Argon2id provides superior resistance to both GPU-accelerated brute-force attacks (memory-hardness) and side-channel cache-timing attacks.
- **Secondary Fallback (where Argon2 is unavailable in restricted environments)**:
  - **Bcrypt**: Work factor `cost = 12` with unique 16-byte random salt.

### 1.2 NIST SP 800-63B-4 Password Policy

- **Minimum Length**: `15` characters (for single-factor authentication without mandatory MFA).
- **Maximum Length**: `128` characters (prevents DoS via computational exhaustion during hashing).
- **Character Set & Formatting**: All printable ASCII and Unicode (UTF-8) characters permitted, including spaces and emojis.
- **No Arbitrary Composition Rules**: No mandatory rules forcing uppercase, lowercase, numbers, or symbols.
- **Password Manager Friendly**: Client forms must explicitly allow paste operations and integrate with browser/OS password autofill.
- **No Arbitrary Expiration**: Passwords do not expire on arbitrary schedules; rotation is prompted only upon evidence of compromise.

---

## 2. Web Application Security Headers & Transport

All HTTP responses from the Web client and API gateway must include modern defense-in-depth headers:

```http
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://assets.vrm.app; connect-src 'self' https://auth.vrm.app https://api.vrm.app; frame-ancestors 'none'; form-action 'self'; base-uri 'self'; object-src 'none';
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
```

---

## 3. Cross-Origin Resource Sharing (CORS) & CSRF Defense

### 3.1 CORS Policy

- **Allowed Origins**: Strictly validated allowlist matching production origins:
  - `https://vrm.app`
  - `https://app.vrm.app`
  - Local dev: `http://localhost:5173` (Vite dev server)
- **No Wildcards with Credentials**: Wildcards (`*`) are prohibited. `Access-Control-Allow-Credentials: true` is enabled exclusively for explicit allowlisted origins.
- **Allowed Headers**: `Content-Type`, `X-CSRF-Token`, `X-Correlation-Id`, `Idempotency-Key`, `Authorization`.

### 3.2 CSRF Defense Architecture

1. **Cookie Configuration**: `Set-Cookie: sid=<token>; Path=/; HttpOnly; Secure; SameSite=Lax`.
2. **Synchronized CSRF Token**:
   - For all mutating HTTP methods (`POST`, `PUT`, `PATCH`, `DELETE`):
   - Client sends token in header: `X-CSRF-Token: <token>`.
   - Server validates token against session HMAC secret in Redis.

---

## 4. Multi-Layer Rate Limiting & Anti-Abuse Matrix

> [!IMPORTANT]
> **Status**: `PROPOSED INITIAL VALUES`. These thresholds are calculated for small-to-medium baseline traffic. Production deployment requires active tuning via load testing and real telemetry.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MULTI-LAYER RATE LIMITING MATRIX                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Edge / Cloudflare WAF ──► Global DDoS & IP reputation filter       │
│ Layer 2: API Gateway (Redis)   ──► Sliding-window token bucket per route/IP │
│ Layer 3: Application Service   ──► Account-level progressive delays         │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Route / Endpoint Class                          | Rate Limit Key                     | Window     | Proposed Limit (Burst)     | HTTP Status & Headers                              | Action on Repeated Abuse                                                                                                       | Distributed Implementation         |
| :---------------------------------------------- | :--------------------------------- | :--------- | :------------------------- | :------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------- | :--------------------------------- |
| **Login (`/auth/login`)**                       | IP `/24` prefix + Normalized Email | 15 Minutes | 10 attempts (Burst: 3)     | `429 Too Many Requests`<br/>`Retry-After: <sec>`   | 1. Exponential delay: 1s, 2s, 4s after 3 fails.<br/>2. 15-minute temporary cooldown after 10 fails. **No permanent lockouts**. | Redis Sliding Window Counter       |
| **Registration (`/auth/register`)**             | IP `/24` prefix                    | 1 Hour     | 5 registrations (Burst: 2) | `429 Too Many Requests`<br/>`Retry-After: 3600`    | Temporary IP block; prompt for Proof-of-Work (PoW) or Cloudflare Turnstile challenge.                                          | Redis Fixed Window with prefix key |
| **Forgot Password (`/auth/forgot-password`)**   | Normalized Email                   | 15 Minutes | 3 requests (Burst: 1)      | `200 OK` (Generic response; suppresses email send) | Email dispatch suppressed; prevents password-reset inbox flooding.                                                             | Redis Sliding Window               |
| **Forgot Password (`/auth/forgot-password`)**   | IP `/24` prefix                    | 1 Hour     | 10 requests (Burst: 3)     | `429 Too Many Requests`<br/>`Retry-After: <sec>`   | Cooldown on IP prefix to prevent mass email-bombing campaigns.                                                                 | Redis Token Bucket                 |
| **Reset Password (`/auth/reset-password`)**     | IP + Token Hash                    | 15 Minutes | 5 attempts (Burst: 2)      | `429 Too Many Requests`                            | Invalidate reset token immediately on suspicious brute-force attempts.                                                         | Redis Atomic Counter               |
| **Sensitive Profile Changes (Password/Delete)** | User ID (`session.user_id`)        | 15 Minutes | 5 attempts (Burst: 2)      | `429 Too Many Requests`                            | Re-authentication lock; require fresh login session.                                                                           | Redis User Key                     |
| **User AI Keys Vault (`/users/me/secrets`)**    | User ID                            | 1 Minute   | 10 requests (Burst: 5)     | `429 Too Many Requests`                            | Log suspicious secret manipulation to security audit.                                                                          | Redis Token Bucket                 |
| **General Authenticated APIs**                  | User ID                            | 1 Minute   | 120 requests (Burst: 30)   | `429 Too Many Requests`                            | Standard client throttling.                                                                                                    | Redis Token Bucket                 |

### 4.1 Anti-Abuse Engineering Principles

1. **Never Rely Solely on IP**: Attackers utilize distributed proxy networks and mobile carrier NATs where thousands of legitimate users share an IP. Limits must bind to normalized account identifiers and device contexts.
2. **No Permanent Account Lockouts**: Permanently locking accounts upon failed login attempts creates a trivial Denial-of-Service (DoS) vector against targeted users. Always use progressive exponential backoff delays and temporary, auto-expiring cooldowns.
3. **Equalized Timing**: All authentication and password-reset endpoints must maintain normalized response times (padding faster execution paths to match Argon2id computation) to defeat timing-based account enumeration.

---

## 5. Secrets Management & Envelope Encryption

### 5.1 Classification of Secrets

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SECRETS CLASSIFICATION                             │
├─────────────────────┬───────────────────────────────────────────────────────┤
│ Server & Infra      │ Database credentials, Session signing keys, KMS keys,  │
│ Secrets             │ Email Provider API Key. Stored in KMS / Env.          │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Client Public Config│ Base URLs, Client IDs, Public flags. (Zero secret).   │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ User AI Keys        │ User's Gemini/OpenAI API keys. Envelope encrypted     │
│ (Vaulted)           │ with AES-256-GCM + AWS KMS/Vault Master Key.          │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Session Credentials │ Web HttpOnly cookies, Electron safeStorage tokens.    │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

### 5.2 Envelope Encryption for User AI Keys

When a user provides their personal Gemini or OpenAI API key:

1. The backend requests a single-use 256-bit Data Encryption Key (DEK) from the Key Management Service (AWS KMS, HashiCorp Vault, or Google Cloud KMS):
   - KMS returns: `Plaintext DEK` and `Encrypted DEK` (wrapped by the KMS Customer Master Key).
2. Backend encrypts the user's API key:
   $$\text{Ciphertext}, \text{Nonce}, \text{AuthTag} = \text{AES-256-GCM}(\text{Plaintext DEK}, \text{API Key})$$
3. Backend securely zeros/wipes `Plaintext DEK` from memory.
4. Backend persists in `user_secrets_vault`:
   - `encrypted_dek`
   - `ciphertext`
   - `nonce`
   - `tag`
   - `kms_key_id`
   - `key_hint` (e.g. `...4a2f`, derived from the last 4 characters).
5. When the backend proxies a request to Gemini or OpenAI, it calls KMS to unwrap the DEK, performs the API call in-flight, and wipes the key immediately.

---

## 6. Logging, Telemetry & Privacy Redaction

To adhere to **OWASP Logging Cheat Sheet** and privacy standards:

1. **Strict Field Blacklist**: The logging engine must intercept and strip the following fields from all logs, error stack traces, and crash dumps:
   - `password`, `currentPassword`, `newPassword`
   - `token`, `refreshToken`, `accessToken`, `csrfToken`
   - `apiKey`, `key`, `secret`, `authorization`, `cookie`
2. **IP Address Truncation**:
   - IPv4 addresses logged as `/24` subnet: `198.51.100.123` $\to$ `198.51.100.0/24`.
   - IPv6 addresses logged as `/48` subnet: `2001:0db8:85a3:0000:0000:8a2e:0370:7334` $\to$ `2001:0db8:85a3::/48`.
3. **Structured Audit Events**:
   ```json
   {
     "timestamp": "2026-10-23T15:30:00.000Z",
     "level": "info",
     "event": "AUTH_LOGIN_SUCCESS",
     "userId": "018f291e-1234-7000-8000-000000000001",
     "clientType": "web",
     "ipSubnet": "198.51.100.0/24",
     "correlationId": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
   }
   ```
