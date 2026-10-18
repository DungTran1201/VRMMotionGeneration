# MotionBricks-to-VRM Integration Engine

A modular, real-time proof-of-concept pipeline bridging NVIDIA's **MotionBricks** generative motion framework with the **VRM (Virtual Reality Model)** 3D humanoid standard via the **`CanonicalHumanoidMotion/v1`** schema.

---

## Highlights

- **Model-Independent Architecture:** Decouples AI motion generation from WebGL avatar rendering using the validated `CanonicalHumanoidMotion/v1` specification.
- **Two Distinct Operating Modes:**
  - **Mode A (Fixture / Offline Demo):** 100% functional without GPU, PyTorch, or pretrained weights. Includes a deterministic walking locomotion cycle.
  - **Mode B (Real MotionBricks Inference):** Integrates directly with the genuine MotionBricks checkpoint pipeline when weights are pulled.
- **G1-to-Humanoid Retargeting Engine:** Converts the 34-joint Unitree G1 robot hierarchy (serial pitch $\rightarrow$ roll $\rightarrow$ yaw hinge chains) into standard 3-DOF spherical humanoid bones.
- **Modern Three.js + `@pixiv/three-vrm` Web Viewer:** High-aesthetic dark-mode technical UI with orbit controls, procedural mannequin fallback, custom VRM file loading, bone inspection, and timeline scrubber.
- **Zero-Modification Policy:** Treats upstream `NVlabs/GR00T-WholeBodyControl` code as read-only reference with isolated adapters.

---

## Quick Start

### 1. Mode A: Instant Offline Demo (Browser Only)

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173/` in your browser. The procedural humanoid mannequin immediately begins walking using the pre-validated Mode A locomotion fixture. You can also drag and drop or upload your own `.vrm` avatar.

### 2. Backend Service (FastAPI & Streaming WebSocket)

```powershell
# From repository root
$env:PYTHONPATH="backend/src"
py -3.12 -m pip install -e backend/
py -3.12 scripts/validate_environment.py
py -3.12 -m uvicorn motionbricks_vrm.app:app --host 127.0.0.1 --port 8000
```

### 3. Running Automated Tests

```powershell
# Run backend pytest suite (24 tests)
$env:PYTHONPATH="backend/src"
py -3.12 -m pytest backend/tests/ -v

# Run frontend unit tests (4 tests)
cd frontend
npm test

# Run frontend build verification
npm run build
```

---

## Project Structure

```
VRMMotionGeneration/
├── README.md                           # Main Project Overview
├── INSPECTION_REPORT.md                # Initial Environment & Upstream Inspection
├── configs/
│   ├── canonical_motion.yaml           # Canonical schema settings & bone requirements
│   └── retarget_profiles/
│       └── g1_to_humanoid.example.yaml # G1-to-Humanoid bone mapping profile
├── fixtures/
│   ├── README.md                       # Fixture documentation
│   └── sample_motion.json              # Validated deterministic walking locomotion fixture
├── scripts/
│   ├── generate_fixture.py             # Deterministic fixture generator
│   ├── validate_environment.py         # Hardware, Python & checkpoint readiness checker
│   └── validate_motion.py              # CLI validator for CanonicalHumanoidMotion documents
├── backend/
│   ├── pyproject.toml                  # Backend package configuration
│   ├── src/motionbricks_vrm/
│   │   ├── schemas/                    # Pydantic v2 CanonicalHumanoidMotion models
│   │   ├── reconstruction/             # Math utilities, G1Skeleton34 model, 6D-to-matrix
│   │   ├── retargeting/                # G1ToHumanoidRetargeter engine
│   │   ├── source_adapter/             # MotionBricks inference lifecycle manager
│   │   ├── streaming/                  # WebSocket session frame streamer
│   │   └── app.py                      # FastAPI REST and WebSocket service
│   └── tests/                          # 24 automated unit tests
├── frontend/
│   ├── package.json                    # Three.js, @pixiv/three-vrm, Vite
│   ├── index.html                      # Technical UI layout & canvas
│   ├── public/sample_motion.json       # Static offline fixture asset
│   ├── src/
│   │   ├── avatar/                     # AvatarManager (VRM + Procedural Mannequin)
│   │   ├── animation/                  # AnimationPlayer (Slerp interpolation, clock)
│   │   ├── motion/                     # In-browser schema validator
│   │   ├── transport/                  # REST & WebSocket ApiClient
│   │   ├── ui/                         # HUD components, checklists, toast alerts
│   │   └── main.js                     # Application entry point
│   └── tests/                          # Frontend math & schema tests
└── docs/
    ├── 01-requirements.md              # Functional & non-functional requirements
    ├── 02-source-analysis.md           # Upstream MotionBricks code analysis
    ├── 03-system-architecture.md       # Component architecture & principles
    ├── 04-motion-representation.md     # CanonicalHumanoidMotion/v1 specification
    ├── 05-retargeting-design.md        # Kinematic composition & mapping table
    ├── 06-api-contract.md              # REST endpoints & WebSocket protocol
    ├── 07-runtime-and-deployment.md    # Installation & troubleshooting guide
    ├── 08-testing-and-validation.md    # Automated test results & observed metrics
    ├── 09-limitations-and-licensing.md # Kinematic limitations & license review
    └── diagrams/
        ├── system-context.mmd          # System context diagram
        ├── component-architecture.mmd  # Component diagram
        ├── data-flow.mmd               # Motion data flow diagram
        ├── inference-sequence.mmd      # Sequence diagram
        ├── operational-swimlane.mmd    # Operational swimlane diagram
        ├── deployment.mmd              # Physical deployment topology
        └── runtime-state-machine.mmd   # Playback & inference state machine
```

---

## Operating Modes Comparison

| Feature | Mode A: Fixture Demo | Mode B: Real Inference |
|---|---|---|
| **GPU / CUDA Required** | No | Yes (CUDA recommended) |
| **Pretrained Weights Required** | No | Yes (`out/*.ckpt` ~2.3 GB) |
| **Model Generation** | Deterministic Gait Cycle | MotionBricks Latent Models |
| **Validation** | Strict `CanonicalHumanoidMotion/v1` | Strict `CanonicalHumanoidMotion/v1` |
| **Avatar Support** | Procedural Mannequin + Custom VRM | Procedural Mannequin + Custom VRM |
| **Status Badge** | `MODE A: FIXTURE (OFFLINE)` | `MODE B: REAL INFERENCE` |

---

## License Notice

- **Integration Source Code:** Apache License 2.0
- **Upstream MotionBricks Code:** Apache License 2.0 (Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES)
- **Model Weights:** NVIDIA Open Model License