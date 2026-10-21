# DiP-Viser Known Limitations & Technical Caveats

**Experiment**: `exp/dip-viser/`  
**Status**: `DOCUMENTED & VERIFIED`

---

## 1. Generation Latency and Non-Streaming Architecture

- **Batch-to-Playback Constraint**:  
  Empirical measurements show that the warm Real-Time Factor (RTF) on an NVIDIA GeForce GTX 1650 (4 GB VRAM) is **2.696x – 3.066x** (median: **2.918x**). Generating a 4.0-second motion takes ~10.8s to 12.3s.
- **Not a Streaming Pipeline**:  
  The current implementation buffers complete motion sequences before beginning playback. It must **not** be advertised or described as a real-time streaming pipeline until sub-horizon chunked streaming and progressive decoding are implemented.

---

## 2. Hardware and Memory Bounds

- **VRAM Sensitivity (4 GB GDDR6)**:  
  On the test machine (GTX 1650), peak VRAM allocation reaches ~1.6 GB for a 4.0-second generation. Sequences longer than 9.8 seconds or batch sizes > 1 may exceed available memory.
- **CPU Fallback Performance**:  
  Inference on CPU is supported via `--device -1`, but latency increases by approximately 5x–8x compared to GPU execution.

---

## 3. Motion Representation and Avatar Boundaries

- **Cartesian 3D Joint Positions (SMPL-22)**:  
  DiP outputs metric $(X, Y, Z)$ positions for 22 joints. It does **not** output 6D joint rotations, local Euler angles, SMPL shape betas, finger articulations, or facial blendshapes.
- **No Direct VRM Retargeting in this Experiment**:  
  As defined in the boundaries, VRM avatar retargeting, ARDY, and production web services are intentionally decoupled from this experiment. Retargeting these 22 Cartesian joint trajectories to VRM humanoid bones requires an inverse kinematics (IK) solver or rotation reconstruction pass in a separate milestone.
- **Ground Penetration and Foot Sliding**:  
  Like many diffusion motion models, foot contact loss minimizes sliding but does not guarantee strict physical zero-velocity constraints during foot strikes.

---

## 4. Upstream Compatibility Patches Applied

Three minimal, documented compatibility patches were applied to the upstream `motion-diffusion-model` clone to ensure seamless operation on Windows without mutating core algorithm logic:

1. **Windows Multiprocessing in DataLoaders (`data_loaders/get_data.py`)**:  
   Python multiprocessing on Windows uses `spawn`, which fails to pickle lambda functions. Patched `num_workers = 0 if os.name == 'nt' else 8` and used `functools.partial`.
2. **SMPL Mesh Lazy Loading (`model/rotation2xyz.py`, `model/mdm.py`)**:  
   Upstream unconditionally instantiated `SMPL()` inside `__init__`, asserting the existence of gated `SMPL_NEUTRAL.pkl` files even when generating pure Cartesian joints (`pose_rep == 'xyz'`). Patched `smpl_model` to be lazy-loaded on demand only when mesh vertex decoding is requested.
3. **Matplotlib 3.8+ RGB Buffer Compatibility (`data_loaders/humanml/utils/plot_script.py`)**:  
   Replaced deprecated `tostring_rgb()` with `fig.canvas.buffer_rgba()`.

---

## 5. Licensing and Governance

- **MDM / DiP Codebase**: MIT License (Guy Tevet et al., Tel Aviv University).
- **HumanML3D Dataset / Normalization Statistics**: Strictly for academic research and non-commercial purposes.
- **OpenAI CLIP**: MIT License.
- **Viser**: Apache 2.0 License.
- **SMPL Body Model Weights**: Not bundled or required for Cartesian 3D skeleton visualization in this experiment.
