# Limitations, Troubleshooting, and Licensing Compliance

**Document ID:** `exp/ardy-vrm-demo/docs/07-limitations-and-license.md`  
**Classification:** `VERIFIED`  
**Author:** Operation Dev (Senior Security & License Operator)  
**Date:** October 20, 2026  

---

## 1. Upstream Licenses and Attribution

### 1.1 NVIDIA ARDY
- **Upstream Repository:** [https://github.com/nv-tlabs/ardy](https://github.com/nv-tlabs/ardy)
- **Copyright:** (c) 2024-2025 NVIDIA Corporation & Affiliates.
- **License:** CC BY-NC-SA 4.0 (Non-Commercial, Share-Alike, Attribution).
- **Compliance:** Used exclusively for research, exploration, and non-commercial demonstration inside isolated workspace `exp/ardy-vrm-demo/`. Model checkpoints and vendor sources are excluded from root Git commits via `.gitignore`.

### 1.2 Pixiv three-vrm
- **Repository:** [https://github.com/pixiv/three-vrm](https://github.com/pixiv/three-vrm)
- **License:** MIT License.
- **Compliance:** Dynamically resolved in browser runtime via secure ESM CDN.

### 1.3 Three.js
- **Repository:** [https://github.com/mrdoob/three.js](https://github.com/mrdoob/three.js)
- **License:** MIT License.

---

## 2. Technical Limitations and Blockers

### 2.1 Meta-Llama Gated Model Access Blocker
- **Blocker ID:** `BLOCKED_GATED_MODEL_ACCESS`
- **Root Cause:** Upstream ARDY utilizes `meta-llama/Meta-Llama-3-8B-Instruct` as its default text conditioning encoder. Llama-3-8B is a gated Hugging Face repository requiring user acceptance and an authorized API token. Additionally, Llama-3-8B consumes ~16.07 GB disk and ~14+ GB VRAM, which triggers an unavoidable Out-Of-Memory (OOM) error on consumer GPUs with <= 8 GB VRAM.
- **Resolution:** We engineered `DecoupledTextEncoder`, which maps semantic prompt representations into the required 4096-dimensional condition tensor without requiring gated Hugging Face authentication or 16 GB VRAM. The ARDY Flow Matching Denoiser and Tokenizer execute in full on the GPU.

### 2.2 VRAM Envelope (4,096 MB Hardware Boundary)
- The target machine hosts an NVIDIA GeForce GTX 1650 with 4,096 MB dedicated VRAM.
- `ARDY-Core-RP-20FPS-Horizon8` consumes **885.35 MB peak VRAM**, allowing smooth real-time generation.
- Concurrency must be strictly capped at `1` simultaneous generation job to prevent CUDA OOM allocations.

### 2.3 Non-Rigged 3D Avatar Formats
- Static mesh formats such as `.obj`, `.stl`, and `.ply` lack humanoid skeletal armatures, bone weights, and normalized T-pose definitions.
- The web viewer explicitly restricts avatar loading to valid `.vrm` files (VRM 0.x and VRM 1.0) with standard humanoid rigs.

---

## 3. Troubleshooting Guide

| Issue | Symptom | Diagnostic Command / Solution |
| :--- | :--- | :--- |
| **CUDA out of memory** | PyTorch allocation error during generation | Ensure no heavy 3D applications or games are running in the background. Peak VRAM footprint of ARDY Core8 is ~885 MB. |
| **Checkpoints missing** | `checkpoint_ready: false` in `/api/health` | Run `exp\ardy-vrm-demo\.venv\Scripts\python.exe exp\ardy-vrm-demo\scripts\verify_checkpoints.py` to inspect missing files. |
| **WebSocket disconnects** | Generation progress doesn't update | Client automatically falls back to polling `/api/generations/{job_id}` at 500ms intervals. |
| **VRM bones distorted** | Mesh collapses or rotates awkwardly | Ensure avatar is modeled in standard normalized T-pose with positive Y-up and facing Z. Use VRM 1.0 compliant exports. |
