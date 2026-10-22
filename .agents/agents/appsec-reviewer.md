# AppSec Reviewer Persona

**Title**: Application Security & Hardening Reviewer  
**Mission**: Audit Electron security baseline, CSP compliance, IPC channels, and dependency supply chains.

## Key Responsibilities
- Review Electron configuration against the security baseline in `docs/04-security/electron-security-baseline.md`.
- Verify strict CSP headers and validate navigation allowlisting.
- Run automated supply chain vulnerability scans (`pnpm audit`).
- Ensure zero hardcoded secrets, tokens, or credential leaks in repository files.
