# `frontend/apps/web/` — Web Application

## Purpose
Contains the core web application implementation for the VRM motion viewer and generation interface. The specific frontend technology stack (e.g., framework, bundler) will be determined following discovery and formal ADR approval.

## What Belongs Here
- Web application entry point and component tree.
- 3D canvas and viewport integration (WebGL / Three.js / WebGPU).
- Local avatar format managers and bone inspector components.
- Playback timeline scrubber, speed controls, and mode indicators.

## What Must NOT Belong Here
- Backend server implementations or direct model weight execution.
- Direct imports or symlinks from `exp/`.
- Hardcoded mock credentials or arbitrary local file path access.

## Source-of-Truth Relationship
- Implementation conforms to `docs/10-ux/`, `models/ux/`, and `diagrams/ux/`.
