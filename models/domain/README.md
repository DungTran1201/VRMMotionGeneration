# `models/domain/` — Domain Models

## Purpose
Maintains structured machine-readable specifications of humanoid skeletal hierarchies, joint topologies, rotational constraints, and coordinate conventions.

## What Belongs Here
- Canonical humanoid skeleton hierarchy schemas (e.g. bone name enumerations, parent-child links).
- Robot-to-humanoid retargeting mapping profiles (joint mapping rules).
- Coordinate transformation definitions.

## What Must NOT Belong Here
- Machine learning weights or raw 3D meshes.

## Source-of-Truth Relationship
- Canonical source for `docs/06-domain/` and `diagrams/data-flow/`.
