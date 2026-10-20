# Web Security and Asset Upload Safety

- Treat all prompts, uploaded files, GLB/glTF metadata, node names, material strings and external URIs as untrusted input.
- Enforce extension allowlists and inspect file signatures/content, maximum file size, decompression/resource limits, texture dimensions, node/bone counts, animation-track counts and parse timeouts.
- Never accept a server filesystem path from the client. Do not concatenate user-supplied filenames into paths; use generated IDs and isolated temporary directories.
- For `.gltf` packages, reject path traversal, absolute paths and arbitrary remote URIs by default; ensure referenced buffers/images remain inside the upload sandbox.
- Avoid SSRF from loader/network fetches, unsafe deserialization, code execution in model files, archive bombs and GPU/CPU denial of service.
- Keep user assets local to the session unless persistent storage is explicitly required. Do not log uploaded binary content or secrets.
- Never commit `.env`, API keys, personal avatar files without permission, pretrained checkpoints or huge generated assets. `.env.example` must contain placeholders only.
- Escape user-controlled labels and error details in the UI. Use explicit CORS/origin policy, upload rate limits, WebSocket session checks, and safe error responses.
