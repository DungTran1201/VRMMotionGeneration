# `docs/06-domain/` — Domain Models & Kinematics

## Purpose
Documents core domain models: humanoid skeletal hierarchies, kinematic composition rules, coordinate systems, rotational representations, and avatar standards (VRM, glTF/GLB).

## What Belongs Here
- Canonical humanoid skeleton hierarchy specifications (bone naming, parent-child links).
- Mathematical definitions of joint rotations (quaternions, Euler angles, 6D continuous rotations).
- Retargeting algorithms and mapping tables between source topologies (e.g. robot rigs) and humanoid standards.
- Avatar format capabilities and rigging requirements.

## What Must NOT Belong Here
- Framework-specific boilerplate or HTTP web routing code.
- Binary 3D mesh files.

## Source-of-Truth Relationship
- Canonical machine-readable definitions reside in `models/domain/` and motion flow is mapped in `diagrams/data-flow/`.
