# DiP-Viser Operator Runbook

**Experiment Location**: `exp/dip-viser/`  
**Purpose**: Step-by-step reproducible instructions for environment setup, model verification, 3D viewer launch, batch generation, testing, and benchmarking.

---

## 1. Prerequisites and Environment Setup

### 1.1 Requirements
- Windows 10/11 64-bit or Linux
- Python 3.10.x (recommended via `uv`)
- NVIDIA GPU with CUDA 12.x support (minimum 4 GB VRAM; CPU fallback also supported)
- `uv` package manager (tested with 0.11.29)

### 1.2 Initialize Isolated Virtual Environment
From repository root `VRMMotionGeneration/`:

```powershell
# Create isolated Python 3.10 virtual environment
uv venv exp/dip-viser/.venv --python 3.10

# Activate the environment (PowerShell)
.\exp\dip-viser\.venv\Scripts\Activate.ps1
```

### 1.3 Install Pinned Dependencies
```powershell
# Install PyTorch with CUDA 12.1
.\exp\dip-viser\.venv\Scripts\pip.exe install torch==2.5.1+cu121 torchvision==0.20.1+cu121 --index-url https://download.pytorch.org/whl/cu121

# Install Viser and core dependencies
.\exp\dip-viser\.venv\Scripts\pip.exe install viser==1.1.1 transformers==4.47.1 numpy==2.2.6 scipy==1.15.3 moviepy==1.0.3 spacy==3.8.16 smplx==0.1.28 pytest matplotlib trimesh joblib scikit-learn

# Install CLIP
.\exp\dip-viser\.venv\Scripts\pip.exe install git+https://github.com/openai/CLIP.git
```

---

## 2. Checkpoint and Asset Verification

### 2.1 Verify Environment & Assets
Run the automated verification scripts:

```powershell
# Check Python, PyTorch, CUDA and Viser imports
.\exp\dip-viser\.venv\Scripts\python.exe exp/dip-viser/scripts/check_environment.py

# Verify DiP checkpoint, GloVe files, and HumanML3D mean/std stats
.\exp\dip-viser\.venv\Scripts\python.exe exp/dip-viser/scripts/verify_assets.py
```
Both scripts must exit with code 0 (`PASS`).

---

## 3. Launching the Interactive Viser 3D Viewer

To start the interactive browser-based 3D viewer:

```powershell
.\exp\dip-viser\.venv\Scripts\python.exe exp/dip-viser/scripts/run_viser_demo.py --host 127.0.0.1 --port 8080
```

### Accessing the Viewer
1. Open your web browser and navigate to:  
   **`http://localhost:8080`**
2. On initial startup, the viewer loads the pre-generated real DiP motion (`sample_01`).
3. To generate a new motion:
   - Type a text prompt into **Prompt Input** (or select a preset).
   - Adjust **Duration** (2.0s – 9.8s) and **Guidance Scale** (default: 7.5).
   - Click **🚀 Generate Motion**.
   - Monitor live progress in the **Job Status** field.
   - Upon completion, the 3D skeleton updates immediately to the new motion with a green **REAL MODEL INFERENCE** badge.
4. Playback controls:
   - **Play/Pause**: Toggle animation playback.
   - **Timeline Slider**: Scrub through frames or inspect specific poses.
   - **Loop Playback**: Continuously loop without re-running model inference.
   - **Speed**: Switch between 0.25x, 0.5x, 1.0x, 1.5x, and 2.0x playback speed.

---

## 4. Running Standalone CLI Generation and Batch Jobs

### 4.1 Single Prompt via Subprocess CLI
```powershell
.\exp\dip-viser\.venv\Scripts\python.exe exp/dip-viser/scripts/run_dip_batch.py `
  --prompt "A person kicks with their right leg." `
  --duration 3.5 `
  --device 0
```

### 4.2 Batch Processing from JSON Prompts File
```powershell
.\exp\dip-viser\.venv\Scripts\python.exe exp/dip-viser/scripts/run_dip_batch.py `
  --prompts_file exp/dip-viser/assets/prompts.json `
  --output_dir exp/dip-viser/artifacts/samples/batch_output `
  --device 0
```

---

## 5. Running the Formal Benchmark Protocol

To measure cold-start latency, warm latency, RTF, generated FPS, and memory:

```powershell
.\exp\dip-viser\.venv\Scripts\python.exe exp/dip-viser/scripts/benchmark_dip.py --trials 3 --device 0
```

Output files:
- Raw JSON: `exp/dip-viser/artifacts/benchmarks/benchmark_results.json`
- Summary Markdown: `exp/dip-viser/artifacts/benchmarks/benchmark_summary.md`
- Formal Report: `exp/dip-viser/docs/benchmark-report.md`

---

## 6. Running the Unit Test Suite

Run all 23 unit tests with pytest:

```powershell
.\exp\dip-viser\.venv\Scripts\pytest.exe exp/dip-viser/tests -v
```

Expected result: `23 passed in 0.22s` with exit code 0.

---

## 7. Troubleshooting

| Issue | Cause | Resolution |
|---|---|---|
| `CUDA out of memory` | VRAM exhausted during diffusion sampling | Lower duration to 3.0s or run on CPU with `--device -1`. |
| `PermissionError: [WinError 32]` | File handle held during directory cleanup on Windows | Addressed by buffering stdout and writing logs after process termination. |
| `DataLoader worker pickling error` | Windows `spawn` multiprocessing limitation | Handled by upstream patch setting `num_workers = 0` on Windows (`os.name == 'nt'`). |
| `SMPL_NEUTRAL.pkl missing` | SMPL mesh loader called unconditionally | HumanML3D uses Cartesian 3D joints (`pose_rep == 'xyz'`); patched to lazy-load SMPL only when mesh reconstruction is requested. |
