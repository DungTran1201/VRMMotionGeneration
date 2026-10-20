# Motion Format and VRM Humanoid Retargeting

**Document ID:** `exp/ardy-vrm-demo/docs/03-motion-format-and-retargeting.md`  
**Classification:** `VERIFIED`  
**Author:** Operation Dev  
**Date:** October 20, 2026  

---

## 1. Upstream ARDY CoreSkeleton27 Topology

The ARDY Core motion representation is based on a 27-joint humanoid rig:
- **Coordinate System:** Right-handed, Y-up, Z-forward (+Z forward, +Y up, +X left).
- **Units:** Meters.
- **Native Sampling Rate:** 20.0 FPS.
- **Autoregressive Horizon:** 8 frames per generation window.

### Joint Hierarchy & Parent Indices

| Index | Joint Name | Parent Name | Parent Index | Description |
| :--- | :--- | :--- | :--- | :--- |
| **0** | `Hips` | *(None / Root)* | `-1` | Pelvis center of gravity & root translation |
| **1** | `Spine` | `Hips` | `0` | Lower lumbar spine |
| **2** | `Spine1` | `Spine` | `1` | Mid-lumbar spine |
| **3** | `Spine2` | `Spine1` | `2` | Lower thoracic spine |
| **4** | `Spine3` | `Spine2` | `3` | Upper thoracic spine / chest |
| **5** | `Neck` | `Spine3` | `4` | Cervical spine |
| **6** | `Head` | `Neck` | `5` | Cranium / gaze orientation |
| **7** | `RightShoulder` | `Spine3` | `4` | Right clavicle |
| **8** | `RightArm` | `RightShoulder`| `7` | Right upper arm / humerus |
| **9** | `RightForeArm` | `RightArm` | `8` | Right elbow / radius & ulna |
| **10**| `RightHand` | `RightForeArm` | `9` | Right wrist |
| **11**| `RightHandEnd` | `RightHand` | `10` | Right palm tip *(unmapped terminal)* |
| **12**| `RightHandThumb1` | `RightHand` | `10` | Right thumb base |
| **13**| `LeftShoulder` | `Spine3` | `4` | Left clavicle |
| **14**| `LeftArm` | `LeftShoulder` | `13` | Left upper arm / humerus |
| **15**| `LeftForeArm` | `LeftArm` | `14` | Left elbow / radius & ulna |
| **16**| `LeftHand` | `LeftForeArm` | `15` | Left wrist |
| **17**| `LeftHandEnd` | `LeftHand` | `16` | Left palm tip *(unmapped terminal)* |
| **18**| `LeftHandThumb1` | `LeftHand` | `16` | Left thumb base |
| **19**| `RightUpLeg` | `Hips` | `0` | Right hip / femur |
| **20**| `RightLeg` | `RightUpLeg` | `19` | Right knee / tibia |
| **21**| `RightFoot` | `RightLeg` | `20` | Right ankle / tarsal |
| **22**| `RightToeBase` | `RightFoot` | `21` | Right metatarsal / toes |
| **23**| `LeftUpLeg` | `Hips` | `0` | Left hip / femur |
| **24**| `LeftLeg` | `LeftUpLeg` | `23` | Left knee / tibia |
| **25**| `LeftFoot` | `LeftLeg` | `24` | Left ankle / tarsal |
| **26**| `LeftToeBase` | `LeftFoot` | `25` | Left metatarsal / toes |

---

## 2. VRM 1.0 Humanoid Mapping Table

The VRM specification (`VRM 1.0`) defines normalized humanoid bone nodes. 22 joints are explicitly mapped from CoreSkeleton27:

| Core Joint Index | Core Bone Name | Target VRM Humanoid Bone | Transformation Applied |
| :--- | :--- | :--- | :--- |
| **0** | `Hips` | `hips` | Matrix -> Quaternion + Translation Vector |
| **1** | `Spine` | `spine` | Matrix -> Normalized Quaternion |
| **3** | `Spine2` | `chest` | Matrix -> Normalized Quaternion |
| **4** | `Spine3` | `upperChest` | Matrix -> Normalized Quaternion |
| **5** | `Neck` | `neck` | Matrix -> Normalized Quaternion |
| **6** | `Head` | `head` | Matrix -> Normalized Quaternion |
| **7** | `RightShoulder` | `rightShoulder` | Matrix -> Normalized Quaternion |
| **8** | `RightArm` | `rightUpperArm` | Matrix -> Normalized Quaternion |
| **9** | `RightForeArm` | `rightLowerArm` | Matrix -> Normalized Quaternion |
| **10** | `RightHand` | `rightHand` | Matrix -> Normalized Quaternion |
| **13** | `LeftShoulder` | `leftShoulder` | Matrix -> Normalized Quaternion |
| **14** | `LeftArm` | `leftUpperArm` | Matrix -> Normalized Quaternion |
| **15** | `LeftForeArm` | `leftLowerArm` | Matrix -> Normalized Quaternion |
| **16** | `LeftHand` | `leftHand` | Matrix -> Normalized Quaternion |
| **19** | `RightUpLeg` | `rightUpperLeg` | Matrix -> Normalized Quaternion |
| **20** | `RightLeg` | `rightLowerLeg` | Matrix -> Normalized Quaternion |
| **21** | `RightFoot` | `rightFoot` | Matrix -> Normalized Quaternion |
| **22** | `RightToeBase` | `rightToes` | Matrix -> Normalized Quaternion |
| **23** | `LeftUpLeg` | `leftUpperLeg` | Matrix -> Normalized Quaternion |
| **24** | `LeftLeg` | `leftLowerLeg` | Matrix -> Normalized Quaternion |
| **25** | `LeftFoot` | `leftFoot` | Matrix -> Normalized Quaternion |
| **26** | `LeftToeBase` | `leftToes` | Matrix -> Normalized Quaternion |

### Unmapped Joints
- `Spine1` (Index 2): Absorbed between `spine` and `chest`.
- `RightHandEnd` (Index 11) & `LeftHandEnd` (Index 17): Terminal indicators with no skinning influence.
- `RightHandThumb1` (Index 12) & `LeftHandThumb1` (Index 18): Retained for skeleton rendering; finger articulation optional in VRM.

---

## 3. Quaternion Continuity & Normalization Pass

To prevent visual flipping artifacts (slerp jumping 360 degrees when $q$ flips to $-q$):
1. **Matrix to Quaternion Conversion:** Numerical conversion using trace formulation with $1e-8$ epsilon stabilization.
2. **Euclidean Normalization:** Every quaternion $q = [x, y, z, w]$ is normalized: $q \leftarrow q / \|q\|$.
3. **Hemisphere Continuity Check:** For each successive frame $t > 0$, compute inner dot product $d = q_t \cdot q_{t-1}$. If $d < 0$, invert sign: $q_t \leftarrow -q_t$.
