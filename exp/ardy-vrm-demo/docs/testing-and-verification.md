# Testing and Verification Evidence

## 1. Automated Test Execution Record

### Test Suite 1: Backend Integration & Frontend Contracts (Pytest)
Command executed:
```powershell
$env:PYTHONPATH = "backend/src;vendor/ardy"
& ".\.venv\Scripts\python.exe" -m pytest backend/src/ardy_vrm_demo/tests
```
- **Exit Code:** `0` (Success)
- **Results:** `19 passed in 5.12s`
  - `test_api_endpoints.py`: 7 passed (health, models, samples, request validation, 404, cancel, static serving)
  - `test_frontend_contracts.py`: 6 passed (no hardcoded fake metrics, truthful placeholders, single file input, stage canvas, import map, fullscreen CSS)
  - `test_motion_math.py`: 4 passed (forward kinematics, rotation matrices, quaternions, normalization)
  - `test_retargeting.py`: 2 passed (payload structure, non-finite value rejection)

### Test Suite 2: Frontend Unit Tests (Node.js Test Runner)
Command executed:
```powershell
node --test frontend/tests/test_vrm_loader_contract.js
```
- **Exit Code:** `0` (Success)
- **Results:** `8 passed, 0 failed in 95ms`
  - `VrmManager: rejects non-existent or null file` (PASS)
  - `VrmManager: rejects file with invalid extension` (PASS)
  - `VrmManager: rejects empty file (0 bytes)` (PASS)
  - `VrmManager: rejects oversized file (>100MB)` (PASS)
  - `VrmManager: rejects GLTF file that lacks VRM metadata with actionable message` (PASS)
  - `VrmManager: loads valid VRM 1.0 avatar, computes bounds, and does NOT rotate VRM 1.0` (PASS)
  - `VrmManager: applies VRMUtils.rotateVRM0 only when VRM 0.x is detected` (PASS)
  - `VrmManager: replacing avatar cleanly disposes old scene and resources` (PASS)

---

## 2. Live Browser E2E Session Verification

Live verification was conducted via headless browser automation:
- **Server:** FastAPI / Uvicorn server running on `http://127.0.0.1:8000/`.
- **Session Recording:** Saved to artifacts as WebP video:
  `ardy_fullscreen_stage_demo_1792512092581.webp`
- **Observed Checklist:**
  - [x] Full-bleed 3D stage canvas occupies 100% of browser viewport (`100dvw × 100dvh`).
  - [x] Zero main-page scrolling or scrollbars at desktop resolutions.
  - [x] 3D world floor grid and stage lighting render cleanly without artifacts.
  - [x] Browser console has **0 errors** and **0 warnings** (no Three.js version collisions).
  - [x] Floating Motion Controls window dragged smoothly by its title bar.
  - [x] Floating window collapse/expand toggle tested and functional.
  - [x] Floating window opacity slider tested and functional.
  - [x] Preset conditioning prompt chips populate the prompt textarea on click.
  - [x] Synchronized bottom timeline scrubber plays, pauses, seeks, and updates frame counter.
  - [x] Truthful telemetry HUD displays `—` for unmeasured fields, with genuine live renderer FPS counter.

---

## 3. Manual Verification Checklist

| Scenario | Steps to Reproduce | Expected Result | Status |
|---|---|---|---|
| Load VRM Avatar via Button | Click "Load / Replace VRM", pick `.vrm` file | Avatar loads, feet grounded at y=0, metadata displayed | `VERIFIED` |
| Load VRM via Drag & Drop | Drag `.vrm` file over 3D viewport and drop | Stage overlay appears, drops, avatar parses cleanly | `VERIFIED` |
| Corrupt / Non-VRM File | Select a standard `.glb` or corrupt file | Toast shows actionable error; UI not stuck in loading | `VERIFIED` |
| Floating Window Drag | Drag header across screen | Moves smoothly, clamps to viewport edges | `VERIFIED` |
| Floating Window Opacity | Adjust opacity slider from 0.9 to 0.5 | Background becomes translucent, revealing 3D world | `VERIFIED` |
| Camera Framing | Click "Avatar", "Skeleton", or "Frame All" | OrbitControls target transitions smoothly to target | `VERIFIED` |
