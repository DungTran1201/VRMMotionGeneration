---
name: motionbricks-real-inference
description: Integrate real upstream MotionBricks inference safely and honestly.
---

\
# MotionBricks Real Inference Integration

## Inspect first
- Read the pinned upstream README, inference demo, model loader, config files, decoder and model/checkpoint license.
- Identify the exact public functions and tensor shapes of the pinned revision. Never guess function names or checkpoint compatibility.
- Check Git LFS pointers versus complete weights, required Python/Torch/CUDA versions and supported devices.

## Implement
- Create a lifecycle with states `unavailable`, `loading`, `ready`, `failed`, `running`, `stopped` (adapt to existing API contract if already established).
- `ready` is allowed only after model objects were actually constructed and a smoke inference/decode succeeds.
- Separate model loading, command normalization, inference, source decoding, G1 reconstruction, retargeting, canonical validation and streaming.
- Preserve fixture mode as an explicit source. Never use fixture output when real inference fails unless caller explicitly selects fixture mode.
- Support deterministic shutdown/resource cleanup and avoid loading one copy of GPU weights per WebSocket client.
- Return actionable, non-sensitive errors for absent weights, LFS pointer files, incompatible checkpoints, missing CUDA and inference exceptions.

## Tests
- Mock tests for lifecycle state/error paths.
- Integration smoke test gated on an explicit checkpoint path/environment variable.
- Test that “ready” without executing the loader is impossible.
- Test that real-inference failure never yields `source=motionbricks` fixture data.
- Measure model inference separately from decoding/retargeting/network delay.
