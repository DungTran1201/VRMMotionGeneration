# `diagrams/state/` — State Machine Diagrams

## Purpose
Maintains state machine diagrams capturing finite states, transition triggers, guard conditions, and action outputs.

## What Belongs Here
- Client animation player state machine (Idle, Playing, Paused, Seeking, Error).
- WebSocket streaming session state machine (Connecting, Streaming, Reconnecting, Closed).
- Avatar lifecycle state machine (Unloaded, Parsing, Rigged, Active).

## What Must NOT Belong Here
- Procedural step-by-step algorithms without explicit state states.

## Source-of-Truth Relationship
- Derived from `models/interaction/` and `docs/08-behavior/`.
