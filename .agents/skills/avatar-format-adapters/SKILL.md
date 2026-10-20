---
name: avatar-format-adapters
description: Add avatar format support through capability-based loaders and rig validation.
---

\
# Avatar Format Adapters

## MVP priorities
1. VRM using `@pixiv/three-vrm` and its humanoid APIs.
2. Rigged GLB/glTF using Three.js `GLTFLoader` and a validated skin/skeleton.
3. FBX only as a later optional adapter with separate tests.

## Design
- Use a registry/adapter boundary such as `AvatarLoaderAdapter` with `canLoad`, `load`, `inspectRig`, `getCapabilities`, `dispose` and structured errors.
- Return a common `LoadedAvatar` but retain format-specific metadata and capabilities; do not erase the distinction between VRM semantics and generic glTF skeletons.
- Inspect `SkinnedMesh`, skeleton joints, rest/bind pose, scale, root, hierarchy, bone lengths, forward axis and animation clips.
- Distinguish `loaded`, `rigged`, `retargetReady` and `exportReady` states.
- For generic GLB, map skeletons through a user-editable `SkeletonProfile`; don't assume bone names match VRM.
- Treat `.gltf` dependency URLs and upload paths as untrusted; sandbox local dependencies and block arbitrary remote fetches by default.
- Reject unsupported formats with clear UI messages. A static OBJ mesh is not an animated humanoid.

## Acceptance
- Tests for valid VRM, valid rigged GLB, unrigged GLB, missing/invalid skeleton, unknown bone names, bad file, and cleanup after switching avatar.
- At least one synthetic or permissively licensed fixture, not a private user avatar.
