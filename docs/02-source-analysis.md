# 02 - Upstream MotionBricks Source Analysis

## 1. Upstream Source Repository & Commit

- **Repository:** `https://github.com/NVlabs/GR00T-WholeBodyControl.git`
- **Analyzed Commit SHA:** `45c03facbf848e0c743091b7d9c17952096ff908`
- **Primary Source Modules:**
  - `motionbricks/motionbricks/motion_backbone/inference/motion_inference.py`
  - `motionbricks/motionbricks/motion_backbone/models/pose_model.py`
  - `motionbricks/motionbricks/motion_backbone/models/root_model.py`
  - `motionbricks/motionbricks/motion_backbone/neural_modules/pose_backbone.py`
  - `motionbricks/motionbricks/motion_backbone/neural_modules/root_backbone.py`
  - `motionbricks/motionbricks/vqvae/neural_modules/vqvae.py`
  - `motionbricks/motionbricks/helper/mujoco_helper.py`
  - `motionbricks/motionbricks/motionlib/core/skeletons/g1.py`
  - `motionbricks/docs/motion_representation.md`

---

## 2. Real Inference Architecture & Flow

MotionBricks generates motion through a sequential two-stage generative model:

```
[Target Keyframes / Initial State]
               │
               ▼
   1. Root Trajectory Model
      (Predicts frame count & root XYZ + heading trajectory)
               │
               ▼
   2. Pose Model & Token Sampler
      (Samples discrete motion tokens via masked autoregressive / non-autoregressive logits)
               │
               ▼
   3. VQ-VAE Decoder
      (Transforms discrete codebook tokens into continuous 414-dim motion features)
               │
               ▼
   4. Recentering & World Frame Alignment
      (Re-applies initial heading and horizontal root offsets)
               │
               ▼
   Decoded Feature Tensor [Batch, Frames, 414]
```

---

## 3. Detailed Output Feature Representation (`DualRootGlobalJoints`)

The decoded feature representation is **414-dimensional** per frame in the global representation (`GlobalRootGlobalJoints`):

| Slice Indices | Feature Name | Dims | Mathematical Description & Unit |
|---|---|---|---|
| `[0:3]` | `global_root_pos` | 3 | World $(X, Y, Z)$ root coordinates in meters. Initial frame horizontal $X, Z$ are normalized to $(0, 0)$. |
| `[3:5]` | `global_root_heading` | 2 | $(\cos\theta, \sin\theta)$ heading angle around the vertical $Y$-axis. |
| `[5:104]` | `ric_data` | 99 | World joint positions for 33 non-root joints relative to projected horizontal root: $P^{joint}_i - (X_{root}, 0, Z_{root})$. |
| `[104:308]` | `global_rot_data` | 204 | Continuous 6D rotation representation (Zhou et al., CVPR 2019) for all 34 joints in world frame. |
| `[308:410]` | `local_vel` | 102 | Per-joint linear velocities in world frame (finite differences $\Delta P / \Delta t$). |
| `[410:414]` | `foot_contacts` | 4 | Binary contact flags: `[left_ankle, left_toe, right_ankle, right_toe]`. |

---

## 4. Coordinate System Conventions

| System | Up Axis | Forward Axis | Right Axis | Handedness | Notes |
|---|---|---|---|---|---|
| **MotionBricks** | $+Y$ | $+Z$ | $+X$ | Right-handed | Native model training space |
| **Canonical glTF / VRM** | $+Y$ | $-Z$ | $+X$ | Right-handed | Standard WebGL / glTF 2.0 convention |
| **MuJoCo** | $+Z$ | $+X$ | $+Y$ | Right-handed | Physics simulation coordinate space |

### Transformation Between MotionBricks and Canonical VRM
The transformation between MotionBricks $(+Z\text{ forward})$ and Canonical glTF $(-Z\text{ forward})$ is an exact $180^\circ$ rotation around the vertical $Y$-axis:
$$R_Y(180^\circ) = \begin{bmatrix} -1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & -1 \end{bmatrix}$$
- Position mapping: $P_{canonical} = [-X_{mb}, Y_{mb}, -Z_{mb}]$
- Orientation mapping: $R_{canonical} = R_Y(180^\circ) \cdot R_{mb} \cdot R_Y(180^\circ)^T$

---

## 5. Source Skeleton Hierarchy (`G1Skeleton34`)

The kinematic tree is derived from the Unitree G1 humanoid robot with 32 active hinge joints and 2 dummy toe base joints:

```
pelvis_skel (0, root)
├── left_hip_pitch_skel (1)
│   └── left_hip_roll_skel (2)
│       └── left_hip_yaw_skel (3)
│           └── left_knee_skel (4)
│               └── left_ankle_pitch_skel (5)
│                   └── left_ankle_roll_skel (6)
│                       └── left_toe_base (7)
├── right_hip_pitch_skel (8)
│   └── right_hip_roll_skel (9)
│       └── right_hip_yaw_skel (10)
│           └── right_knee_skel (11)
│               └── right_ankle_pitch_skel (12)
│                   └── right_ankle_roll_skel (13)
│                       └── right_toe_base (14)
└── waist_yaw_skel (15)
    └── waist_roll_skel (16)
        └── waist_pitch_skel (17)
            ├── left_shoulder_pitch_skel (18)
            │   └── left_shoulder_roll_skel (19)
            │       └── left_shoulder_yaw_skel (20)
            │           └── left_elbow_skel (21)
            │               └── left_wrist_roll_skel (22)
            │                   └── left_wrist_pitch_skel (23)
            │                       └── left_wrist_yaw_skel (24)
            │                           └── left_hand_roll_skel (25)
            └── right_shoulder_pitch_skel (26)
                └── right_shoulder_roll_skel (27)
                    └── right_shoulder_yaw_skel (28)
                        └── right_elbow_skel (29)
                            └── right_wrist_roll_skel (30)
                                └── right_wrist_pitch_skel (31)
                                    └── right_wrist_yaw_skel (32)
                                        └── right_hand_roll_skel (33)
```

---

## 6. Pretrained Checkpoint Findings

- Upstream repositories store pretrained model weights as **Git-LFS pointer files** (~135 bytes each):
  - `out/motionbricks_pose/version_1/checkpoints/model-step=2000000.ckpt` (~1.64 GB actual binary)
  - `out/motionbricks_root/version_1/checkpoints/model-step=2000000.ckpt` (~391 MB actual binary)
  - `out/motionbricks_vqvae/version_1/checkpoints/model-step=2000000.ckpt` (~273 MB actual binary)
  - `out/G1-clip.ckpt` (~7.5 MB actual binary)
- **Verified Fact:** In clean clones without `git lfs pull`, these checkpoints are pointer text files. Our source adapter dynamically checks for LFS pointers and prevents mock executions.
- **Normalization Statistics:** `mean.npy` and `std.npy` (418 floats each) are verified binary numpy arrays present in the upstream release.
