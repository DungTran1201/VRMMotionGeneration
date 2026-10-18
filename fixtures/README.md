# Motion Fixtures Directory

This directory contains verified, deterministic test fixtures formatted according to the **`CanonicalHumanoidMotion/v1`** schema.

## `sample_motion.json`

- **Schema:** `CanonicalHumanoidMotion/v1`
- **Origin / Source:** `fixture` (Mode A: Offline Demo)
- **Duration:** 1.9667 seconds (60 frames sampled at 30.0 fps)
- **Coordinate System:** `glTF_Y_UP_Z_BACK_X_RIGHT` (+X Right, +Y Up, -Z Forward)
- **Rotation Format:** `quaternion_xyzw` ($[x, y, z, w]$ unit quaternions)
- **Description:** A biomechanically plausible bipedal walking gait cycle containing:
  - Dynamic root displacement along $-Z$ with vertical bounce ($Y$) and lateral hip sway ($X$).
  - Counter-rotational spine twist to maintain balance.
  - Alternating hip flexion/extension, knee articulation, and ankle strike.
  - Synchronized arm swings opposite to leg phases.
  - Discrete binary foot contacts (`leftFoot`, `rightFoot`, `leftToe`, `rightToe`).

### Usage

1. **Frontend Offline Mode:** The Three.js/VRM viewer loads this fixture directly for offline playback without requiring a backend or GPU.
2. **Backend Validation:** The FastAPI backend serves and validates this fixture via `GET /api/motion/fixture` and `POST /api/motion/validate`.
3. **CLI Validation:** Run `python scripts/validate_motion.py fixtures/sample_motion.json` to verify schema conformance.
