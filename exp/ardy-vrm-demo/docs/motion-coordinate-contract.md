# Motion Coordinate and Representation Contract

## 1. Coordinate System Conventions

To ensure synchronized side-by-side visualization between the **ARDY CoreSkeleton27** viewport and the **VRM Humanoid Avatar**, coordinate axes, units, and handedness are explicitly specified:

| Property | ARDY CoreSkeleton27 | Three.js World Space | VRM 1.0 Humanoid (T-Pose) |
| :--- | :--- | :--- | :--- |
| **Handedness** | Right-handed ($X \times Y = Z$) | Right-handed ($X \times Y = Z$) | Right-handed ($X \times Y = Z$) |
| **Up Vector** | $+Y$ (meters) | $+Y$ (meters) | $+Y$ (meters) |
| **Forward Vector** | $+Z$ (toes at $+0.1607$) | $-Z$ (into scene) / $+Z$ (facing camera) | $+Z$ (facing viewer) |
| **Right Arm Vector** | $-X$ (in rest pose) | $-X$ (viewer's left) | $-X$ (model's right / viewer's left) |
| **Left Arm Vector** | $+X$ (in rest pose) | $+X$ (viewer's right) | $+X$ (model's left / viewer's right) |
| **Units** | Meters ($1.0 = 1\text{m}$) | Meters ($1.0 = 1\text{m}$) | Meters ($1.0 = 1\text{m}$) |

### Camera and Viewer Orientation
The viewer stage camera is situated at $(0, 1.25, 3.2)$ targeting $(0, 0.9, 0)$. Looking from $+Z$ towards $0$:
* Characters facing $+Z$ look towards the camera, allowing clear front-facing inspection of body gestures, arm swings, and facial features.
* Walking forward corresponds to displacement advancing along $+Z$ (towards the foreground).

---

## 2. Canonical Motion Representation Schema (`UnifiedMotionPayload`)

Both the skeleton renderer and the VRM retargeter consume a shared, immutable payload structure:

```json
{
  "schema_version": "1.0.0",
  "source_model": "ARDY-Core-RP-20FPS-Horizon8",
  "prompt": "A person walks forward.",
  "seed": 42,
  "fps": 20.0,
  "total_frames": 60,
  "duration_seconds": 3.0,
  "timestamps": [0.0, 0.05, 0.10, "..."],
  "mode": "LIVE ARDY",
  "telemetry": {
    "model_name": "ARDY-Core-RP-20FPS-Horizon8",
    "device": "cuda:0",
    "prompt": "A person walks forward.",
    "seed": 42,
    "requested_duration": 3.0,
    "actual_duration": 3.0,
    "total_frames": 60,
    "fps": 20.0,
    "model_load_time_seconds": 1.24,
    "generation_time_seconds": 1.62,
    "effective_generated_fps": 37.0,
    "real_time_factor": 0.54,
    "retarget_time_ms": 3.8,
    "end_to_end_latency_ms": 1625.0,
    "peak_vram_mb": 885.4
  },
  "skeleton": {
    "bone_names": ["Hips", "Spine", "Spine1", "..."],
    "parent_indices": [-1, 0, 1, "..."],
    "joint_positions": [
      [[0.0, 0.92, 0.0], [-0.03, 1.44, -0.02], "..."],
      "..."
    ]
  },
  "vrm": {
    "bones": {
      "hips": [[0.0, 0.0, 0.0, 1.0], "..."],
      "spine": [[0.02, 0.0, -0.01, 0.99], "..."],
      "rightUpperArm": [[0.08, 0.15, 0.50, 0.84], "..."],
      "leftUpperArm": [[0.07, -0.09, -0.54, 0.83], "..."]
    },
    "root_translation": [
      [0.0, 0.92, 0.0],
      [0.0, 0.91, 0.67],
      "..."
    ]
  }
}
```

---

## 3. Root Motion Policy

1. **Origin Grounding:** When an avatar is loaded, its native foot ground offset is calculated via bounding box and applied to `vrm.scene.position.y`. The avatar's initial hips rest position is recorded: `restHipsPosition = hipsNode.position.clone()`.
2. **Relative Displacement:** At frame $t$, displacement relative to frame 0 is calculated:
   $$\Delta \vec{p}(t) = \vec{p}_{root}(t) - \vec{p}_{root}(0)$$
3. **Scene-Orientation Transformation:** If `vrm.scene` carries an initial orientation (e.g. $180^\circ$ rotation applied to legacy VRM 0.x files via `VRMUtils.rotateVRM0`), the displacement is inverted by `vrm.scene.quaternion.invert()`:
   $$\Delta \vec{p}_{local}(t) = (Q_{scene})^{-1} \cdot \Delta \vec{p}(t) \cdot Q_{scene}$$
   $$\vec{p}_{hips}(t) = \vec{p}_{hips, rest} + \Delta \vec{p}_{local}(t)$$
4. **Result:** Both the Skeleton and the Avatar advance along the identical trajectory vector in Three.js world space without warping avatar body proportions.
