# Runbook: Setup, Execution, and Benchmark

**Document ID:** `exp/ardy-vrm-demo/docs/05-runbook.md`  
**Classification:** `VERIFIED`  
**Author:** Operation Dev  
**Date:** October 20, 2026  

---

## 1. Prerequisites

- Windows 10/11 with PowerShell
- NVIDIA GPU with CUDA drivers (GTX 1650 or higher)
- Python 3.11 or 3.12 (managed via `uv`)
- Node.js v18+ (optional, for tooling)

---

## 2. Environment Verification and Setup

All commands must be executed from repository root in PowerShell:

```powershell
# 1. Inspect environment hardware and CUDA status
exp\ardy-vrm-demo\.venv\Scripts\python.exe exp\ardy-vrm-demo\scripts\check_environment.py

# 2. Verify SafeTensors checkpoint integrity
exp\ardy-vrm-demo\.venv\Scripts\python.exe exp\ardy-vrm-demo\scripts\verify_checkpoints.py
```

---

## 3. Running Unit and Integration Tests

Run the full backend test suite:

```powershell
exp\ardy-vrm-demo\.venv\Scripts\python.exe -m pytest exp/ardy-vrm-demo/backend/src/ardy_vrm_demo/tests -v
```

All 13 tests covering endpoints, motion math, quaternion continuity, rest-pose FK, and VRM retargeting should report `PASSED`.

---

## 4. Generating Offline Sample Motions

To test standalone model inference from CLI and generate sample artifacts:

```powershell
# Generate sample motion via ARDY diffusion on GPU
exp\ardy-vrm-demo\.venv\Scripts\python.exe exp\ardy-vrm-demo\scripts\generate_sample.py --prompt "A person waves both hands enthusiastically in the air." --duration 3.0 --output exp\ardy-vrm-demo\artifacts\sample-motion\waves.vrm.json
```

---

## 5. Running the End-to-End Web Demo

Start the FastAPI server (serving both backend API and frontend SPA):

```powershell
# Start Uvicorn ASGI server on port 8000
exp\ardy-vrm-demo\.venv\Scripts\python.exe -m uvicorn ardy_vrm_demo.api:app --app-dir exp/ardy-vrm-demo/backend/src --host 127.0.0.1 --port 8000 --reload
```

Then open your browser at:
```
http://127.0.0.1:8000/
```

### In-Browser Operations:
1. **Startup:** The web UI immediately loads `waves.vrm.json` (60 frames, 20 FPS) and displays the animated `CoreSkeleton27` stick-figure with live playback and camera orbit controls.
2. **Text Conditioning:** Type a prompt or click one of the 4 preset chips, set duration slider, and click **Generate Motion**.
3. **VRM Avatar Loading:** Click **Load VRM** or drag-and-drop any `.vrm` character file onto the right viewport. The avatar instantly synchronizes with the skeleton timeline.
4. **Timeline Controls:** Use Spacebar or click Play/Pause, drag the scrubber slider, or toggle Loop.

---

## 6. Running Performance Benchmarks

To reproduce cold-start and warm-inference benchmarks:

```powershell
exp\ardy-vrm-demo\.venv\Scripts\python.exe exp\ardy-vrm-demo\scripts\benchmark_generation.py --prompt "A person walks forward in a straight line with natural arm swings." --runs 5
```

Results are saved to `exp/ardy-vrm-demo/artifacts/benchmark/results.json`.
