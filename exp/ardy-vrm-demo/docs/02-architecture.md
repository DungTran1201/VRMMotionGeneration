# System Architecture & Boundaries

**Document ID:** `exp/ardy-vrm-demo/docs/02-architecture.md`  
**Classification:** `VERIFIED`  
**Author:** Operation Dev  
**Date:** October 20, 2026  

---

## 1. Product Boundaries & Strict Isolation

In compliance with the repository Operating Contract in `AGENTS.md`:
- **Production Scope:** Root directories (`frontend/`, `backend/`, `infra/`, `models/`, `docs/`) remain untouched and uncoupled.
- **Experiment Boundary:** All demo assets reside exclusively within `exp/ardy-vrm-demo/`.
- **Zero Runtime Dependencies:** No module in `exp/ardy-vrm-demo/` imports or links to root application files. The experiment operates completely stand-alone with its own Python environment (`.venv`), dependencies, backend server, frontend UI, tests, scripts, and documentation.

---

## 2. Component Decomposition

```
+-----------------------------------------------------------------------------------------------------+
|                                          exp/ardy-vrm-demo/                                         |
|                                                                                                     |
|  +-----------------------------------------------------------------------------------------------+  |
|  |                                  Frontend (Browser Client)                                    |  |
|  |  - HTML/CSS: Modern Cybernetic HUD (index.html, index.css)                                     |  |
|  |  - 3D Viewport 1: CoreSkeleton27 LineSegments & Joint Spheres (Three.js)                      |  |
|  |  - 3D Viewport 2: VRM 1.0 Humanoid Normalized Bone Retargeting (@pixiv/three-vrm)             |  |
|  |  - Timeline Engine: Frame-synchronized dual playback, seek, loop, restart                     |  |
|  |  - Telemetry HUD: Real-time rendering FPS, RTF, generation latency, VRAM                       |  |
|  +----------------------------------------------+------------------------------------------------+  |
|                                                 | REST + WebSocket Events                           |
|  +----------------------------------------------v------------------------------------------------+  |
|  |                                  FastAPI Backend Server                                       |  |
|  |  - api.py: REST Endpoints (/api/health, /api/models, /api/generations, /api/samples/default)   |  |
|  |  - job_manager.py: Asynchronous queue, concurrency throttle (1 GPU job max), cancel handling  |  |
|  |  - WebSocket: Real-time generation progress and streaming telemetry broadcaster               |  |
|  +----------------------------------------------+------------------------------------------------+  |
|                                                 | Conditioning Tensors [B, 32, 4096]                |
|  +----------------------------------------------v------------------------------------------------+  |
|  |                                   ARDY Runtime Adapter                                        |  |
|  |  - DecoupledTextEncoder: Natural language semantic mapping to 4096-dim condition space        |  |
|  |  - ArdyEngine: Model lifecycle, CUDA device management, monotonic benchmarking timers        |  |
|  |  - Upstream ARDY Denoiser: Flow matching transformer diffusion on GPU (PyTorch 2.6 CUDA)      |  |
|  |  - Upstream Tokenizer: Autoencoding latent dequantization to rotation matrices               |  |
|  +----------------------------------------------+------------------------------------------------+  |
|                                                 | 3x3 Rotations [T, 27, 3, 3] + Root [T, 3]        |
|  +----------------------------------------------v------------------------------------------------+  |
|  |                             Motion Adapter & Kinematics Engine                                |  |
|  |  - core_skeleton.py: CoreSkeleton27 joint hierarchy, parent indices, Forward Kinematics       |  |
|  |  - vrm_retargeter.py: Matrix-to-quaternion mapping, sign continuity check, VRM 1.0 retargeting  |  |
|  |  - schemas.py: UnifiedMotionPayload serialization with strict coordinate validation           |  |
|  +-----------------------------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------------------------+
```

---

## 3. Data Flow Overview

1. **User Prompt Submission:** User inputs a prompt (or chooses one of 4 presets) and configures duration (0.5s–10.0s).
2. **Job Scheduling:** Frontend posts to `POST /api/generations`, which creates a background task and returns `job_id`.
3. **Conditioning:** Text is projected into 4096-dimensional condition features.
4. **Diffusion Execution:** Real ARDY Flow Matching Denoiser runs iterative denoising on GPU (`cuda:0`).
5. **Latent Decoding:** Tokenizer reconstructs `[T, 27, 3, 3]` 3D rotation matrices and `[T, 3]` root translations.
6. **Kinematics & Retargeting:** Forward kinematics calculates 3D joint positions for `CoreSkeleton27`; retargeter calculates normalized quaternions for 22 standard VRM Humanoid bones.
7. **Delivery:** Payload is sent to frontend via WebSocket or REST.
8. **Synchronized Playback:** Dual viewports advance on the same clock tick, comparing skeleton physics directly with avatar deformations.
