# 05. Account Data Model & Schema Design

This document specifies the relational data model, entity relationships, integrity constraints, indexes, retention lifecycles, and PII classifications for the Authentication & Account Management domain.

> [!IMPORTANT]
> **Definitive Schema Constraint**: There are **zero fields, tables, or flags for email verification**. The `users` table does not contain `is_email_verified`, `email_verified_at`, or `email_verification_token`. The `email` column is explicitly classified as an unverified, self-asserted contact identifier.

---

## 1. Entity Relationship Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ACCOUNT DATA MODEL (PROPOSED)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│      ┌─────────────────────────┐           ┌─────────────────────────┐      │
│      │         users           │1         1│      user_profiles      │      │
│      ├─────────────────────────┼───────────┤─────────────────────────┤      │
│      │ PK id (UUIDv7)          │           │ PK/FK user_id (UUIDv7)  │      │
│      │    email (CITEXT)       │           │       display_name      │      │
│      │    password_hash        │           │       avatar_url        │      │
│      │    status               │           │       timezone / locale │      │
│      │    created_at           │           │       updated_at        │      │
│      │    updated_at           │           └─────────────────────────┘      │
│      └───────────┬─────────────┘                                            │
│                  │                                                          │
│                  │ 1:N                                                      │
│                  ├─────────────────────────┬───────────────────────┐        │
│                  │                         │                       │        │
│                  ▼                         ▼                       ▼        │
│      ┌───────────────────────┐ ┌───────────────────────┐ ┌────────────────┐ │
│      │       sessions        │ │ password_reset_tokens │ │user_secrets_v..│ │
│      ├───────────────────────┤ ├───────────────────────┤ ├────────────────┤ │
│      │ PK id (UUIDv7)        │ │ PK id (UUIDv7)        │ │ PK id (UUIDv7) │ │
│      │ FK user_id            │ │ FK user_id            │ │ FK user_id     │ │
│      │    token_hash (SHA256)│ │    token_hash (SHA256)│ │    provider    │ │
│      │    client_type        │ │    expires_at (15min) │ │    ciphertext  │ │
│      │    device_name        │ │    used_at            │ │    nonce / tag │ │
│      │    ip_subnet (/24)    │ │    ip_subnet (/24)    │ │    key_hint    │ │
│      │    idle_expires_at    │ │    created_at         │ │    kms_key_id  │ │
│      │    absolute_expires_at│ └───────────────────────┘ └────────────────┘ │
│      │    revoked_at         │                                              │
│      │    created_at         │                                              │
│      └───────────────────────┘                                              │
│                                                                             │
│      ┌───────────────────────────────────────────────────────────────┐      │
│      │                          audit_logs                           │      │
│      ├───────────────────────────────────────────────────────────────┤      │
│      │ PK id (UUIDv7)       user_id (FK, Nullable)  event_type       │      │
│      │    status (ENUM)     ip_subnet (/24)         metadata (JSONB) │      │
│      │    created_at                                                 │      │
│      └───────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Table Specifications & DDL Definitions

### 2.1 Table: `users`

Core identity table representing subscriber accounts.

```sql
CREATE TYPE user_account_status AS ENUM ('active', 'suspended', 'deactivated');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email CITEXT NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status user_account_status NOT NULL DEFAULT 'active',
    failed_login_attempts INT NOT NULL DEFAULT 0,
    lockout_until TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Unique constraint ensuring no two accounts share the same case-insensitive email
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);
CREATE INDEX idx_users_status ON users(status);
```

- **Attributes Analysis**:
  - `email`: Defined as `CITEXT` (PostgreSQL case-insensitive text extension) to prevent casing duplicates (e.g. `User@domain.com` vs `user@domain.com`).
  - `password_hash`: Stores Argon2id encoded string format: `$argon2id$v=19$m=65536,t=3,p=4$...`.
  - `failed_login_attempts` & `lockout_until`: Support progressive delay and temporary cooldowns.

---

### 2.2 Table: `user_profiles`

Stores presentation attributes and non-critical preferences.

```sql
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(64) NOT NULL,
    avatar_url TEXT NULL,
    locale VARCHAR(10) NOT NULL DEFAULT 'en-US',
    timezone VARCHAR(64) NOT NULL DEFAULT 'UTC',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### 2.3 Table: `sessions`

Tracks active client sessions across Web and Electron Desktop devices.

```sql
CREATE TYPE client_device_type AS ENUM ('web', 'desktop');

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL,
    client_type client_device_type NOT NULL,
    device_name VARCHAR(128) NOT NULL,
    user_agent_hash VARCHAR(64) NOT NULL,
    ip_subnet VARCHAR(45) NOT NULL,
    idle_expires_at TIMESTAMPTZ NOT NULL,
    absolute_expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Lookups by hashed session token
