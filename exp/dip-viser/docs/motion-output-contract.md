# Motion Output Contract & Schema Specification — DiP + Viser

**Version**: `1.0.0`  
**Date**: 2026-10-21  
**Author**: Operation Dev  
**Experiment Path**: `exp/dip-viser/`  
**Status**: `VERIFIED`

---

## 1. Upstream DiP Output Serialization (`results.npy`)

When official DiP inference completes (`sample/generate.py`), it saves a Python dictionary in NumPy format:

```python
{
    'motion': np.ndarray,      # shape: (num_samples, 22, 3, num_frames)
    'text': list[str],         # Prompt strings per sample
    'lengths': np.ndarray,     # Frame count per sample (e.g. [120])
    'num_samples': int,        # Number of distinct text prompt samples
    'num_repetitions': int     # Repetitions per prompt
}
```

### Transposition & Per-Frame View
In `sample/generate.py` line 235:
```python
motion = all_motions[sample_idx].transpose(2, 0, 1) # -> shape: (num_frames, 22, 3)
```
- Axis 0: Time frame $t \in [0, N_{\text{frames}} - 1]$.
- Axis 1: Joint index $j \in [0, 21]$.
- Axis 2: 3D spatial coordinate $(x, y, z)$ in meters.

---

## 2. Coordinate System & Kinematic Conventions

| Dimension | Specification | Notes |
| :--- | :--- | :--- |
| **Handedness** | Right-Handed Cartesian | Standard in 3D graphics and robotics |
| **$+Y$ Axis** | Upward / Vertical | Gravity points along $-Y$ |
| **$+Z$ Axis** | Forward / Anterior | Character initially faces $+Z$ |
| **$+X$ Axis** | Lateral / Character Left | $(Z \times Y = -X)$ in standard orientation |
| **Units** | Meters ($m$) | Metric scale; human height is typically $1.5\text{m} - 1.9\text{m}$ |
| **Native Frame Rate** | 20.0 FPS | $\Delta t = 0.050$ seconds per frame |
| **Ground Reference** | $y = 0.0$ | Feet ground contact occurs near $y \approx 0$ |

---

## 3. HumanML3D 22 Joint Topology & Hierarchy

Parent-to-child links for the 22 SMPLH body joints:

| Joint ID | Name | Parent ID | Parent Name | Semantic Role |
| :---: | :--- | :---: | :--- | :--- |
| **0** | `pelvis` | *None* | Root | Root body translation & orientation |
| **1** | `left_hip` | 0 | `pelvis` | Left leg root |
| **2** | `right_hip` | 0 | `pelvis` | Right leg root |
| **3** | `spine1` | 0 | `pelvis` | Lower spine |
| **4** | `left_knee` | 1 | `left_hip` | Left knee articulation |
| **5** | `right_knee` | 2 | `right_hip` | Right knee articulation |
| **6** | `spine2` | 3 | `spine1` | Mid spine |
| **7** | `left_ankle` | 4 | `left_knee` | Left ankle articulation |
| **8** | `right_ankle` | 5 | `right_knee` | Right ankle articulation |
| **9** | `spine3` | 6 | `spine2` | Upper chest / thorax |
| **10** | `left_foot` | 7 | `left_ankle` | Left foot end-effector |
| **11** | `right_foot` | 8 | `right_ankle` | Right foot end-effector |
| **12** | `neck` | 9 | `spine3` | Cervical base |
| **13** | `left_collar` | 9 | `spine3` | Left clavicle base |
| **14** | `right_collar` | 9 | `spine3` | Right clavicle base |
| **15** | `head` | 12 | `neck` | Head end-effector |
| **16** | `left_shoulder` | 13 | `left_collar` | Left shoulder joint |
| **17** | `right_shoulder`| 14 | `right_collar` | Right shoulder joint |
| **18** | `left_elbow` | 16 | `left_shoulder` | Left elbow articulation |
| **19** | `right_elbow` | 17 | `right_shoulder`| Right elbow articulation |
| **20** | `left_wrist` | 18 | `left_elbow` | Left wrist end-effector |
| **21** | `right_wrist` | 19 | `right_elbow` | Right wrist end-effector |

---

## 4. Internal Canonical Motion Schema (`MotionClip`)

Serialized to and from structured JSON or Python dataclass:

```json
{
  "schema_version": "1.0.0",
  "source_model": "DiffusionPlanner-DiP",
  "source_checkpoint": "model000600343.pt",
  "provenance": "real_inference",
  "prompt": "A person walks forward and waves.",
  "fps": 20.0,
  "num_frames": 120,
  "duration_seconds": 6.0,
  "num_joints": 22,
  "joint_names": ["pelvis", "left_hip", ...],
  "joint_parents": [-1, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 12, 13, 14, 16, 17, 18, 19],
  "coordinate_system": "RightHanded_YUp_ZForward_Metric",
  "positions": [
    [[0.0, 0.95, 0.0], [0.08, 0.91, 0.0], ...],
    ...
  ],
  "telemetry": {
    "inference_duration_sec": 1.45,
    "generated_fps": 82.7,
    "real_time_factor": 0.24,
    "device": "NVIDIA GeForce GTX 1650"
  }
}
```

### Strict Validation Rules
1. `positions` array must have shape $(N_{\text{frames}}, 22, 3)$.
2. All float values must be finite (no `NaN`, `+Inf`, `-Inf`).
3. Frame count must match timestamps ($N_{\text{frames}} = \text{duration} \times \text{fps}$).
4. Provenance flag must strictly distinguish `real_inference` from `fixture`.
