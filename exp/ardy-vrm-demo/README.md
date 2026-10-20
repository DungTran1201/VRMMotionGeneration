# NVIDIA ARDY Text-to-Motion-to-VRM End-to-End Demo

Welcome to the **ARDY → VRM Motion Lab**, an isolated experimental workspace implementing an end-to-end Text-to-Motion-to-VRM synthesis pipeline using NVIDIA ARDY and Three.js in a full-page 3D technical workspace.

---

## 1. Quick Start

### 1.1 Run Backend & Frontend Contract Tests (Pytest - 19 Tests)
```powershell
$env:PYTHONPATH = "backend/src;vendor/ardy"
& ".\.venv\Scripts\python.exe" -m pytest backend/src/ardy_vrm_demo/tests -v
```

### 1.2 Run Frontend VRM Loader Contract Tests (Node.js Test Runner - 8 Tests)
```powershell
node --test frontend/tests/test_vrm_loader_contract.js
```

### 1.3 Start the Web Server
```powershell
$env:PYTHONPATH = "backend/src;vendor/ardy"
& ".\.venv\Scripts\python.exe" -m uvicorn ardy_vrm_demo.api:app --host 127.0.0.1 --port 8000
```
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

### 1.4 Reproduce Performance Benchmark
```powershell
& ".\.venv\Scripts\python.exe" scripts\benchmark_generation.py --prompt "A person walks forward in a straight line with natural arm swings." --runs 5
```

---

## 2. Directory Structure

```
exp/ardy-vrm-demo/
├── README.md                          # Workspace documentation & quickstart
├── pyproject.toml                     # Isolated Python project configuration
├── .gitignore                         # Checkpoint & virtualenv ignore rules
├── .env.example                       # Environment variables template
├── frontend/                          # Fullscreen 3D Motion Workspace
│   ├── index.html                     # Full-page 3D stage entry point (100dvw x 100dvh)
│   ├── src/
│   │   ├── animation/                 # Synchronized single timeline controller
│   │   ├── api/                       # REST + WebSocket client
│   │   ├── app/                       # Main application coordinator
│   │   ├── components/                # Floating customizable tool window component
│   │   ├── scene/                     # Unified single Three.js comparison stage
│   │   ├── skeleton/                  # CoreSkeleton27 joint & line renderer
│   │   ├── styles/                    # Technical cybernetic HUD & window styles
│   │   ├── telemetry/                 # Telemetry HUD updater with truthful defaults
│   │   └── vrm/                       # VRM 1.0 & 0.x loader with auto-grounding
│   └── tests/                         # Node.js automated test suite
│       └── test_vrm_loader_contract.js# Automated unit tests for VRM loader
├── backend/                           # FastAPI server & inference engine
│   └── src/ardy_vrm_demo/
│       ├── api.py                     # REST endpoints & static file serving
│       ├── schemas.py                 # Pydantic contract schemas
│       ├── ardy_runtime/              # Model engine & decoupled text encoder
│       ├── jobs/                      # Async queue & WebSocket broadcaster
│       ├── motion_adapter/            # CoreSkeleton27 FK & VRM retargeter
│       └── tests/                     # Pytest suite (19 tests)
│           ├── test_api_endpoints.py
│           ├── test_frontend_contracts.py
│           ├── test_motion_math.py
│           └── test_retargeting.py
├── checkpoints/                       # Local model weights (gitignored)
│   └── ARDY-Core-RP-20FPS-Horizon8/   # 20 FPS, 8-frame horizon checkpoint
├── vendor/ardy/                       # Official NVIDIA ARDY (commit e706e27)
├── artifacts/
│   ├── sample-motion/                 # Real generated motion samples (JSON)
│   └── benchmark/                     # Benchmark results (results.json)
├── scripts/
│   ├── check_environment.py           # Hardware & driver verification
│   ├── verify_checkpoints.py          # Checkpoint SafeTensors integrity test
│   ├── generate_sample.py             # CLI motion synthesis tool
│   └── benchmark_generation.py        # Automated benchmark runner
├── docs/                              # Technical lifecycle documentation
│   ├── vrm-loading-root-cause.md      # Root cause analysis & loader diagnostics
│   ├── fullscreen-stage-design.md     # 3D workspace design & floating windows
│   ├── motion-and-vrm-lifecycle.md    # Avatar loading, retargeting & timeline
│   └── testing-and-verification.md    # Test commands, logs & browser evidence
└── diagrams/                          # Derived Mermaid architecture diagrams
    ├── vrm-loading-sequence.mmd
    ├── fullscreen-stage-architecture.mmd
    └── motion-playback-sequence.mmd
```

---

## 3. Verified Benchmark Metrics

Empirical measurements on NVIDIA GeForce GTX 1650 (4 GB VRAM):
- **Model Checkpoint:** `ARDY-Core-RP-20FPS-Horizon8`
- **Output Sample:** 60 frames (3.0s at 20 FPS)
- **Median Generation Time:** **1.625 seconds**
- **Throughput:** **36.92 FPS**
- **Real-Time Factor (RTF):** **0.542** (~1.85x faster than real-time playback)
- **Peak VRAM:** **885.35 MB**
- **Retargeting Time:** **< 16 ms**
