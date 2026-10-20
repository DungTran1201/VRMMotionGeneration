# `diagrams/data-flow/` — Data Flow Diagrams

## Purpose
Maintains diagrams depicting the pipeline transformation of motion data from latent representations through kinematic composition to rendered vertices.

## What Belongs Here
- Motion pipeline flowcharts: latent vector -> 6D rotation -> G1 forward kinematics -> spherical humanoid joints -> VRM bones.
- User input upload -> binary validation -> local buffer streaming.

## What Must NOT Belong Here
- Physical server deployment diagrams.

## Source-of-Truth Relationship
- Derived from `models/domain/` and `docs/06-domain/`.
