# Motion Data and Coordinate Contract

- Treat `CanonicalHumanoidMotion/v1` as the only browser-facing motion contract until a reviewed versioned migration is approved.
- Contract conventions currently documented: glTF Y-up, -Z-forward, +X-right, right-handed; meters; seconds; quaternion `[x,y,z,w]`; root transform separated from parent-local bone rotations.
- MotionBricks source convention is Y-up and +Z-forward. Convert frames mathematically and test positions, directions and rotations; do not flip random axes ad hoc.
- Keep raw source tensors and checkpoint-specific normalization in the source adapter/reconstruction layer.
- Validate finite numbers, normalized quaternions, monotonic timestamps, frame count/duration consistency, permitted bone identities, and bounded payload sizes.
- Distinguish root/world translation from hips/local rotation to avoid double-applying root motion.
- Preserve unknown/custom target skeleton details in `SkeletonProfile` or profile metadata, not by silently inserting arbitrary names into the standard humanoid enum.
- For streaming, specify timestamp semantics, frame ordering, chunk boundaries, sequence identifiers, backpressure, and how stale frames are discarded.
