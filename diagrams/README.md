# `diagrams/` — Visual System Projections

## Purpose
The `diagrams/` directory contains visual architectural, operational, and behavioral representations (rendered via Mermaid markdown or SVG). Diagrams are derived projections of canonical models in `models/` and narrative documentation in `docs/`.

## Critical Rule: Derived Views Only
- Diagrams are **not** sole sources of truth.
- Every diagram created here must explicitly reference its underlying source artifact(s) from `models/` or `docs/`.
- If an implementation change alters system behavior, update the canonical model first, then refresh the corresponding diagram.

## Organization
- `context/`: System context, external actors, and environmental boundary diagrams.
- `architecture/`: High-level component decomposition, layer boundaries, and structural views.
- `processes/`: Business workflows, user journeys, and operational process flows.
- `sequence/`: Synchronous and asynchronous message exchange, API calls, and streaming interactions.
- `state/`: Finite state machines for playback, streaming sessions, and loading lifecycle.
- `data-flow/`: Motion data transformation, joint representation decoding, and retargeting flows.
- `deployment/`: Container, network topology, and hosting layout diagrams.
- `ux/`: User interaction wireframes, screen transitions, and viewport layout maps.

## What Belongs Here
- Plain-text Mermaid diagram source files (`.mmd` or fenced markdown blocks) and exported vector graphics (`.svg`).
- Clear component labeling distinguishing planned vs implemented components.

## What Must NOT Belong Here
- Unreferenced diagrams that contradict canonical models.
- Proprietary binary diagram formats (e.g. Visio binaries) that cannot be reviewed via version control.
