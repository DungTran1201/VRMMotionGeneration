# Repository Inspection and Baseline Environment Report

**Date:** 2026-10-18  
**Project:** MotionBricks-to-VRM Integration Prototype  
**Workspace:** `c:\Users\PC\Project\VRMMotionGeneration`  
**Upstream Reference Repository:** `https://github.com/NVlabs/GR00T-WholeBodyControl.git`  
**Upstream Commit SHA:** `45c03facbf848e0c743091b7d9c17952096ff908` (Merge pull request #276)

---

## 1. Workspace and Git Status

- **Local Working Tree:** Clean on branch `main`, tracking `origin/main` (`https://github.com/DungTran1201/VRMMotionGeneration.git`).
- **Initial Commit:** `8c0db74 Initial commit`.
- **Existing User Files:** `.git`, `.gitignore`, `README.md`. No user uncommitted changes exist.
- **Change-Safety Policy:** All upstream MotionBricks code from `NVlabs/GR00T-WholeBodyControl` is treated as **read-only reference**. The integration code, schemas, adapters, API server, frontend viewer, tests, and documentation are isolated within `c:\Users\PC\Project\VRMMotionGeneration`.

---

## 2. Licenses Verified

- **Source Code License:** **Apache License 2.0** (Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES). Permits modification, commercial use, and distribution with attribution.
- **Model Checkpoints License:** **NVIDIA Open Model License** (Last Modified: October 24, 2025). Grants royalty-free permission to use, distribute, and create derivative models subject to trustworthy AI conditions and non-infringement terms.
- **VRM Assets Policy:** No proprietary or unlicensed VRM model assets are added to the repository. The viewer supports local user-uploaded `.vrm` avatars and includes a procedural fallback rig.

---

## 3. Environment & Runtime Inspection

| Component | Detected Version | Status / Notes |
|---|---|---|
| **OS** | Windows 11 (64-bit) | PowerShell shell execution |
| **Python 3.12** | 3.12.9 (64-bit) | FastAPI, Uvicorn, Pydantic, NumPy 2.5, SciPy 1.18, PyYAML, WebSockets, PyTest installed |
| **Python 3.9** | 3.9 (64-bit) | PyTorch 2.8.0+cpu, Torchvision, Scipy, NumPy installed |
| **Node.js** | v24.18.0 | Verified for Vite frontend tooling |
| **npm** | 11.16.0 | Verified for package management |
| **GPU / Driver** | NVIDIA GeForce GTX 1650 (4 GB VRAM), Driver 591.74 | CUDA 13.1 supported by driver; limited VRAM (4 GB) |
| **Pretrained Weights** | Git LFS pointers in upstream repository | `model-step=2000000.ckpt` is ~1.6 GB (LFS pointer 135 bytes). Offline/Fixture Mode is required and prioritized; Real Inference Mode is implemented with explicit availability checks. |

---

## 4. Upstream MotionBricks Architecture Findings

1. **Output Representation (`DualRootGlobalJoints`):**
   - **Global subset (414 dims):** Used by the root model and data loader.
     - `global_root_pos` (3 dims): World XYZ position (meters). Coordinate space: Y-up, Z-forward, X-right.
     - `global_root_heading` (2 dims): $(\cos\theta, \sin\theta)$ around Y.
     - `ric_data` (99 dims): 33 non-root joints $\times$ 3D positions with per-frame projected root XZ subtracted.
     - `global_rot_data` (204 dims): 34 joints $\times$ continuous 6D rotation matrices in world frame.
     - `local_vel` (102 dims): 34 joints $\times$ world-frame velocities.
     - `foot_contacts` (4 dims): Binary contact flags (left ankle, left toe, right ankle, right toe).
   - **Local subset (413 dims):** Used by the pose tokenizer/backbone.
     - `local_root_rot_vel` (1 dim): Angular velocity around Y.
     - `local_root_vel` (2 dims): XZ translational velocity in heading-aligned frame.
     - `global_root_y` (1 dim): Root height.
     - Same 409 body features as global representation.

2. **Kinematic Hierarchy (`G1Skeleton34`):**
   - 34 joints total: 32 active joints from Unitree G1 robot + 2 dummy toe joints (`left_toe_base`, `right_toe_base`).
   - Root: `pelvis_skel` (index 0).
   - Serial 1-DOF hinge joints are chained (e.g., `left_hip_pitch` $\rightarrow$ `left_hip_roll` $\rightarrow$ `left_hip_yaw`), which must be composed into 3-DOF spherical humanoid bone transforms during retargeting.

3. **Coordinate Systems:**
   - **MotionBricks:** Y-up, +Z forward, +X right (Right-handed).
   - **VRM / glTF:** Y-up, -Z forward, +X right (Right-handed).
   - **MuJoCo:** Z-up, +X forward, +Y left (Right-handed).

---

## 5. Implementation Strategy & Next Steps

1. **Step 1:** Establish clean project structure (`backend/`, `frontend/`, `docs/`, `configs/`, `fixtures/`, `scripts/`).
2. **Step 2:** Formulate `CanonicalHumanoidMotion/v1` formal schema and Pydantic validation models.
3. **Step 3:** Implement G1-to-Humanoid adapter with 6D-to-matrix, coordinate transformation, and hierarchical retargeting.
4. **Step 4:** Generate and validate deterministic fixture `fixtures/sample_motion.json`.
5. **Step 5:** Build FastAPI backend service with health, schema, validation, retargeting, and WebSocket streaming.
6. **Step 6:** Build modern Three.js + `@pixiv/three-vrm` web client with dual-mode support, humanoid inspector, and playback controls.
7. **Step 7:** Write comprehensive technical documentation (01 to 09) and 7 Mermaid architecture diagrams.
8. **Step 8:** Run backend and frontend automated test suites, document observed metrics, and deliver final implementation report.
