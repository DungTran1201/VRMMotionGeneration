# 11. Decisions & Open Questions (ADR Summary)

This document formalizes the Architecture Decision Records (ADR), architectural trade-off evaluations, and unresolved open questions requiring formal sign-off from the Product Owner and Security Owner.

---

## 1. Architecture Decision Records (ADR) Summary

| Decision ID     | Title                                                                           | Status                          | Primary Rationale                                                                                                                          | Trade-Off / Consequence                                                                                         | Reference                                    |
| :-------------- | :------------------------------------------------------------------------------ | :------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------- | :------------------------------------------- |
| **ADR-SEC-001** | **Strict Elimination of Email Verification Gate**                               | **DECIDED** _(Product Mandate)_ | Zero signup friction; instant user activation; independent from transactional email delivery reliability.                                  | **Risk**: Unverified accounts, potential account squatting, typo-induced lockout on password recovery.          | Product Decision                             |
| **ADR-SEC-002** | **Bifurcated Session Architecture**<br/>(Web Cookie BFF vs Desktop safeStorage) | **PROPOSED**                    | Mitigates XSS token theft on Web via `HttpOnly` cookies; enables persistent offline-tolerant desktop credentials via OS-backed encryption. | Requires maintaining two transport strategies (Cookie vs Bearer) in backend middleware.                         | RFC 10017<br/>Electron safeStorage           |
| **ADR-SEC-003** | **Password Storage via Argon2id**                                               | **PROPOSED**                    | Superior resistance against GPU/ASIC brute-force and side-channel cache attacks compared to SHA/MD5/Bcrypt.                                | Higher server CPU/memory footprint (~64MB per hash); requires concurrency limits on auth workers.               | NIST SP 800-63B-4<br/>OWASP Password Storage |
| **ADR-SEC-004** | **Envelope Encryption for User AI Keys**                                        | **PROPOSED**                    | Guarantees third-party provider keys (Gemini, OpenAI) are unreadable even if relational database read replicas are fully exfiltrated.      | Requires integration with cloud KMS (AWS KMS, GCP KMS, or HashiCorp Vault); latency overhead on key unwrapping. | OWASP Secrets Mgmt                           |
| **ADR-SEC-005** | **Multi-Layer Distributed Rate Limiting**                                       | **PROPOSED**                    | Protects endpoints from credential stuffing, DoS, and email bombing without relying solely on client IP addresses.                         | Requires distributed cache infrastructure (Redis); potential false positives on shared corporate NATs.          | OWASP Abuse Case                             |

---

## 2. In-Depth Trade-Off Evaluations

### 2.1 Trade-Off: Unverified Email vs Account Integrity

- **Option A (Chosen)**: Email as primary login identifier without verification.
  - _Pros_: Zero onboarding latency, zero dependency on third-party mailer deliverability for signups.
  - _Cons_: An attacker can register `target@company.com`. The true owner is blocked from registering that address until a dispute workflow is invoked. If a user mistypes their email, forgotten passwords cannot be reset.
- **Option B (Alternative)**: Username as primary identifier (`@username`) + optional unverified contact email.
  - _Pros_: Completely eliminates email squatting as a login barrier.
  - _Cons_: Higher UX friction (username availability checks, remembering unique handles).

### 2.2 Trade-Off: Electron Direct Auth vs External Browser OAuth

- **Option 1 (Direct Auth via IPC Preload — Baseline)**:
  - _Pros_: Clean, native UI within the Electron window; frictionless user experience.
  - _Cons_: Desktop app directly handles user password strings in main process memory.
- **Option 2 (OAuth 2.0 PKCE via System Browser — RFC 8252 Enterprise Pattern)**:
  - _Pros_: User authenticates in their trusted browser (leveraging existing web sessions and password managers); app binary never sees plaintext passwords.
  - _Cons_: Window switching friction; requires handling local loopback HTTP server or OS custom protocol registration (`vrm-app://`).

---

## 3. Open Questions for Stakeholder Approval

| Question ID | Stakeholder     | Question & Context                                                                                                                                                           | Proposed Recommendation                                                                                                                                                                | Approval Status |
| :---------- | :-------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------- |
| **OQ-01**   | Product Owner   | **Account Reclamation / Squatting Dispute Policy**: How should the platform handle a legitimate owner who wishes to claim an email squatted by someone else?                 | Implement a manual support ticket reclamation workflow (P1) where the legitimate owner proves domain control or email ownership.                                                       | `OPEN QUESTION` |
| **OQ-02**   | Security Owner  | **Email Address Modification Policy**: When a user changes their email address in profile settings, should we dispatch a security alert to the OLD email address?            | **Yes (Recommended)**. Dispatch an immediate security notice to the prior email stating that the account contact address was modified, with a link to revoke sessions if unauthorized. | `OPEN QUESTION` |
| **OQ-03**   | Product Owner   | **Third-Party Social Login (Google / GitHub)**: Should social login be prioritized for MVP or deferred to P1?                                                                | Defer to P1. Direct email/password satisfies core foundation needs with lower initial dependency complexity.                                                                           | `OPEN QUESTION` |
| **OQ-04**   | Legal / Privacy | **Account Deletion Retention Window**: Should self-service account deletion execute immediately (hard delete) or enter a 30-day soft-delete grace period?                    | 30-day soft-delete grace period with immediate session revocation (allows users to cancel accidental deletion within 30 days).                                                         | `OPEN QUESTION` |
| **OQ-05**   | DevOps / SRE    | **Production Redis High-Availability**: Should Redis be deployed as a managed cluster (AWS ElastiCache / Redis Enterprise) to guarantee 99.9% uptime for session validation? | Mandate managed multi-AZ Redis with automatic failover to prevent session validation outages.                                                                                          | `OPEN QUESTION` |
