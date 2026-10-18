# 06 - REST and WebSocket API Contract

## 1. REST Endpoints

### 1.1 `GET /api/health`
Returns service operational status, environment readiness, and checkpoint availability.

**Response `200 OK`:**
```json
{
  "status": "healthy",
  "mode_a_fixture_ready": true,
  "mode_b_real_inference_ready": false,
  "checkpoint_details": "Checkpoints unavailable for real inference: pose (~1.6GB LFS pointer), root (~391MB LFS pointer), vqvae (~273MB LFS pointer), clip (~7.5MB LFS pointer). Use git lfs pull to fetch.",
  "environment": {
    "pose_ckpt_present": true,
    "pose_ckpt_lfs": true,
    "root_ckpt_present": true,
    "root_ckpt_lfs": true,
    "vqvae_ckpt_present": true,
    "vqvae_ckpt_lfs": true
  }
}
```

---

### 1.2 `GET /api/motion/schema`
Returns the JSON Schema definition for `CanonicalHumanoidMotion/v1`.

---

### 1.3 `GET /api/motion/fixture`
Returns the validated Mode A locomotion fixture (`sample_motion.json`).

**Response `200 OK`:**
Returns the complete JSON document adhering to `CanonicalHumanoidMotion/v1`.

---

### 1.4 `POST /api/motion/validate`
Validates an arbitrary motion document against mathematical and structural schema constraints.

**Request Body:**
```json
{
  "motion": { ... }
}
```

**Response `200 OK` (Valid):**
```json
{
  "valid": true,
  "schema_version": "CanonicalHumanoidMotion/v1",
  "frame_count": 60,
  "duration": 1.9667,
  "errors": []
}
```

**Response `200 OK` (Invalid):**
```json
{
  "valid": false,
  "schema_version": null,
  "frame_count": null,
  "duration": null,
  "errors": [
    "[frames -> 0 -> bones -> hips -> rotation] Quaternion norm deviates from unit length"
  ]
}
```

---

### 1.5 `POST /api/motion/retarget`
Retargets an array of 414-dimensional raw MotionBricks feature vectors into a `CanonicalHumanoidMotion/v1` document.

**Request Body:**
```json
{
  "raw_features": [
    [0.0, 0.95, 0.0, ... 414 floats ...],
    [0.0, 0.95, 0.1, ... 414 floats ...]
  ],
  "fps": 30.0,
  "profile_name": "g1_to_humanoid_standard"
}
```

---

### 1.6 `POST /api/inference/generate`
Executes real MotionBricks inference when genuine model weights are available.

**Request Body:**
```json
{
  "command": "walk",
  "duration_seconds": 2.0
}
```

**Error Response `503 Service Unavailable` (When weights are LFS pointers):**
```json
{
  "detail": {
    "error": "Real MotionBricks inference unavailable",
    "reason": "Checkpoints unavailable for real inference: pose (~1.6GB LFS pointer)...",
    "suggested_action": "Fetch checkpoints via `git lfs pull --include=\"motionbricks/out/**\"` or use Mode A Fixture Demo."
  }
}
```

---

## 2. WebSocket Streaming Contract

- **Endpoint:** `ws://<host>:8000/ws/motion`
- **Protocol:** JSON message frames.

### Client Commands
- `{"command": "stream_fixture", "loop": true, "speed": 1.0}`: Streams the sample fixture frame by frame.
- `{"command": "ping"}`: Health ping.

### Server Packets
- **Motion Header Packet:**
  ```json
  {
    "type": "motion_header",
    "schema": "CanonicalHumanoidMotion/v1",
    "metadata": { ... }
  }
  ```
- **Motion Frame Packet:**
  ```json
  {
    "type": "motion_frame",
    "frame": {
      "timestamp": 0.033333,
      "frame_index": 1,
      "root": { ... },
      "bones": { ... },
      "contacts": { ... }
    }
  }
  ```
- **Motion Ended Packet:**
  ```json
  {
    "type": "motion_ended"
  }
  ```
