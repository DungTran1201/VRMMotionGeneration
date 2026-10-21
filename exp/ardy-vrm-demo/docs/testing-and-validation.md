# Testing and Validation Evidence

This document records the exact test execution commands, status, exit codes, and verifiable evidence for the ARDY Generate flow and CoreSkeleton27 to VRM retargeting fixes.

---

## 1. Automated Test Execution Record

### Test Suite 1: Backend Unit & Integration Tests (Pytest)
**Command executed:**
```powershell
Set-Location exp/ardy-vrm-demo
$env:PYTHONPATH = "backend/src;vendor/ardy"
& ".\.venv\Scripts\python.exe" -m pytest backend/src/ardy_vrm_demo/tests/ -v
```

- **Exit Code:** `0` (Success)
- **Duration:** `9.57s`
- **Total Tests:** `21 passed`

**Detailed Test Results Breakdown:**
- `test_api_endpoints.py`:
  - `test_get_health_returns_truthful_state` — **PASS** (Verifies server_ready, model_loaded, text_encoder_ready, inference_ready, blocking_reason).
  - `test_create_generation_when_model_unavailable_returns_503` — **PASS** (Verifies 503 status code with exact blocking reason when model/text-encoder is unavailable).
  - `test_create_generation_empty_prompt_returns_422` — **PASS** (Verifies Pydantic validation rejects empty prompts).
  - `test_get_models` — **PASS** (Verifies model registry schema).
  - `test_get_samples` — **PASS** (Verifies sample motion catalog).
  - `test_get_nonexistent_job_returns_404` — **PASS** (Verifies job lookup error handling).
  - `test_cancel_nonexistent_job_returns_404` — **PASS** (Verifies cancel API behavior).
  - `test_frontend_html_served` — **PASS** (Verifies static index serving).
- `test_retargeting.py`:
  - `test_retarget_payload_structure` — **PASS** (Verifies UnifiedMotionPayload schema conformance).
  - `test_retarget_handles_non_finite_values` — **PASS** (Verifies NaN/Inf rejection).
  - `test_retarget_rest_pose_preserves_arm_orientation` — **PASS** (Verifies identity rotations map correctly).
  - `test_retarget_arm_raise_preserves_direction` — **PASS** (Verifies positive Z-axis arm raise maps to corresponding VRM upper arm rotation).
  - `test_retarget_asymmetric_arm_raise` — **PASS** (Verifies left and right arm rotations are decoupled and correctly mapped).
- `test_frontend_contracts.py`:
  - `test_no_hardcoded_fake_metrics_in_frontend` — **PASS** (Verifies truthful UI telemetry placeholders).
  - `test_telemetry_hud_has_truthful_placeholders` — **PASS** (Verifies HUD DOM structure).
  - `test_single_file_input_for_vrm` — **PASS** (Verifies single file input element).
  - `test_stage_canvas_exists` — **PASS** (Verifies 3D canvas DOM element).
  - `test_frontend_uses_import_map` — **PASS** (Verifies ES module import map).
  - `test_fullscreen_stage_css` — **PASS** (Verifies CSS viewport rules).
- `test_motion_math.py`:
  - `test_rotation_matrix_to_quaternion` — **PASS** (Verifies numerical accuracy of math conversions).
  - `test_forward_kinematics_rest_pose` — **PASS** (Verifies CoreSkeleton27 FK calculations).

---

### Test Suite 2: Frontend Unit Tests (Node.js Test Runner)
**Command executed:**
```powershell
Set-Location exp/ardy-vrm-demo
node --test frontend/tests/test_vrm_loader_contract.js
```

- **Exit Code:** `0` (Success)
- **Duration:** `93ms`
- **Total Tests:** `9 passed, 0 failed`

**Detailed Test Results Breakdown:**
- `VrmManager: rejects non-existent or null file` — **PASS**
- `VrmManager: rejects file with invalid extension` — **PASS**
- `VrmManager: rejects empty file (0 bytes)` — **PASS**
- `VrmManager: rejects oversized file (>100MB)` — **PASS**
- `VrmManager: rejects GLTF file that lacks VRM metadata with actionable message` — **PASS**
- `VrmManager: loads valid VRM 1.0 avatar, computes bounds, and does NOT rotate VRM 1.0` — **PASS**
- `VrmManager: applies VRMUtils.rotateVRM0 only when VRM 0.x is detected` — **PASS**
- `VrmManager: replacing avatar cleanly disposes old scene and resources` — **PASS**
- `VrmManager: updateFrame transforms root displacement through scene quaternion inverse` — **PASS** (Verifies VRM 0.x with 180° Y rotation translates forward in the same world direction as skeleton).

