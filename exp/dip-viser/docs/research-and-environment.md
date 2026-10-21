# Research & Environment Architecture — DiP + Viser Experiment

**Date**: 2026-10-21  
**Author**: Operation Dev  
**Experiment Root**: `exp/dip-viser/`  
**Classification**: `VERIFIED`

---

## 1. Upstream Research References & Inspections

| Reference | Target / Asset | Inspected Files / Lines | Checked Date | Verification State |
| :--- | :--- | :--- | :--- | :--- |
| **MDM / DiP Repository** | `https://github.com/GuyTevet/motion-diffusion-model` | Commit `ef8edce6a53c6ab19e53b4d4dcf15bc0bc60a778` | 2026-10-21 | `VERIFIED` |
| **DiP Instructions** | `DiP.md` | Lines 1–142 (`save/DiP_no-target_10steps_context20_predict40`) | 2026-10-21 | `VERIFIED` |
| **CLoSD Hugging Face Repo** | `guytevet/CLoSD` | `checkpoints/dip/DiP_no-target_10steps_context20_predict40/` | 2026-10-21 | `VERIFIED` |
| **DiP Checkpoint** | `model000600343.pt` | Size: 232,011,477 bytes (~232 MB), SHA-256 available | 2026-10-21 | `VERIFIED` |
| **DiP Training Config** | `args.json` | 74 parameters: `trans_dec`, `diffusion_steps: 10`, `text_encoder_type: bert`, `num_frames: 60`, `context_len: 20`, `pred_len: 40` | 2026-10-21 | `VERIFIED` |
| **Viser Project** | `https://viser.studio/` | Viser Python Server, 3D Canvas, Timeline & GUI API | 2026-10-21 | `VERIFIED` |
| **HumanML3D Dataset** | `https://github.com/EricGuo5513/HumanML3D` | `Mean.npy`, `Std.npy`, `test.txt`, 22 joints kinematics | 2026-10-21 | `VERIFIED` |

---

## 2. DiP (Diffusion Planner) Architectural Mechanics

1. **Model Architecture**:
   - Transformer Decoder (`arch: trans_dec`), 8 layers, 512 latent dimensions (`latent_dim: 512`).
   - Text encoder: DistilBERT (`distilbert/distilbert-base-uncased`, 768-dim embedding mapped to 512-dim).
   - Diffusion schedule: 10 diffusion steps with cosine schedule (`noise_schedule: cosine`), vastly faster than original 1000-step MDM.
2. **Autoregressive Horizon**:
   - `context_len = 20` frames (1.0 second at 20 FPS).
   - `pred_len = 40` frames (2.0 seconds at 20 FPS).
   - Total window per call = 60 frames. At each iteration, the model takes the clean 20-frame prefix and predicts the next 40-frame motion chunk.
3. **Motion Feature Representation**:
   - Raw feature vector dimension: **263** (HumanML3D representation):
     - `root_rot_velocity`: 1 dim
     - `root_linear_velocity`: 2 dims (horizontal XZ)
     - `root_y`: 1 dim (vertical position)
     - `ric_data` (positions relative to root): $(22 - 1) \times 3 = 63$ dims
     - `rot_data` (6D rotations): $(22 - 1) \times 6 = 126$ dims
     - `local_velocity`: $22 \times 3 = 66$ dims
     - `foot_contact`: 4 dims
     - Total: $1 + 2 + 1 + 63 + 126 + 66 + 4 = 263$ dimensions.
4. **Kinematic Reconstruction (`recover_from_ric`)**:
   - Un-normalization: $x_{\text{unnorm}} = x \times \text{std} + \text{mean}$.
   - Position recovery: Root rotation angle integrated from angular velocity, root XZ integrated from horizontal velocities, root Y placed directly.
   - 21 child joints rotated back by root orientation and offset by root position.
   - Result: $(N_{\text{frames}}, 22, 3)$ Cartesian 3D joint positions in meters.

---

## 3. HumanML3D Skeleton Hierarchy

The 22 SMPLH body joints in `HML_JOINT_NAMES`:
```text
0: pelvis (Root)
├── 1: left_hip ── 4: left_knee ── 7: left_ankle ── 10: left_foot
├── 2: right_hip ── 5: right_knee ── 8: right_ankle ── 11: right_foot
└── 3: spine1 ── 6: spine2 ── 9: spine3
    ├── 12: neck ── 15: head
    ├── 13: left_collar ── 16: left_shoulder ── 18: left_elbow ── 20: left_wrist
    └── 14: right_collar ── 17: right_shoulder ── 19: right_elbow ── 21: right_wrist
```

Kinematic chains from `paramUtil.t2m_kinematic_chain`:
- Chain 1 (Right leg): `[0, 2, 5, 8, 11]`
- Chain 2 (Left leg): `[0, 1, 4, 7, 10]`
- Chain 3 (Spine & Head): `[0, 3, 6, 9, 12, 15]`
- Chain 4 (Right arm): `[9, 14, 17, 19, 21]`
- Chain 5 (Left arm): `[9, 13, 16, 18, 20]`

---

## 4. Hardware Sizing & Compatibility Decisions

- **GPU Constraints**: The GTX 1650 provides 4 GB VRAM (~2.9 GB free).
  - DiP weights: ~232 MB.
  - DistilBERT weights: ~260 MB.
  - Transformer activation memory: < 300 MB for batch size 1.
  - Total inference VRAM requirement is under 1.2 GB, fitting safely into available VRAM.
  - CPU fallback is fully supported with identical numerical results should VRAM or CUDA experience contention.
- **Python Compatibility**:
  - Python 3.10.20 provides clean compatibility across PyTorch 2.x, Transformers 4.x, and Viser 0.2.x on Windows without C++ compiler build requirements.
