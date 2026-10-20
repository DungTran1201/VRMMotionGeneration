# Code Style and Dependency Rules

- Python: type hints for public functions; small pure math functions where possible; explicit errors; avoid global mutable state; use structured logging and deterministic tests.
- TypeScript/JavaScript: prefer typed interfaces for canonical payloads and skeleton profiles; centralize coordinate math; dispose Three.js resources; do not write every feature into `main.js`.
- Keep dependency versions constrained and explain new large/native dependencies. Avoid installing packages at runtime.
- No raw `except: pass`, ignored failed promises, console spam in production, or hidden automatic mode fallbacks.
- Avoid duplicated schema implementations drifting between Python and TypeScript; provide fixtures/shared test vectors or generated types where feasible.
- All configs should have safe defaults and explicit environment-variable overrides. Never place machine-specific absolute paths in committed defaults.
