# 01 - System Requirements Specification

## 1. Executive Summary & Goals

The objective of this project is to build an architectural bridge and working proof-of-concept (PoC) integrating NVIDIA's **MotionBricks** real-time generative humanoid motion model with the **VRM (Virtual Reality Model)** 3D avatar standard.

### Goals
- Analyze the official upstream MotionBricks code from `NVlabs/GR00T-WholeBodyControl` to identify the genuine inference pipeline and feature representations.
- Specify and implement **`CanonicalHumanoidMotion/v1`**, a model-independent, rendering-engine-agnostic canonical humanoid motion contract.
- Build a robust G1-to-Humanoid adapter that reconstructs the 34-joint Unitree G1 robot hierarchy and retargets serial hinge joints into standard VRM humanoid bones.
- Deliver an interactive, high-aesthetic 3D web viewer using Three.js and `@pixiv/three-vrm` supporting local VRM file loading, bone inspection, and playback controls.
- Provide two explicit operating modes:
  - **Mode A (Fixture / Offline Demo):** 100% functional without GPU, PyTorch, or pretrained weights.
  - **Mode B (Real MotionBricks Inference):** Connects to the genuine inference pipeline when checkpoints and dependencies are available.

### Non-Goals
- Training or fine-tuning MotionBricks neural networks.
- Implementing speech recognition (ASR), large language models (LLM), or camera pose estimation.
- Redistributing copyrighted, commercial, or unlicensed VRM avatars or multi-gigabyte proprietary checkpoint binaries.
- Building a full non-linear 3D keyframe animation editor.

---

## 2. User Stories & Use Cases

1. **3D Avatar Developer (Offline Verification):**
   - *As a 3D web developer*, I want to open the viewer in my browser and test humanoid animations on my VRM model without installing CUDA, PyTorch, or downloading 2+ GB weights.
2. **AI / Robotics Researcher (Integration & Diagnostics):**
   - *As a robotics researcher*, I want to inspect how MotionBricks G1 joint features map to human skeletal kinematics and verify joint orientations and foot contacts.
3. **Backend / Graphics Engineer (System Extensibility):**
   - *As a backend engineer*, I want an engine-independent canonical JSON contract so that future generative motion models (e.g., SMPL-based or diffusion models) can feed the same VRM viewer without rewriting the frontend.

---

## 3. Functional Requirements

| ID | Requirement | Implementation Status |
|---|---|---|
| **FR-01** | Strict validation of `CanonicalHumanoidMotion/v1` documents (quaternion norms, timestamps, schema version). | Implemented via Pydantic v2 and TypeScript/JS validator. |
| **FR-02** | Decoding of 414-dimensional MotionBricks feature tensors into root transforms, 6D continuous rotations, and joint positions. | Implemented in `G1SkeletonReconstructor`. |
| **FR-03** | Mathematical retargeting of G1 serial hinge joints (hip, waist, shoulder, wrist) to 3-DOF spherical humanoid bones. | Implemented in `G1ToHumanoidRetargeter`. |
| **FR-04** | Explicit coordinate system conversion from MotionBricks (+Z forward, +Y up) to Canonical glTF/VRM (-Z forward, +Y up). | Implemented via $R_Y(180^\circ)$ involutive transformation. |
| **FR-05** | Browser 3D viewport rendering VRM avatars and procedural humanoid mannequins with orbit controls and lighting. | Implemented in Three.js + `@pixiv/three-vrm`. |
| **FR-06** | Local loading of custom `.vrm` files with humanoid bone coverage checklist. | Implemented in `AvatarManager`. |
| **FR-07** | Timeline controls: play/pause, seek scrubber, restart, speed scaling (0.25x - 2.0x), and loop toggle. | Implemented in `AnimationPlayer`. |
| **FR-08** | Two distinct operating modes: Mode A (Offline Fixture) and Mode B (Real Inference) with explicit badges and zero silent fallbacks. | Implemented across frontend UI and FastAPI backend. |
| **FR-09** | REST API endpoints for health, schema, validation, retargeting, and WebSocket streaming. | Implemented in `app.py`. |

---

## 4. Non-Functional Requirements

- **Performance:** Frontend render loop decoupled from network streaming; maintains 60+ FPS via slerp interpolation.
- **Portability:** Backend runs on Python 3.9 - 3.12 across Windows and Linux; frontend runs in all modern WebGL2-compatible browsers.
- **Change Safety:** Zero modifications to upstream MotionBricks code. Checkpoint presence verified dynamically.
- **Aesthetics:** Dark modern technical UI with glassmorphism panels, Inter/JetBrains Mono typography, and responsive dock layout.

---

## 5. Definition of Ready (DoR) and Definition of Done (DoD)

### Definition of Ready
1. Upstream source repository inspected and verified.
2. Tensor dimensions, coordinate conventions, and skeleton hierarchies documented from code.
3. Package compatibility for Three.js and `@pixiv/three-vrm` verified.

### Definition of Done
1. Canonical schema defined with automated validation tests.
2. Source adapter and retargeting engine implemented with unit tests.
3. 3D WebGL viewer verified in browser with both procedural and custom VRM avatars.
4. Two distinct operating modes implemented and verified.
5. All 9 technical documentation documents and 7 Mermaid diagrams authored and checked.
6. Full test suite passing with 100% success rate.
