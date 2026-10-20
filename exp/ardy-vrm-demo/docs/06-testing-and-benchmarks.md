# Testing Suite and Empirical Benchmark Evidence

**Document ID:** `exp/ardy-vrm-demo/docs/06-testing-and-benchmarks.md`  
**Classification:** `VERIFIED`  
**Author:** Operation Dev (Senior QA & Performance Operator)  
**Date:** October 20, 2026  

---

## 1. Automated Test Suite Results

The backend test suite was executed via `pytest` inside the isolated virtual environment:
- **Command:** `exp\ardy-vrm-demo\.venv\Scripts\python.exe -m pytest exp/ardy-vrm-demo/backend/src/ardy_vrm_demo/tests -v`
- **Result:** **13 PASSED, 0 FAILED** (Duration: 5.58s)

### Test Case Breakdown

| Test Name | Module | Status | Verification Target |
| :--- | :--- | :--- | :--- |
| `test_health_endpoint` | `test_api_endpoints.py` | `PASSED` | Vitality, GPU identification, VRAM, and checkpoint availability |
| `test_models_endpoint` | `test_api_endpoints.py` | `PASSED` | Model registry schema, CoreSkeleton27 declaration, 20 FPS |
| `test_default_sample_endpoint`| `test_api_endpoints.py` | `PASSED` | Default startup sample schema, bones dict, root positions |
| `test_generation_request_validation` | `test_api_endpoints.py` | `PASSED` | Rejection of whitespace prompts and out-of-bounds duration |
| `test_nonexistent_job_returns_404` | `test_api_endpoints.py` | `PASSED` | Error handling on invalid job IDs |
| `test_cancel_nonexistent_job`| `test_api_endpoints.py` | `PASSED` | Proper rejection of cancellation on unknown tasks |
| `test_index_and_static_serving`| `test_api_endpoints.py` | `PASSED` | Root SPA delivery and static CSS asset accessibility |
| `test_identity_matrix_to_quaternion` | `test_motion_math.py` | `PASSED` | Identity 3x3 mapping to canonical quaternion `[0, 0, 0, 1]` |
| `test_quaternion_normalization` | `test_motion_math.py` | `PASSED` | Unit Euclidean norm constraint ($\|q\| = 1.0$) |
| `test_quaternion_continuity_flip` | `test_motion_math.py` | `PASSED` | Sign-flip prevention for smooth continuous spherical interpolation |
| `test_rest_pose_forward_kinematics` | `test_motion_math.py` | `PASSED` | Forward kinematics matches canonical `REST_JOINTS_CORE` offsets |
| `test_vrm_retargeting_payload_structure` | `test_retargeting.py` | `PASSED` | 22 VRM 1.0 humanoid bone tracks and timestamps assembly |
| `test_retargeting_rejects_non_finite_values` | `test_retargeting.py` | `PASSED` | Immediate ValueError on encountering NaN or Inf values |

---

## 2. Empirical Benchmark Report

All metrics were captured using Python's `time.perf_counter()` on the active hardware:
- **Device:** `NVIDIA GeForce GTX 1650` (Driver 591.74, CUDA 13.1, PyTorch 2.6.0+cu124)
- **Model:** `ARDY-Core-RP-20FPS-Horizon8`
- **Output:** 60 frames (3.0 seconds duration at 20.0 native FPS)
- **Prompt:** `"A person walks forward in a straight line with natural arm swings."`

### Cold-Start vs. Warm-Inference Comparison

| Metric | Cold Start (Run 0) | Warm Median (5 Runs) | Warm Min | Warm Max |
| :--- | :--- | :--- | :--- | :--- |
| **Model Weights Loading** | 10.219 s | *Cached in VRAM* | -- | -- |
| **Diffusion Generation Time**| 2.828 s | **1.625 s** | 1.594 s | 1.656 s |
| **Effective Generated FPS** | 21.22 FPS | **36.92 FPS** | 36.23 FPS| 37.64 FPS|
| **Real-Time Factor (RTF)** | 0.943 | **0.542** | 0.531 | 0.552 |
| **Retargeting Time** | 47.0 ms | **0.0 ms** | 0.0 ms | 16.0 ms |
| **End-to-End Latency** | 13.187 s | **1.625 s** | 1.609 s | 1.672 s |
| **Peak VRAM Consumed** | 885.35 MB | **885.35 MB** | 885.35 MB| 885.35 MB|

> **Real-Time Factor (RTF) Interpretation:**  
> A Real-Time Factor of **0.542** indicates that the ARDY diffusion denoiser and tokenizer run at **~1.85x real-time speed** on the GTX 1650 (generating 3.0 seconds of continuous 20 FPS motion in only 1.625 seconds).

### Raw Benchmark Data

The raw benchmark runs are permanently archived in JSON format:
- Path: `exp/ardy-vrm-demo/artifacts/benchmark/results.json`