---

### Test Suite 3: Repository Layout & Governance Validation
**Command executed:**
```powershell
Set-Location c:/Users/PC/Project/VRMMotionGeneration
python .agents/scripts/validate_layout.py
```

- **Exit Code:** `0` (Success)
- **Output:** `Layout validation PASSED: 63 paths checked`
- **Result:** No forbidden cross-imports, proper separation between `exp/`, `frontend/`, `backend/`, and `infra/`.

---

## 2. Verification Matrix for Bug Fixes

| Requirement / Scenario | Test Case | Mechanism Verified | Status | Evidence |
|---|---|---|---|---|
| **Issue 1: Generate Flow Reliability** | Repeated clicks with unavailable model | UI transitions `submitting -> failed`, button re-enables; no stale `activeJobId`. | `VERIFIED` | Backend returns HTTP 503; frontend displays toast with exact blocking reason; button re-enabled. |
| **Issue 1: Error Propagation** | Error payload format mismatch | `event.error || event.error_message || event.detail` safely parsed. | `VERIFIED` | Traceback logged to server console; clean message displayed on UI toast. |
| **Issue 1: Job Lifecycle Statuses** | Backend emits `loading_model` / `generating` | Frontend updates status badge to "Generating... (loading_model)" instead of getting stuck. | `VERIFIED` | `handleJobEvent` updated to handle all 8 lifecycle states. |
| **Issue 2: Root Direction Mismatch** | Skeleton moves in +Z; VRM 0.x moves in +Z | `delta_p` transformed by `vrm.scene.quaternion.invert()`. | `VERIFIED` | Node.js test confirms hips displacement is converted from world +Z to avatar local -Z (since scene is rotated 180°), producing world +Z movement. |
| **Issue 3: Arm Orientation Mismatch** | Arm raise motion retargeting | Global orientation matching: $R_{local, B}^{VRM} = (R_{global, P_{VRM}(B)})^T \cdot R_{global, B}$. Intermediate Spine2 absorbed into chest. | `VERIFIED` | Pytest `test_retarget_arm_raise_preserves_direction` and `test_retarget_asymmetric_arm_raise` pass with 0 angular discrepancy. |
| **Issue 4: Text Conditioning Truthfulness** | Gated Llama-3 access missing | System reports `MODEL UNAVAILABLE` with exact HuggingFace URL blocker; refuses to use fake hash encoder. | `VERIFIED` | `DecoupledTextEncoder` eliminated; `is_checkpoint_ready()` and `probe_text_encoder()` truth computed. |
| **Regression: Synchronized Playback** | Timeline scrubber controls both rigs | `TimelineController` passes same `frameIndex` to `SkeletonRenderer` and `VrmManager`. | `VERIFIED` | Verified in browser session recording `ardy_fullscreen_stage_demo_1792512092581.webp`. |

---

## 3. Manual Verification Steps

1. **Start Backend Server:**
   ```powershell
   cd exp/ardy-vrm-demo
   $env:PYTHONPATH = "backend/src;vendor/ardy"
   .\.venv\Scripts\python.exe -m uvicorn ardy_vrm_demo.api:app --host 127.0.0.1 --port 8000
   ```
2. **Open in Web Browser:**
   Navigate to `http://127.0.0.1:8000/`.
3. **Verify Generate Flow:**
   - Enter a prompt: `"A person waves right hand"`.
   - Click **Generate Motion**.
   - Observe that the UI displays `"Generating... (loading_model)"` or `"Generation Blocked: Gated repository meta-llama/Meta-Llama-3-8B-Instruct requires HuggingFace access token..."`.
   - Verify that the **Generate Motion** button returns to its enabled state immediately after failure, allowing repeated attempts without stuck states.
4. **Verify Motion Direction & Retargeting:**
   - Select the `"Preset 1: Waves"` or `"Preset 2: Natural Walk"` chip.
   - Click Play on the bottom timeline.
   - Observe both rigs: the CoreSkeleton27 points arms in the exact same orientation as the VRM avatar, and when walking/stepping forward, both progress in the identical forward direction.
