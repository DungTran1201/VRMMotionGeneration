# ADR-0003: Bifurcated Session and CSRF Defense Architecture

- **Status**: Accepted
- **Deciders**: Operation Dev, Security Lead
- **Date**: 2026-10-23
- **Technical Context**: Designing secure session management and token handling for Web and Electron Desktop clients.

---

## 1. Context and Problem Statement

Web browsers and native Electron desktop applications possess fundamentally different security boundaries and storage capabilities:
1. **Web Browsers**: Subject to Cross-Site Scripting (XSS) attacks. If authentication tokens are stored in `localStorage` or `sessionStorage`, an injected script can immediately exfiltrate full credentials.
2. **Electron Desktop**: Runs in an operating system process. The sandboxed renderer must not have direct filesystem or Node API access, but the host process can leverage hardware-backed or OS-backed credential vaults (Windows DPAPI, macOS Keychain).

---

## 2. Considered Alternatives

### Alternative 1: Uniform Bearer Tokens in `localStorage`
- *Cons*: Severe security vulnerability on the Web (RFC 10017 violation). Fails OWASP ASVS Level 2 requirements.

### Alternative 2: Uniform Cookie-Based Authentication
- *Cons*: Electron native requests from Node main process would have to maintain a manual cookie jar, complicating cross-process token refresh and offline capability.

### Alternative 3: Bifurcated Architecture (Web Cookie BFF vs Desktop safeStorage Hybrid Bearer) (Selected)
- *Web Client*: Relies on server-managed `HttpOnly; Secure; SameSite=Lax` cookies. JavaScript cannot access the session token. State-changing requests validate a synchronized `X-CSRF-Token` header.
- *Electron Desktop*: Uses short-lived Access Tokens (15 min) in memory and long-lived Refresh Tokens encrypted via Electron `safeStorage`. Preload script exposes typed methods; renderer never holds raw persistent tokens.

---

## 3. Decision Outcome

**Selected Option:** Adopt the bifurcated session model in compliance with RFC 10017, RFC 8252, and OWASP Session Management guidelines.
