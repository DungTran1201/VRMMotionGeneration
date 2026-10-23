# 06. API Contract Specification

This document details the RESTful API contract for Authentication and Account Management across Web and Electron Desktop clients, covering endpoint specifications, error envelopes, rate limit headers, and idempotency controls.

> [!NOTE]
> **Status**: `PROPOSED`. These endpoints represent the target architecture design and are not currently deployed in runtime code.

---

## 1. Global Conventions & Standards

- **Transport**: HTTPS (TLS 1.3 mandatory; TLS 1.2 minimum).
- **Base Path**: `/api/v1`
- **Content Negotiation**: `Content-Type: application/json; charset=utf-8`
- **Date-Time Format**: ISO-8601 Extended UTC format: `YYYY-MM-DDTHH:mm:ss.sssZ`
- **Correlation Tracking**: Every request accepts or generates `X-Correlation-Id: <UUID>` propagated through logs and error payloads.
- **Standard Error Envelope**:
  ```json
  {
    "error": "invalid_credentials",
    "message": "Invalid email or password",
    "correlationId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "timestamp": "2026-10-23T15:30:00.000Z"
  }
  ```
- **Rate Limit Headers**:
  - `X-RateLimit-Limit`: Maximum requests permitted in window.
  - `X-RateLimit-Remaining`: Remaining request budget.
  - `X-RateLimit-Reset`: Unix timestamp when quota resets.
  - `Retry-After`: Seconds to wait when `HTTP 429` is emitted.

---

## 2. Authentication Endpoint Catalogue

### 2.1 Direct Registration (No Email Verification)

- **Route**: `POST /api/v1/auth/register`
- **Access**: Public
- **Idempotency**: Supports `Idempotency-Key: <UUID>`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "CorrectHorseBatteryStaple123!",
    "displayName": "Alex Chen"
  }
  ```
- **Success Response (HTTP 201 Created)**:
  ```json
  {
    "user": {
      "id": "018f291e-1234-7000-8000-000000000001",
      "email": "user@example.com",
      "status": "active",
      "emailVerified": false,
      "emailStatusNotice": "Email address is self-asserted and unverified.",
      "createdAt": "2026-10-23T15:30:00.000Z"
    },
    "profile": {
      "displayName": "Alex Chen",
      "avatarUrl": null,
      "locale": "en-US",
      "timezone": "UTC"
    }
  }
  ```
  _(For Web: Sets `Set-Cookie: sid=...; HttpOnly; Secure; SameSite=Lax`)_

---

### 2.2 Web Client Login

- **Route**: `POST /api/v1/auth/login`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "CorrectHorseBatteryStaple123!"
  }
  ```
- **Success Response (HTTP 200 OK)**:
  - **Headers**:
    - `Set-Cookie: sid=c2Vzc2lvbl90b2tlbl8xMjg=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=2592000`
    - `X-CSRF-Token: d9b7a4f8e6c2d1b...`
  - **Body**:
    ```json
    {
      "user": {
        "id": "018f291e-1234-7000-8000-000000000001",
        "email": "user@example.com",
        "status": "active",
        "emailVerified": false
      },
      "csrfToken": "d9b7a4f8e6c2d1b..."
    }
    ```

---

### 2.3 Desktop Client Direct Login

- **Route**: `POST /api/v1/auth/desktop-login`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "CorrectHorseBatteryStaple123!",
    "deviceName": "Alex-MacBookPro-Workstation"
  }
  ```
- **Success Response (HTTP 200 OK)**:
  ```json
  {
    "accessToken": "eyJhbGciOiJFUzI1NiIs...",
    "expiresIn": 900,
    "refreshToken": "rt_98fbc4e2910a4...",
    "refreshExpiresIn": 7776000,
    "user": {
      "id": "018f291e-1234-7000-8000-000000000001",
      "email": "user@example.com",
      "status": "active"
    }
  }
  ```

---

### 2.4 Desktop Token Refresh (Sliding Rotation)

- **Route**: `POST /api/v1/auth/desktop-refresh`
- **Access**: Public (requires valid refresh token)
- **Request Body**:
  ```json
  {
    "refreshToken": "rt_98fbc4e2910a4..."
  }
  ```
- **Success Response (HTTP 200 OK)**:
  ```json
  {
    "accessToken": "eyJhbGciOiJFUzI1NiIs...",
    "expiresIn": 900,
    "refreshToken": "rt_new_7a3d901bc..."
  }
  ```

---

### 2.5 User Logout

- **Route**: `POST /api/v1/auth/logout`
- **Access**: Authenticated
- **Headers**: Web: `Cookie: sid=...`, `X-CSRF-Token: ...` | Desktop: `Authorization: Bearer <token>`
- **Success Response (HTTP 200 OK)**:
  - `Set-Cookie: sid=; Path=/; Max-Age=0`
  ```json
  {
    "message": "Session terminated successfully"
  }
  ```

---

### 2.6 Global Logout (Revoke All Devices)

- **Route**: `POST /api/v1/auth/logout-all`
- **Access**: Authenticated
- **Success Response (HTTP 200 OK)**:
  ```json
  {
    "message": "All active sessions have been revoked"
  }
  ```

---

### 2.7 Forgot Password (Request Reset Link)

- **Route**: `POST /api/v1/auth/forgot-password`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Success Response (HTTP 200 OK - Generic Anti-Enumeration)**:
  ```json
  {
    "message": "If that email address is in our system, we have dispatched a password reset link to it."
  }
  ```

---

### 2.8 Reset Password Execution

- **Route**: `POST /api/v1/auth/reset-password`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "token": "raw_reset_token_from_email_link",
    "newPassword": "NewSuperSecureHorseBattery987!"
  }
  ```