CREATE UNIQUE INDEX idx_sessions_token_hash ON sessions(token_hash);

-- Active session lookups per user
CREATE INDEX idx_sessions_user_active ON sessions(user_id)
WHERE revoked_at IS NULL AND idle_expires_at > NOW();
```

- **Attributes Analysis**:
  - `token_hash`: Stored as `SHA256(raw_session_token)` to prevent session hijacking if database read replicas are dumped.
  - `ip_subnet`: Anonymized IP string (e.g., `198.51.100.0/24` or `2001:db8:abcd::/48`) balancing fraud detection and user privacy.

---

### 2.4 Table: `password_reset_tokens`

Stores short-lived, single-use tokens for email-based account recovery.

```sql
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ NULL,
    ip_subnet VARCHAR(45) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_pwd_reset_token_hash ON password_reset_tokens(token_hash);
CREATE INDEX idx_pwd_reset_user ON password_reset_tokens(user_id);
```

---

### 2.5 Table: `user_secrets_vault`

Stores envelope-encrypted third-party AI provider API keys (Gemini, OpenAI, Anthropic).

```sql
CREATE TYPE ai_provider_type AS ENUM ('gemini', 'openai', 'anthropic');

CREATE TABLE user_secrets_vault (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider ai_provider_type NOT NULL,
    encrypted_dek BYTEA NOT NULL,
    ciphertext BYTEA NOT NULL,
    nonce BYTEA NOT NULL,
    tag BYTEA NOT NULL,
    kms_key_id VARCHAR(255) NOT NULL,
    key_hint VARCHAR(16) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_provider UNIQUE (user_id, provider)
);
```

---

### 2.6 Table: `audit_logs`

Records security-significant authentication and administrative events.

```sql
CREATE TYPE audit_event_status AS ENUM ('success', 'failure');

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(64) NOT NULL,
    status audit_event_status NOT NULL,
    ip_subnet VARCHAR(45) NOT NULL,
    user_agent_summary VARCHAR(128) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_event ON audit_logs(event_type, created_at);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at);
```

---

## 3. Data Retention, TTL & Purge Policies

| Table                   | Retention Policy                                                                                                 | Purge Mechanism                                                                                                                                        | Frequency |
| :---------------------- | :--------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- | :-------- |
| `password_reset_tokens` | Records expire after 15 minutes. Retained for 24 hours for audit correlation.                                    | Cron / Scheduled worker: `DELETE FROM password_reset_tokens WHERE expires_at < NOW() - INTERVAL '24 hours'`.                                           | Daily     |
| `sessions`              | Active sessions expire on idle (24h/7d) or absolute (30d/90d). Revoked sessions retained for 30 days.            | `DELETE FROM sessions WHERE (revoked_at IS NOT NULL AND revoked_at < NOW() - INTERVAL '30 days') OR absolute_expires_at < NOW() - INTERVAL '30 days'`. | Weekly    |
| `audit_logs`            | Security events retained for 90 days in primary operational database; cold-archived to encrypted object storage. | Partition rotation: Monthly partitioned tables dropped after 90 days.                                                                                  | Monthly   |
| `users` (Deactivated)   | Hard deletion executed 30 days after user self-service deletion request.                                         | Automated purge job deleting cascaded user rows.                                                                                                       | Daily     |

---

## 4. PII Classification & Privacy Matrix

| Field Name             | Entity               | PII Classification           | Sensitivity  | Protective Control                                                                             |
| :--------------------- | :------------------- | :--------------------------- | :----------- | :--------------------------------------------------------------------------------------------- |
| `users.email`          | `users`              | Direct PII                   | Medium       | Stored as self-asserted identifier. Never logged in plaintext in security monitoring logs.     |
| `users.password_hash`  | `users`              | Highly Sensitive Auth Secret | Critical     | One-way salted hash via Argon2id. Never serialized in API responses.                           |
| `sessions.ip_subnet`   | `sessions`           | Indirect PII                 | Low / Medium | Truncated to `/24` (IPv4) or `/48` (IPv6) to prevent exact geolocation tracking.               |
| `user_secrets_vault.*` | `user_secrets_vault` | Sensitive Third-Party Secret | High         | Envelope encryption (AES-256-GCM + KMS). Never returned in plaintext; only `key_hint` exposed. |
