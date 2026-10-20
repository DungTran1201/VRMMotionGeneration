# `docs/09-security/` — Security & Threat Modeling

## Purpose
Documents security policies, asset upload safety guidelines, threat models, input sanitization rules, and vulnerability mitigations.

## What Belongs Here
- Threat models (e.g. STRIDE) covering user avatar uploads and motion payloads.
- Binary asset validation rules (magic byte checks, maximum size thresholds, zip-bomb protections).
- Path traversal defenses and sandbox execution policies.
- Secret management practices and access control specifications.

## What Must NOT Belong Here
- Exploitable vulnerability payloads or live secret keys.
- Vague statements without concrete mitigation rules.

## Source-of-Truth Relationship
- Canonical security rules and policies are modeled in `models/security/`.
