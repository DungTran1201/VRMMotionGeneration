# 04 - CanonicalHumanoidMotion/v1 Specification

## 1. Specification Overview

`CanonicalHumanoidMotion/v1` is an open, model-agnostic, engine-independent JSON schema for skeletal humanoid motion. It defines positions, local bone orientations, and contact states.

### Key Conventions
- **Schema Identifier:** `CanonicalHumanoidMotion/v1`
- **Coordinate System:** `glTF_Y_UP_Z_BACK_X_RIGHT` ($+Y$ is Up, $+X$ is Right, $-Z$ is Forward, Right-handed).
- **Units:** Linear measurements in meters; angular velocities in radians/second; timestamps in seconds.
- **Rotation Format:** Unit quaternions serialized strictly as `[x, y, z, w]`.
- **Root Motion:** Applied strictly to the `root` object. Local bone rotations are relative to their parent bone.

---

## 2. JSON Schema Definition & Example

```json
{
  "schema": "CanonicalHumanoidMotion/v1",
  "metadata": {
    "source": "fixture",
    "fps": 30.0,
    "duration": 1.966667,
    "num_frames": 60,
    "coordinate_system": "glTF_Y_UP_Z_BACK_X_RIGHT",
    "units": "meters",
    "rotation_format": "quaternion_xyzw",
    "retargeting_profile": "deterministic_bipedal_walk_v1",
    "retargeting_version": "1.0.0",
    "generator_info": "generate_fixture.py"
  },
  "frames": [
    {
      "timestamp": 0.0,
      "frame_index": 0,
      "root": {
        "position": [0.0, 0.98, -0.0],
        "rotation": [0.0, 0.0, 0.0, 1.0]
      },
      "bones": {
        "hips": { "rotation": [0.0, 0.0, 0.0, 1.0] },
        "spine": { "rotation": [0.0, 0.0, 0.0, 1.0] },
        "leftUpperLeg": { "rotation": [0.0, 0.0, 0.0, 1.0] },
        "leftLowerLeg": { "rotation": [0.0, 0.0, 0.0, 1.0] },
        "leftFoot": { "rotation": [0.0, 0.0, 0.0, 1.0] },
        "rightUpperLeg": { "rotation": [0.0, 0.0, 0.0, 1.0] },
        "rightLowerLeg": { "rotation": [0.0, 0.0, 0.0, 1.0] },
        "rightFoot": { "rotation": [0.0, 0.0, 0.0, 1.0] }
      },
      "contacts": {
        "leftFoot": true,
        "rightFoot": false,
        "leftToe": false,
        "rightToe": false
      },
      "diagnostics": {
        "warnings": [],
        "approximate_bones": ["chest", "neck", "head"]
      }
    }
  ]
}
```

---

## 3. Humanoid Bone Naming Conventions

The schema aligns directly with the official **VRM Humanoid 1.0** bone taxonomy:

| Category | Bone Identifiers |
|---|---|
| **Core / Torso** | `hips`, `spine`, `chest`, `upperChest`, `neck`, `head` |
| **Left Leg** | `leftUpperLeg`, `leftLowerLeg`, `leftFoot`, `leftToes` |
| **Right Leg** | `rightUpperLeg`, `rightLowerLeg`, `rightFoot`, `rightToes` |
| **Left Arm** | `leftShoulder`, `leftUpperArm`, `leftLowerArm`, `leftHand` |
| **Right Arm** | `rightShoulder`, `rightUpperArm`, `rightLowerArm`, `rightHand` |

---

## 4. Validation Rules

1. **Schema Check:** Rejects any document where `schema != "CanonicalHumanoidMotion/v1"`.
2. **Numeric Integrity:** Rejects `NaN`, `+Infinity`, or `-Infinity` in any vector or quaternion.
3. **Quaternion Norms:** Every rotation vector $[x, y, z, w]$ must satisfy $|\|q\| - 1.0| \le 10^{-3}$.
4. **Monotonic Timestamps:** For each frame $i > 0$, $t_i \ge t_{i-1}$.
5. **Frame Count Consistency:** Number of frame entries must exactly equal `metadata.num_frames`.
6. **Duration Consistency:** Metadata duration must match $(num\_frames - 1) / fps$ within a tolerance of $\pm 2 / fps$.
7. **Bone Name Validation:** Disallows unregistered bone names to ensure target rig compatibility.
