# Baseline Environment & Machine Audit — DiP + Viser Experiment

**Date**: 2026-10-21  
**Author**: Operation Dev  
**Experiment Path**: `exp/dip-viser/`  
**Classification**: `VERIFIED`

---

## 1. Host Machine Specification

- **Operating System**: Microsoft Windows 10 Pro 64-bit (Version 10.0.19045)
- **CPU**: 12th Gen Intel(R) Core(TM) i5-12400F (6 physical cores, 12 logical threads, base ~2.50 GHz)
- **RAM**:
  - Total Visible Memory: 8,227,972 KB (~7.85 GB)
  - Free Physical Memory: ~1.4 GB at inspection time (RAM constraints present)
- **Disk Drives**:
  - `C:\`: ~10.4 GB free / 244.9 GB total
  - `E:\`: ~310.7 GB free / 500.1 GB total
  - Note: Disk space on `C:\` must be strictly managed to avoid exhaustion during package caching.
- **GPU & Accelerator**:
  - GPU Model: NVIDIA GeForce GTX 1650
  - Driver Version: 591.74
  - Max Supported CUDA Version: CUDA 13.1 (WDDM 2.7)
  - VRAM: 4,096 MiB total, ~1,191 MiB used by OS/browser/display, ~2,905 MiB available
- **Installed Developer Tooling**:
  - `python`: Python 3.8.10 (`C:\Users\PC\AppData\Local\Programs\Python\Python38\python.exe`)
  - `python 3.9`: Python 3.9.12 (`C:\Users\PC\AppData\Local\Programs\Python\Python39\python.exe`)
  - `python 3.12`: Python 3.12.9 (`C:\Users\PC\AppData\Local\Programs\Python\Python312\python.exe`)
  - `uv`: 0.11.29 (`901092ee1 2026-07-15 x86_64-pc-windows-msvc`)
  - `git-lfs`: 3.7.0 (`windows amd64; go 1.24.4; git 92dddf56`)
  - `conda`: Not found in system PATH
  - `ffmpeg`: Not found in system PATH (moviepy fallback / pure skeleton export to Viser)

---

## 2. Upstream MDM / DiP Pinned Source

- **Repository URL**: `https://github.com/GuyTevet/motion-diffusion-model`
- **Pinned Commit SHA**: `ef8edce6a53c6ab19e53b4d4dcf15bc0bc60a778`
- **Commit Date**: Tue Sep 30 17:29:26 2025 -0700
- **Commit Message**: `Merge pull request #81 from urw7rs/improve_performance — Fix low GPU utilization`
- **Location**: `exp/dip-viser/upstream/motion-diffusion-model/` (ignored via `.gitignore`)
- **Key Upstream Characteristics Verified**:
  - DiP architecture uses Transformer Decoder (`trans_dec`, 8 layers, 512 latent dimension).
  - Text encoder uses DistilBERT (`distilbert/distilbert-base-uncased` via Hugging Face `transformers`).
  - Diffusion steps: 10 steps (cosine schedule).
  - Frame structure: 20 context frames prefix, 40 frames predicted per chunk (2 seconds at 20 FPS).
  - Output representation: HumanML3D 263-dim feature vector un-normalized and converted to 22 joints 3D Cartesian coordinates via `recover_from_ric()`.

---

## 3. Experiment Isolation & Safety Strategy

1. **Venv Isolation**: Dedicated virtual environment at `exp/dip-viser/.venv` using CPython 3.10.20 managed via `uv`. No mutation or sharing with root or other experiments (`exp/ardy-vrm-demo`, `exp/motionstreamer`).
2. **Git & Weight Isolation**: `exp/dip-viser/.gitignore` excludes `.venv/`, `upstream/`, `checkpoints/*`, `*.pt`, `*.npy`, `*.mp4`, preventing multi-hundred-megabyte binaries from entering Git history.
3. **Layout Compliance**: Checkpoint files are strictly located in `exp/dip-viser/checkpoints/` to satisfy `python .agents/scripts/validate_layout.py`.
4. **Deterministic Fixture Fallback**: If checkpoint or asset access is unavailable or interrupted, a marked fixture format is maintained and verified. Real model generation is never claimed unless live inference logs and tensors are produced and validated.
