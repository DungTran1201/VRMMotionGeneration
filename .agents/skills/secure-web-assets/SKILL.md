---
name: secure-web-assets
description: Review and implement safe avatar uploads and web asset handling.
---

\
# Secure Web Asset Handling

- Trace the upload from browser picker through API, temporary storage, parsing and rendering.
- Enforce byte limits, extension/content checks, resource limits and safe parse errors.
- For GLTF, normalize and validate every referenced local resource; reject path traversal, absolute paths and remote URLs unless explicitly allowed.
- Prevent archive bombs, GPU exhaustion, giant textures, excessive bones/tracks/nodes, malformed numeric transforms and long parse hangs.
- Use random server-side asset IDs and private temp folders; never trust user-provided paths.
- Do not store or log user assets unless product requirements authorize it.
- Test malicious and malformed files in isolated fixtures. Security failures should fail closed with actionable UI feedback.
