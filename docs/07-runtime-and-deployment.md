# 07 - Runtime Setup and Deployment Guide

## 1. Prerequisites & Environment Setup

### Required Runtimes
- **Python:** 3.9+ (Python 3.12 verified)
- **Node.js:** v18+ (Node.js v24 verified with npm 11.16)
- **Git & Git LFS:** For repository management

---

## 2. Installation & Quick Start

### 2.1 Backend Setup (Windows PowerShell)

```powershell
# Navigate to repository root
cd c:\Users\PC\Project\VRMMotionGeneration

# Install backend dependencies
py -3.12 -m pip install -e backend/

# Validate environment readiness
$env:PYTHONPATH="backend/src"
py -3.12 scripts/validate_environment.py

# Launch FastAPI Backend Service (Port 8000)
py -3.12 -m uvicorn motionbricks_vrm.app:app --host 127.0.0.1 --port 8000
```

### 2.2 Backend Setup (Unix / macOS)

```bash
cd /path/to/VRMMotionGeneration
python3 -m pip install -e backend/
export PYTHONPATH="backend/src"
python3 scripts/validate_environment.py
python3 -m uvicorn motionbricks_vrm.app:app --host 127.0.0.1 --port 8000
```

### 2.3 Frontend Setup

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open your browser at **`http://127.0.0.1:5173/`**.

---

## 3. Operating Modes

### Mode A: Fixture / Offline Demo (Default)
- **Requirements:** Browser only. Backend is optional (will serve from static `/sample_motion.json` if offline).
- **Features:** 100% functional WebGL viewport, walking mannequin animation, full timeline controls (play, pause, scrub, speed, loop), and local `.vrm` avatar loading.
- **Verification:** UI displays green badge `MODE A: FIXTURE (OFFLINE)`.

### Mode B: Real MotionBricks Inference
- **Requirements:** Pretrained weights downloaded, PyTorch installed, and compatible NVIDIA GPU.
- **Fetching Weights:**
  From the root of `GR00T-WholeBodyControl`, execute:
  ```bash
  git lfs pull --include="motionbricks/out/**" --exclude=""
  ```
- **Verification:** Run `python scripts/validate_environment.py`. When checkpoints are verified binary weights (not 135-byte pointers), Mode B automatically transitions to READY.

---

## 4. Troubleshooting Common Issues

| Symptom | Cause | Solution |
|---|---|---|
| `HTTP 503: Real MotionBricks inference unavailable` | Checkpoint files in `motionbricks/out` are Git-LFS pointer files (~135 bytes). | Run `git lfs pull --include="motionbricks/out/**"` in `GR00T-WholeBodyControl`. |
| Avatar appears transparent or distorted | Incompatible VRM 0.0 axis orientation. | Click "Reset Camera" or verify the VRM model using official VRM validator tools. |
| Port 8000 or 5173 already in use | Stale background server process. | Terminate running process via Task Manager or run `Get-Process python` / `Stop-Process`. |
