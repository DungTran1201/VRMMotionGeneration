# `models/security/` — Security Policy Models

## Purpose
Maintains structured machine-readable security policies, input validation rules, file upload limits, and authorization constraints.

## What Belongs Here
- File upload validation schemas (permitted MIME types, magic numbers, max file sizes).
- Threat modeling taxonomy (STRIDE mapping) in structured format.
- CORS policy and header requirements.

## What Must NOT Belong Here
- Concrete private keys, passwords, or production secrets.

## Source-of-Truth Relationship
- Canonical source for `docs/09-security/`.
