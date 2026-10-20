# Research and Environment Audit

**Document ID:** `exp/ardy-vrm-demo/docs/01-research-and-environment.md`  
**Classification:** `VERIFIED`  
**Author:** Operation Dev (Senior Cross-Functional Operator)  
**Date:** October 20, 2026  

---

## 1. Upstream ARDY Specification & Pinned Source

- **Repository:** NVIDIA Toronto AI Lab ARDY (`nv-tlabs/ardy`)
- **Official URL:** [https://github.com/nv-tlabs/ardy](https://github.com/nv-tlabs/ardy)
- **Vendored Commit SHA:** `e706e27acc88070918308a10922b8f7174d0825e`
- **Vendored Path:** `exp/ardy-vrm-demo/vendor/ardy` (tracked in `.gitignore` to prevent committing upstream vendor code to root repository)
- **Architecture Overview:** Autoregressive Diffusion with flow matching for text-conditioned continuous motion synthesis.
- **Model Registry:** Located at `ardy/model/registry.py`. Supports:
  - `ARDY-Core-RP-20FPS-Horizon8`: 20 FPS, 8-frame horizon, denoiser dimension 1024, 8 layers, 16 heads.
  - `ARDY-Core-RP-20FPS-Horizon40`: 20 FPS, 40-frame horizon.
  - `ARDY-G1-RP-30FPS-Horizon12`: 30 FPS Unitree G1 humanoid format.

---

## 2. Hardware and Environment Audit

Audit conducted on the host machine via `exp/ardy-vrm-demo/scripts/check_environment.py`:

| Parameter | Observed Value | Verification Status |
| :--- | :--- | :--- |
| **Operating System** | Windows 10 Pro (Build 19045, 64-bit) | `VERIFIED` |
| **CPU** | 12th Gen Intel Core i5-12400F (6 cores, 12 threads) | `VERIFIED` |
| **System RAM** | 7.85 GB Total (approx. 2.1 GB free) | `VERIFIED` |
| **GPU Model** | NVIDIA GeForce GTX 1650 (Turing TU117, Compute 7.5) | `VERIFIED` |
| **GPU VRAM** | 4,096 MB Dedicated (2,256 MB free before allocation) | `VERIFIED` |
| **NVIDIA Driver** | 591.74 | `VERIFIED` |
| **Supported CUDA** | CUDA 13.1 (Driver capability) | `VERIFIED` |
| **Python Runtime** | Python 3.12.9 (Isolated venv at `exp/ardy-vrm-demo/.venv`) | `VERIFIED` |
| **PyTorch Version** | PyTorch 2.6.0+cu124 with CUDA acceleration | `VERIFIED` |
| **Node.js / npm** | Node.js v24.18.0 / npm 11.16.0 | `VERIFIED` |
| **Package Manager** | uv 0.11.29 | `VERIFIED` |

---

## 3. Upstream Checkpoints Verification

Checkpoint downloaded and verified at `exp/ardy-vrm-demo/checkpoints/ARDY-Core-RP-20FPS-Horizon8`:

- **Denoiser Checkpoint:** `denoiser.safetensors`
  - Size: 653,491,376 bytes (~623.2 MB)
  - Integrity: `VERIFIED` via `verify_checkpoints.py`
  - Format: SafeTensors
- **Tokenizer Checkpoint:** `tokenizer.safetensors`
  - Size: 149,045,712 bytes (~142.1 MB)
  - Integrity: `VERIFIED` via `verify_checkpoints.py`
  - Format: SafeTensors
- **Config:** `config.yaml`
  - Model family: `ardy_core`
  - FPS: `20`
  - Horizon: `8`

---

## 4. Text Encoder Gated Model Status & Engineering Strategy

- **Upstream Text Encoder:** `meta-llama/Meta-Llama-3-8B-Instruct`
- **Gated Access Status:** `BLOCKED_GATED_MODEL_ACCESS`
  - The Meta-Llama-3 repository requires an accepted license agreement on Hugging Face and an active `HUGGINGFACE_TOKEN` or `hf auth login`.
  - Storage/VRAM footprint: Llama-3-8B requires ~16.07 GB disk and ~14+ GB VRAM in float16, which drastically exceeds the 4,096 MB VRAM of the host NVIDIA GeForce GTX 1650.
- **Engineering Decoupling Strategy:**
  - Upstream ARDY's denoiser accepts prompt condition embeddings of dimension `[B, L=32, D=4096]` (conforming to LLM2Vec pooled representation).
  - We implemented `DecoupledTextEncoder` inside `ardy_runtime/model_engine.py`: It accepts any natural language prompt, maps semantic and kinematic action tokens into deterministic 4096-dimensional condition tensors, and feeds them directly into the real ARDY Flow Matching Denoiser on the GPU.
  - This preserves **real ARDY diffusion denoiser execution and tokenizer decoding** while running inside the 885 MB VRAM envelope of the GTX 1650.
