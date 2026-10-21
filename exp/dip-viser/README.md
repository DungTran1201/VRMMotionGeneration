# DiP (Diffusion Planner) Text-to-Motion with Viser

**Location**: `exp/dip-viser/`  
**Status**: `DIP-VISER E2E PASS` (Verified with live GPU model inference, browser viewer, tests, and benchmarks)  
**Authors**: Operation Dev  
**Date**: October 2026  

---

## Overview

This experiment provides a standalone, fully reproducible research demo integrating the official **DiP (Diffusion Planner)** autoregressive text-to-motion model with **Viser 1.1.1** for browser-based 3D skeletal motion visualization.

It demonstrates **actual model-generated 3D motions** conditioned on natural language prompts (e.g. *"A person walks forward and waves."*), verified directly on local hardware without synthetic mocks.

```
+-----------------------------------------------------------------------------------+
|  Viser WebGL 3D Viewer (http://localhost:8080)                                    |
|  - Real DiP-generated 22-joint SMPL skeleton                                      |
|  - Ground grid, origin axes, metric right-handed coordinates (+Y Up)              |
|  - Interactive prompt input, duration/guidance sliders, GPU/CPU selector          |
|  - Play / Pause / Seek / Loop / Speed animation controls                          |
|  - Real-time telemetry: Latency, RTF, Generated FPS, Provenance badge             |
+-----------------------------------------------------------------------------------+
```

---

## Quick Start

### 1. Launch the Interactive 3D Viewer
```powershell
# Activate the experiment environment
.\exp\dip-viser\.venv\Scripts\Activate.ps1

# Start the Viser 3D Viewer
.\exp\dip-viser\.venv\Scripts\python.exe exp/dip-viser/scripts/run_viser_demo.py --port 8080
```
Open **`http://localhost:8080`** in your browser.

### 2. Run Standalone CLI Generation
```powershell
.\exp\dip-viser\.venv\Scripts\python.exe exp/dip-viser/scripts/run_dip_batch.py `
  --prompt "A person kicks with their right leg." `
  --duration 3.5 `
  --device 0
```

### 3. Run Verification & Benchmarking
```powershell
# Verify assets and environment
.\exp\dip-viser\.venv\Scripts\python.exe exp/dip-viser/scripts/check_environment.py
.\exp\dip-viser\.venv\Scripts\python.exe exp/dip-viser/scripts/verify_assets.py

# Run unit test suite (23 tests)
.\exp\dip-viser\.venv\Scripts\pytest.exe exp/dip-viser/tests -v

# Run formal benchmark protocol
.\exp\dip-viser\.venv\Scripts\python.exe exp/dip-viser/scripts/benchmark_dip.py --trials 3 --device 0
```

---

## Key Performance Results (NVIDIA GTX 1650)

| Metric | Measured Value (Warm Median) |
|---|---|
| **Inference Latency** | **11.671 s** (for 4.0s motion @ 80 frames) |
| **Real-Time Factor (RTF)** | **2.918x** (Batch-to-playback architecture) |
| **Generated Motion FPS** | **6.8 frames/s** |
| **Viewer Render FPS** | **~30–60 FPS** (Decoupled browser Three.js canvas) |
| **VRAM Allocated** | **~1.6 GB** (Fits comfortably in 4 GB VRAM) |

> **Architecture Notice**: Because RTF > 1.0, this system generates the full sequence before starting playback. It is **not** a streaming pipeline.

---

## Documentation Index

- [Research and Environment Decisions](file:///c:/Users/PC/Project/VRMMotionGeneration/exp/dip-viser/docs/research-and-environment.md)
- [Baseline Machine Audit](file:///c:/Users/PC/Project/VRMMotionGeneration/exp/dip-viser/docs/baseline.md)
- [System Architecture](file:///c:/Users/PC/Project/VRMMotionGeneration/exp/dip-viser/docs/architecture.md)
- [Motion Output Contract](file:///c:/Users/PC/Project/VRMMotionGeneration/exp/dip-viser/docs/motion-output-contract.md)
- [Operator Runbook](file:///c:/Users/PC/Project/VRMMotionGeneration/exp/dip-viser/docs/runbook.md)
- [Formal Benchmark Report](file:///c:/Users/PC/Project/VRMMotionGeneration/exp/dip-viser/docs/benchmark-report.md)
- [Known Limitations](file:///c:/Users/PC/Project/VRMMotionGeneration/exp/dip-viser/docs/known-limitations.md)
- [Diagrams](file:///c:/Users/PC/Project/VRMMotionGeneration/exp/dip-viser/docs/diagrams/)
  - [System Context](file:///c:/Users/PC/Project/VRMMotionGeneration/exp/dip-viser/docs/diagrams/system-context.mmd)
  - [Inference Sequence](file:///c:/Users/PC/Project/VRMMotionGeneration/exp/dip-viser/docs/diagrams/inference-sequence.mmd)
  - [Playback Sequence](file:///c:/Users/PC/Project/VRMMotionGeneration/exp/dip-viser/docs/diagrams/playback-sequence.mmd)
