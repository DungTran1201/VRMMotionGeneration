# NVIDIA ARDY Text-to-Motion-to-VRM End-to-End Demo

Welcome to the **ARDY → VRM Motion Lab**, an isolated experimental workspace implementing an end-to-end Text-to-Motion-to-VRM synthesis pipeline using NVIDIA ARDY.

---

## 1. Quick Start

### 1.1 Run the Automated Test Suite
```powershell
exp\ardy-vrm-demo\.venv\Scripts\python.exe -m pytest exp/ardy-vrm-demo/backend/src/ardy_vrm_demo/tests -v
```

### 1.2 Start the Web Server
```powershell
exp\ardy-vrm-demo\.venv\Scripts\python.exe -m uvicorn ardy_vrm_demo.api:app --app-dir exp/ardy-vrm-demo/backend/src --host 127.0.0.1 --port 8000
```
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

### 1.3 Reproduce Performance Benchmark
```powershell
exp\ardy-vrm-demo\.venv\Scripts\python.exe exp\ardy-vrm-demo\scripts\benchmark_generation.py --prompt "A person walks forward in a straight line with natural arm swings." --runs 5
```

---

## 2. Directory Structure

```
exp/ardy-vrm-demo/
├── README.md                          # Workspace documentation & quickstart
├── pyproject.toml                     # Isolated Python project configuration
├── .gitignore                         # Checkpoint & virtualenv ignore rules
├── .env.example                       # Environment variables template
├── frontend/                          # Web UI comparison viewer
│   ├── index.html                     # Dual-viewport SPA entry point
│   └── src/
│       ├── animation/                 # Synchronized timeline controller
│       ├── api/                       # REST + WebSocket client
│       ├── app/                       # Main application coordinator
│       ├── scene/                     # Three.js dual-viewport stage
│       ├── skeleton/                  # CoreSkeleton27 line & joint renderer
│       ├── styles/                    # Cybernetic technical HUD styles
│       ├── telemetry/                 # Telemetry HUD updater
│       └── vrm/                       # VRM 1.0 loader & humanoid retargeter
├── backend/                           # FastAPI server & inference engine
│   └── src/ardy_vrm_demo/
│       ├── api.py                     # REST endpoints & static file serving
│       ├── schemas.py                 # Pydantic contract schemas
│       ├── ardy_runtime/              # Model engine & decoupled text encoder
│       ├── jobs/                      # Async queue & WebSocket broadcaster
│       ├── motion_adapter/            # CoreSkeleton27 FK & VRM retargeter
│       └── tests/                     # Pytest suite (13 tests)
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
└── diagrams/                          # Derived Mermaid architecture diagrams
```

---

## 3. Verified Metrics

Empirical measurements on NVIDIA GeForce GTX 1650 (4 GB VRAM):
- **Model Checkpoint:** `ARDY-Core-RP-20FPS-Horizon8`
- **Output Sample:** 60 frames (3.0s at 20 FPS)
- **Median Generation Time:** **1.625 seconds**
- **Throughput:** **36.92 FPS**
- **Real-Time Factor (RTF):** **0.542** (~1.85x faster than real-time playback)
- **Peak VRAM:** **885.35 MB**
- **Retargeting Time:** **< 16 ms**
