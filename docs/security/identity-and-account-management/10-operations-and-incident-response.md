# 10. Operations & Incident Response Runbook

This document details operational monitoring, alerting thresholds, rate-limit tuning procedures, secret rotation playbooks, and incident response runbooks for Authentication and Account Management.

---

## 1. Observability, Metrics & Telemetry

The Identity & Authentication service emits structured Prometheus metrics and OpenTelemetry traces for real-time health monitoring:

### 1.1 Core Metrics Registry

| Metric Name                      | Type      | Labels                                | Description & Purpose                                                                  |
| :------------------------------- | :-------- | :------------------------------------ | :------------------------------------------------------------------------------------- |
| `auth_requests_total`            | Counter   | `route`, `status_code`, `client_type` | Total volume of authentication endpoint traffic.                                       |
| `auth_login_failures_total`      | Counter   | `reason`, `client_type`               | Failed logins tracked by cause (`invalid_credentials`, `account_suspended`, `locked`). |
| `auth_rate_limit_exceeded_total` | Counter   | `route`, `key_type`                   | Triggers when `HTTP 429` is emitted (identifies DDoS and brute-force).                 |
| `auth_argon2_duration_seconds`   | Histogram | `operation`                           | Execution latency of Argon2id password hashing (p50, p95, p99).                        |
| `auth_active_sessions_gauge`     | Gauge     | `client_type`                         | Current active sessions cached in Redis / persisted in DB.                             |
| `auth_password_resets_total`     | Counter   | `status`                              | Outbound forgot-password events (detects reset bombing).                               |

---

## 2. Alerting Thresholds & Incident Routing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ALERT ROUTING ARCHITECTURE                            │
├─────────────────────┬───────────────────┬──────────────┬────────────────────┤
│ Alert Condition     │ Threshold         │ Severity     │ Escalation Channel │
├─────────────────────┼───────────────────┼──────────────┼────────────────────┤
│ Credential Stuffing │ Failed logins     │ CRITICAL     │ PagerDuty On-Call  │
│ Attack              │ > 100/min         │              │ + Security Slack   │
├─────────────────────┼───────────────────┼──────────────┼────────────────────┤
│ Reset Email Bombing │ Forgot-password   │ HIGH         │ Security Slack     │
│                     │ > 50/min          │              │                    │
├─────────────────────┼───────────────────┼──────────────┼────────────────────┤
│ Redis Session Cache │ Redis latency     │ CRITICAL     │ DevOps / SRE       │
│ Failure             │ > 50ms (p99)      │              │                    │
├─────────────────────┼───────────────────┼──────────────┼────────────────────┤
│ KMS Unwrapping      │ KMS decrypt fails │ HIGH         │ AppSec On-Call     │
│ Anomaly             │ > 5/min           │              │                    │
└─────────────────────┴───────────────────┴──────────────┴────────────────────┘
```

---

## 3. Rate-Limit Dynamic Tuning Procedure

When legitimate users report unexpected `HTTP 429 Too Many Requests` (e.g. from enterprise corporate NATs or university campuses):

1. **Step 1: Inspect Telemetry**:
   - Query metric: `sum(rate(auth_rate_limit_exceeded_total{route="/auth/login"}[5m])) by (ip_subnet)`.
   - Identify if the triggering prefix is a high-density NAT gateway.
2. **Step 2: Temporary Rate Limit Adjustment**:
   - Update gateway Redis configuration without service restart:
     ```bash
     # Example Redis command adjusting sliding window limit for corporate prefix
     redis-cli HSET rate_limits:custom:198.51.100.0/24 limit 50
     ```
3. **Step 3: Long-term Policy Tuning**:
   - Evaluate introducing Proof-of-Work (PoW) or Cloudflare Turnstile challenge step-up before imposing hard 429 blocks.

---

## 4. Secret & Key Rotation Playbooks

### 4.1 Web Session Cookie Signing Key Rotation

- **Frequency**: Every 90 days.
- **Procedure (Zero-Downtime Dual-Key Window)**:
  1. Generate new 256-bit secret: `SESSION_SECRET_NEW = crypto.randomBytes(32).toString('hex')`.
  2. Deploy application with both keys:
     - `SESSION_SECRET_CURRENT = SESSION_SECRET_NEW` (used to sign all new session cookies).
     - `SESSION_SECRET_FALLBACK = SESSION_SECRET_OLD` (used to accept existing active cookies).
  3. Maintain fallback key for 24 hours (matching Web idle timeout window).
  4. Remove `SESSION_SECRET_FALLBACK` in subsequent deployment.

### 4.2 KMS Master Key Rotation (User AI Keys Vault)

- **Frequency**: Annual automated rotation via Cloud KMS provider.
- **Procedure**:
  1. KMS Provider automatically generates new Customer Master Key (CMK) version.
  2. Existing ciphertext records do NOT need re-encryption immediately (KMS unwraps older versions automatically).
  3. New writes utilize the latest CMK version identifier.

---

## 5. Security Incident Response Playbooks

### 5.1 Credential Stuffing & Botnet Mitigation Runbook

- **Trigger**: Critical alert: `auth_login_failures_total > 100/min`.
- **Execution Steps**:
  1. **Identify Attack Profile**: Query access logs for common User-Agent strings, IP ranges, or credential stuffing dictionaries.
  2. **Enable Edge WAF Managed Rules**:
     - Activate Cloudflare Bot Management / WAF Managed Challenge on `/api/v1/auth/*`.
  3. **Enforce Step-Up Progressive Delay**:
     - Dynamically lower the progressive delay threshold from 3 attempts to 1 attempt across targeted subnets.
  4. **Notify Affected Accounts**:
     - For accounts experiencing > 20 failed attempts, dispatch a security alert notice to the unverified contact email advising a password update.

### 5.2 Mass Emergency Session Revocation

- **Trigger**: Detection of database read replica compromise or critical session signing key leakage.
- **Execution Steps**:
  1. Execute administrative global revocation script:
     ```sql
     -- Database command terminating all active user sessions
     UPDATE sessions SET revoked_at = NOW() WHERE revoked_at IS NULL;
     ```
  2. Flush Redis session cache:
     ```bash
     redis-cli --scan --pattern "session:*" | xargs redis-cli del
     ```
  3. Invalidate current session signing keys and redeploy service.
  4. Force all Web and Electron Desktop clients to re-authenticate.

### 5.3 Data Breach Incident Response & Notification Protocol

In the event of confirmed unauthorized access to identity data:

1. **Containment**: Isolate affected database read replicas and rotate all master credentials within 1 hour.
2. **Forensic Audit**: Analyze `audit_logs` to delineate exact rows exfiltrated.
3. **Regulatory Disclosure**: If PII (emails or hashed passwords) is compromised, initiate GDPR/CCPA notification procedures within the statutory 72-hour window.
