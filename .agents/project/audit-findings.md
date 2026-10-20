# Codebase Audit Findings

**Scope:** remote-readable source/docs of `DungTran1201/VRMMotionGeneration` on `main` as reviewed 2026-10-19. This is a repository source review, not a fresh local execution of its test suite. Re-check every item against the current working tree before implementation.

## P0 — real inference is still a stub

Evidence: `backend/src/motionbricks_vrm/source_adapter/inference_adapter.py`, especially `initialize_real_inference()` and `run_inference()`. The initialization path checks for checkpoints, imports Torch, detects a device, then sets `is_initialized=True` without constructing/loading model instances. `run_inference()` ends in `NotImplementedError`. README claims Mode B integration, but the inspected source does not execute actual model inference. The adapter must only report ready after a real loader + smoke inference + decode succeeds.

## P1 — VRM-only loading despite GLTFLoader import

Evidence: `frontend/src/avatar/vrm_manager.js` uses `GLTFLoader` and registers `VRMLoaderPlugin`, but `loadVrmUrl()` requires `gltf.userData.vrm`; it rejects assets that don't expose VRM metadata. That is not generic rigged GLB/glTF support. Extract loader adapters; retain the existing VRM path; add a GLTF path that validates `SkinnedMesh`/`Skeleton` and resolves a `SkeletonProfile`.

## P1 — canonical schema is humanoid-name restricted

Evidence: `backend/src/motionbricks_vrm/schemas/canonical_motion.py` declares a `HumanoidBoneName` enum containing the current standard humanoid bone names. That is useful for VRM, but generic rig names must be mapped to the stable canonical humanoid set or supported through an explicit custom-rig profile. Do not silently change v1 semantics. Separate source-to-canonical mapping from canonical-to-target mapping.

## P1 — retargeting quality and coverage

Evidence: `docs/05-retargeting-design.md` acknowledges G1 serial 1-DOF chains, axis differences, and lack of articulated neck/head. `docs/09-limitations-and-licensing.md` notes foot sliding and the need for foot pinning/IK. Tests should cover axis conventions, neutral/rest pose, root-motion double application, left/right symmetry, body-proportion variation and contact.

## P2 — test report is not equivalent to real model verification

Evidence: `docs/08-testing-and-validation.md` reports 24 backend tests, 4 frontend tests and a successful frontend build, but explicitly says weights were Git-LFS pointers and real inference was not measured. Keep this distinction in CI, status UI and release notes.

## P2 — repository organization

Current project already has `backend/`, `frontend/`, `configs/`, `fixtures/`, `scripts/` and `docs/`. The reference `AgentHarnessBuilderTools` uses an application/infrastructure split including `ai-backend/`, `ai-frontend/`, `ai-infra/`, `assets/`, `docs/` and `packaging/windows/`. Adopt its separation-of-concerns pattern, not cosmetic renames that break package imports. Add `infra/`, `assets/`, and `packaging/windows/` only when real content requires them.

## Recommended implementation order

1. Add and validate this `.agents` harness.
2. Fix inference lifecycle truthfulness and execute the pinned upstream loader.
3. Design loader registry + target skeleton profile; implement rigged GLB/glTF alongside VRM.
4. Strengthen retargeting/IK and synthetic integration fixtures.
5. Add secure uploads, error states, and end-to-end quality gates.
6. Migrate documentation into logical groups incrementally after preserving all links.

## Sources inspected

- https://github.com/DungTran1201/VRMMotionGeneration
- https://raw.githubusercontent.com/DungTran1201/VRMMotionGeneration/main/INSPECTION_REPORT.md
- https://raw.githubusercontent.com/DungTran1201/VRMMotionGeneration/main/backend/src/motionbricks_vrm/source_adapter/inference_adapter.py
- https://raw.githubusercontent.com/DungTran1201/VRMMotionGeneration/main/backend/src/motionbricks_vrm/schemas/canonical_motion.py
- https://raw.githubusercontent.com/DungTran1201/VRMMotionGeneration/main/frontend/src/avatar/vrm_manager.js
- https://github.com/DungTran1201/AgentHarnessBuilderTools
