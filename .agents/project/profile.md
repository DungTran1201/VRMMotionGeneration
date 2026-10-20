# Project Profile — VRMMotionGeneration

## Verified from repository documentation/source
- Product: website that bridges NVIDIA MotionBricks motion generation with browser-based humanoid avatar rendering.
- Backend: Python package `motionbricks-vrm`, FastAPI, Pydantic v2, NumPy/SciPy, WebSocket streaming.
- Frontend: Vite, Three.js, `@pixiv/three-vrm`.
- Motion contract: `CanonicalHumanoidMotion/v1`; Y-up, glTF-style -Z forward; positions in meters; quaternion serialized `[x,y,z,w]`; root translation is separate from parent-relative bone rotations.
- Upstream source skeleton: `G1Skeleton34`; source coordinate is Y-up, +Z forward. Retargeting must account for the forward-axis conversion and the serial single-axis joint chains.
- Demo modes: fixture/offline mode and intended real MotionBricks inference mode.
- Current known blocker: `backend/src/motionbricks_vrm/source_adapter/inference_adapter.py` has a stub `run_inference()` ending in `NotImplementedError`; `initialize_real_inference()` does not actually load/execute the networks. Verify current code before relying on this statement if the repository has changed.
- Existing docs report 24 backend tests, 4 frontend tests, and a Vite build; these are reported results, not an assertion that the agent ran them in the current workspace.

## Architectural constraints
- Never couple the browser to raw MotionBricks feature vectors/checkpoint structures.
- Keep upstream NVIDIA source as a read-only reference; isolate adapters and record source revision.
- Fixture mode must remain independently usable without GPU/model weights.
- Real inference must be explicit and fail visibly if checkpoints, dependencies, or model initialization are not valid.
- Keep `backend/` and `frontend/` names unless a migration plan proves a rename is valuable; avoid breaking imports for cosmetic symmetry.

## Avatar strategy
1. First-class: `.vrm` (humanoid semantics available through VRM API).
2. First-class: rigged `.glb` and `.gltf` (must include usable skin/skeleton; `.gltf` external dependencies must be packaged and validated safely).
3. Optional later: `.fbx` after loader, bone-profile and test coverage are added.
4. Motion-source formats such as `.bvh` are not avatar mesh formats. Static mesh formats like `.obj`, `.stl`, `.ply` do not become skeletal avatars without a rigging/retargeting pipeline. USD/USDZ support is out of MVP unless explicitly scoped.

## Verification boundary
Only the actual checked-out working tree and commands run in the current task can establish current pass/fail status. Documentation alone is not execution evidence.