- **Success Response (HTTP 200 OK)**:
  ```json
  {
    "message": "Password updated successfully. Please log in with your new password."
  }
  ```

---

## 3. Account Management Endpoint Catalogue

### 3.1 Get Current User Profile

- **Route**: `GET /api/v1/users/me`
- **Access**: Authenticated
- **Success Response (HTTP 200 OK)**:
  ```json
  {
    "id": "018f291e-1234-7000-8000-000000000001",
    "email": "user@example.com",
    "emailVerified": false,
    "emailStatusNotice": "Email is unverified. Used for password recovery.",
    "status": "active",
    "profile": {
      "displayName": "Alex Chen",
      "avatarUrl": "https://assets.vrm.app/avatars/user-1.png",
      "locale": "en-US",
      "timezone": "America/New_York"
    },
    "createdAt": "2026-10-23T15:30:00.000Z"
  }
  ```

---

### 3.2 Update User Profile

- **Route**: `PATCH /api/v1/users/me`
- **Access**: Authenticated
- **Request Body**:
  ```json
  {
    "displayName": "Alex C.",
    "timezone": "Europe/London"
  }
  ```
- **Success Response (HTTP 200 OK)**: Updated profile object.

---

### 3.3 Change Password

- **Route**: `POST /api/v1/users/me/change-password`
- **Access**: Authenticated (Requires current password verification)
- **Request Body**:
  ```json
  {
    "currentPassword": "CorrectHorseBatteryStaple123!",
    "newPassword": "BrandNewHorseBatteryStaple2026!",
    "revokeOtherSessions": true
  }
  ```
- **Success Response (HTTP 200 OK)**:
  ```json
  {
    "message": "Password updated successfully"
  }
  ```

---

### 3.4 List Active Sessions

- **Route**: `GET /api/v1/users/me/sessions`
- **Access**: Authenticated
- **Success Response (HTTP 200 OK)**:
  ```json
  {
    "sessions": [
      {
        "id": "018f291e-9999-7000-8000-000000000002",
        "clientType": "web",
        "deviceName": "Chrome 122 on Windows 11",
        "ipSubnet": "198.51.100.0/24",
        "isCurrent": true,
        "lastSeenAt": "2026-10-23T15:40:00.000Z",
        "createdAt": "2026-10-23T15:30:00.000Z"
      },
      {
        "id": "018f291e-8888-7000-8000-000000000003",
        "clientType": "desktop",
        "deviceName": "Alex-MacBookPro-Workstation",
        "ipSubnet": "203.0.113.0/24",
        "isCurrent": false,
        "lastSeenAt": "2026-10-22T19:15:00.000Z",
        "createdAt": "2026-10-18T10:00:00.000Z"
      }
    ]
  }
  ```

---

### 3.5 Revoke Remote Session

- **Route**: `DELETE /api/v1/users/me/sessions/{sessionId}`
- **Access**: Authenticated
- **Success Response (HTTP 200 OK)**:
  ```json
  {
    "message": "Session revoked successfully"
  }
  ```

---

### 3.6 Self-Service Account Deletion

- **Route**: `POST /api/v1/users/me/delete`
- **Access**: Authenticated (Requires current password verification)
- **Request Body**:
  ```json
  {
    "currentPassword": "BrandNewHorseBatteryStaple2026!",
    "confirmationPhrase": "DELETE MY ACCOUNT"
  }
  ```
- **Success Response (HTTP 200 OK)**:
  ```json
  {
    "message": "Account has been scheduled for permanent deletion"
  }
  ```

---

## 4. User Third-Party AI Provider Secrets Vault

### 4.1 List Stored Provider Secrets (Masked Metadata)

- **Route**: `GET /api/v1/users/me/secrets`
- **Access**: Authenticated
- **Success Response (HTTP 200 OK)**:
  ```json
  {
    "secrets": [
      {
        "provider": "gemini",
        "keyHint": "...4a2f",
        "createdAt": "2026-10-23T15:35:00.000Z",
        "updatedAt": "2026-10-23T15:35:00.000Z"
      }
    ]
  }
  ```

### 4.2 Save / Rotate Provider Secret

- **Route**: `POST /api/v1/users/me/secrets`
- **Access**: Authenticated
- **Request Body**:
  ```json
  {
    "provider": "gemini",
    "apiKey": "AIzaSyD_EXAMPLE_USER_SUPPLIED_SECRET_12345"
  }
  ```
- **Success Response (HTTP 201 Created)**:
  ```json
  {
    "provider": "gemini",
    "keyHint": "...2345",
    "message": "API key encrypted and securely stored"
  }
  ```

### 4.3 Delete Provider Secret

- **Route**: `DELETE /api/v1/users/me/secrets/{provider}`
- **Access**: Authenticated
- **Success Response (HTTP 200 OK)**:
  ```json
  {
    "message": "Provider key deleted"
  }
  ```
