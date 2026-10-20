# Avatar Formats, Rigging, and Compatibility

## Required MVP
- `.vrm`: load with `@pixiv/three-vrm`; validate a usable humanoid rig before enabling retargeting.
- `.glb` / `.gltf`: load with Three.js `GLTFLoader`; require a valid `SkinnedMesh`/`Skeleton` for skeletal motion. A GLB can also contain only static meshes, so extension alone is not proof of animation support.
- `.gltf` may reference external buffers/textures. Validate packaged dependencies and never fetch arbitrary remote URLs without an explicit, safe allowlist.
- A target-specific `SkeletonProfile` describes source/target bone mappings, hierarchy, rest pose, primary axes, limb lengths, root/hips policy and unsupported/missing bones.
- Loader success, skeleton validity, humanoid retarget readiness, and export readiness are separate states in the UI/API.

## Optional, gated formats
- `.fbx`: only claim support after adding a supported loader, hierarchy extraction, axis/unit conversion, material/animation handling, and fixtures/tests. Consider conversion to GLB for predictable web runtime.
- `.bvh`: motion/skeleton data, not a complete avatar mesh format. Treat it as a future motion-source importer, not as equivalent to VRM.
- `.obj`, `.stl`, `.ply`: generally static geometry without a standardized humanoid skeleton. Do not offer them as directly animatable avatars unless users go through an explicit rigging/auto-rig workflow.
- `.usd` / `.usdz`: out of MVP unless an explicit compatible loader/conversion pipeline and tests are added.

## Rig mapping requirements
- Never assume all GLB files use VRM humanoid bone names.
- Inspect hierarchy, bind/rest transforms, root node, skin joints, mesh weights, scale, forward axis, bone lengths and missing bones.
- Compose G1 serial 1-DOF joints correctly before applying a rotation to human-like 3-DOF bones; do not copy raw angles by name.
- Report approximation for absent neck/head/fingers, unmapped bones and uncertain mappings.
- Do not mutate the uploaded source asset in place; create runtime transforms or derived animation tracks.
