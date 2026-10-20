# `frontend/public/` — Static Web Assets

## Purpose
Hosts static client-side web assets served directly by the web server or development bundler without transpilation.

## What Belongs Here
- Favicons, logos, and UI icons.
- Static HTML index shell and web manifests.
- Standard client-side demo fixtures (e.g., small, deterministic motion test vectors).

## What Must NOT Belong Here
- Large binary datasets or copyrighted avatar models without redistribution licenses.
- Pretrained model checkpoints or raw experiment output dumps.
- Secrets, credentials, or private configuration files.

## Source-of-Truth Relationship
- Demo fixtures stored here must strictly adhere to the schemas in `models/domain/` and `models/api/`.
