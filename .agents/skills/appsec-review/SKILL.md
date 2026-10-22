---
name: appsec-review
description: Application security review and threat auditing
---

# AppSec Review Skill

## 1. Purpose & When to Use
Use before merging changes touching Electron configuration, IPC interfaces, dependency manifests, or network calls.

## 2. Inputs
- Electron configuration files (`frontend/apps/desktop/src/main/`).
- CSP definitions and HTML templates (`index.html`).
- Dependencies manifest (`package.json`, `pnpm-lock.yaml`).

## 3. Step-by-Step Runbook
1. **Verify WebPreferences**: Audit `contextIsolation`, `nodeIntegration`, and `sandbox`.
2. **Audit CSP**: Ensure scripts and styles are restricted and inline eval is blocked.
3. **Audit IPC Handlers**: Verify channel validation, input sanitization, and error masking.
4. **Scan Dependencies**: Run `pnpm audit` and confirm zero critical vulnerabilities.
5. **Secret Scan**: Scan staged changes for tokens, API keys, and sensitive paths.

## 4. Acceptance Criteria & Checklist
- [ ] Electron security baseline satisfied.
- [ ] No hardcoded secrets detected.
- [ ] Clean `pnpm audit` status.

## 5. Sources
- OWASP Desktop App Security Verification Standard (DASVS)
- Electron Security Checklist
