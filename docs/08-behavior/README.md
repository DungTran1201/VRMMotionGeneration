# `docs/08-behavior/` — System Behavior & State Transitions

## Purpose
Documents system dynamic behavior, lifecycle transitions, animation playback timing, streaming buffer policies, and operational mode states.

## What Belongs Here
- State transition specifications for playback (Idle, Loading, Playing, Paused, Error).
- Mode switching rules (Mode A: Fixture Demo vs. Mode B: Real Inference).
- Frame rate timing, interpolation windows, and clock synchronization semantics.
- Error recovery and graceful degradation behaviors.

## What Must NOT Belong Here
- Static data models or database schemas.
- Ephemeral runtime log traces.

## Source-of-Truth Relationship
- Modeled structurally in `models/interaction/` and visually rendered in `diagrams/state/`.
