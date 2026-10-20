---
name: motion-retargeting
description: Implement and validate source-to-target skeleton mapping and motion quality.
---

\
# Motion Retargeting

1. Read the source skeleton hierarchy and coordinate conventions from the pinned source docs/code.
2. Reconstruct joint transforms with the correct matrix convention and transform composition.
3. Convert source world/local transforms into the canonical coordinate system with tests for axes and known poses.
4. Resolve source serial 1-DOF chains into target bone rotations; do not copy scalar hinge values onto spherical target joints.
5. Use target rest pose and bone directions; preserve root motion exactly once.
6. Scale translation based on measured target/source height or limb lengths; document scaling policy.
7. Use inverse kinematics/foot pinning where required, with explicit tolerance and fallback when target limbs differ.
8. Mark unsupported approximations (head/neck/fingers) rather than inventing source motion.
9. Test neutral pose, forward/backward movement, 90/180-degree turn, left/right symmetry, continuity, contact, and a different body proportion.

Report retargeting quality separately from model-generation quality.
