# `diagrams/sequence/` — Sequence Diagrams

## Purpose
Maintains UML sequence diagrams modeling chronological message exchanges across system boundaries.

## What Belongs Here
- Mode A (fixture) playback initialization sequence.
- Mode B (real inference) WebSocket streaming and frame delivery sequence.
- Client-side avatar loading and bone retargeting sequence.

## What Must NOT Belong Here
- Static component hierarchies without temporal interaction.

## Source-of-Truth Relationship
- Derived from `models/interaction/`, `models/api/`, and `docs/07-api/`.
