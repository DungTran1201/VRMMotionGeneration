# 05 - G1-to-Humanoid Retargeting Design

## 1. The Retargeting Challenge

MotionBricks was trained exclusively on the **Unitree G1** humanoid robot skeleton (`G1Skeleton34`). The G1 robot kinematics differ significantly from standard human skeletons:
- **Serial 1-DOF Hinge Joints:** Rather than 3-DOF spherical ball joints at the hips, spine, and shoulders, the G1 represents rotation as a chain of 1-DOF revolute joints along orthogonal axes (pitch $\rightarrow$ roll $\rightarrow$ yaw).
- **No Active Head/Neck:** G1 features a rigid camera sensor mount atop the upper torso rather than an articulated cervical spine.
- **Coordinate System Orientation:** Native MotionBricks models face $+Z$ with $+Y$ Up, whereas glTF/VRM models face $-Z$ with $+Y$ Up.

---

## 2. Mathematical Kinematic Composition

For any serial chain of 1-DOF joints connecting ancestor link $A$ to descendant link $C$ through intermediate joints $j_1, j_2, \dots, j_n$, the relative orientation of $C$ with respect to $A$ in world frame is:
$$R_{rel} = (R^{world}_A)^T \cdot R^{world}_C$$

This identity eliminates intermediate hinge offsets and computes the single composite 3-DOF orientation matrix of the humanoid limb directly from world rotations.

### Coordinate Conversion into Canonical glTF Space
The resulting rotation matrix is transformed into the Canonical coordinate frame via conjugation with $R_Y(180^\circ)$:
$$R^{canonical}_{rel} = R_Y(180^\circ) \cdot R_{rel} \cdot R_Y(180^\circ)^T$$

The final unit quaternion $[x, y, z, w]$ is extracted using Shepperd's stable algorithm.

---

## 3. Joint Mapping Table

| Humanoid Target Bone | Source G1 Kinematic Chain | Ancestor Index ($A$) | Child Index ($C$) | Mapping Type | Confidence |
|---|---|---|---|---|---|
| **`hips`** | `pelvis_skel` | - | 0 | Root Pass-Through | Exact |
| **`spine`** | `waist_yaw` $\rightarrow$ `waist_roll` $\rightarrow$ `waist_pitch` | 0 (`pelvis`) | 17 (`waist_pitch`) | Composed Chain | Exact |
| **`chest`** | None (Inherits spine orientation) | - | - | Static / Identity | Approximate |
| **`neck` / `head`** | None (Rigid torso mount) | - | - | Static / Identity | Approximate |
| **`leftUpperLeg`** | `left_hip_pitch` $\rightarrow$ `left_hip_roll` $\rightarrow$ `left_hip_yaw` | 0 (`pelvis`) | 3 (`left_hip_yaw`) | Composed Chain | Exact |
| **`leftLowerLeg`** | `left_knee_skel` | 3 (`left_hip_yaw`) | 4 (`left_knee`) | Direct Hinge | Exact |
| **`leftFoot`** | `left_ankle_pitch` $\rightarrow$ `left_ankle_roll` | 4 (`left_knee`) | 6 (`left_ankle_roll`) | Composed Chain | Exact |
| **`leftToes`** | `left_toe_base` | 6 (`left_ankle_roll`) | 7 (`left_toe_base`) | Direct | Exact |
| **`rightUpperLeg`** | `right_hip_pitch` $\rightarrow$ `right_hip_roll` $\rightarrow$ `right_hip_yaw` | 0 (`pelvis`) | 10 (`right_hip_yaw`) | Composed Chain | Exact |
| **`rightLowerLeg`** | `right_knee_skel` | 10 (`right_hip_yaw`) | 11 (`right_knee`) | Direct Hinge | Exact |
| **`rightFoot`** | `right_ankle_pitch` $\rightarrow$ `right_ankle_roll` | 11 (`right_knee`) | 13 (`right_ankle_roll`) | Composed Chain | Exact |
| **`rightToes`** | `right_toe_base` | 13 (`right_ankle_roll`) | 14 (`right_toe_base`) | Direct | Exact |
| **`leftShoulder`** | `left_shoulder_pitch_skel` | 17 (`waist_pitch`) | 18 (`left_shoulder_pitch`) | Direct Elevation | Approximate |
| **`leftUpperArm`** | `left_shoulder_roll` $\rightarrow$ `left_shoulder_yaw` | 18 (`left_shoulder_pitch`) | 20 (`left_shoulder_yaw`) | Composed Chain | Exact |
| **`leftLowerArm`** | `left_elbow_skel` | 20 (`left_shoulder_yaw`) | 21 (`left_elbow`) | Direct Hinge | Exact |
| **`leftHand`** | `left_wrist_roll` $\rightarrow$ `pitch` $\rightarrow$ `yaw` $\rightarrow$ `hand_roll` | 21 (`left_elbow`) | 25 (`left_hand_roll`) | Composed Chain | Exact |
| **`rightShoulder`** | `right_shoulder_pitch_skel` | 17 (`waist_pitch`) | 26 (`right_shoulder_pitch`) | Direct Elevation | Approximate |
| **`rightUpperArm`** | `right_shoulder_roll` $\rightarrow$ `right_shoulder_yaw` | 26 (`right_shoulder_pitch`) | 28 (`right_shoulder_yaw`) | Composed Chain | Exact |
| **`rightLowerArm`** | `right_elbow_skel` | 28 (`right_shoulder_yaw`) | 29 (`right_elbow`) | Direct Hinge | Exact |
| **`rightHand`** | `right_wrist_roll` $\rightarrow$ `pitch` $\rightarrow$ `yaw` $\rightarrow$ `hand_roll` | 29 (`right_elbow`) | 33 (`right_hand_roll`) | Composed Chain | Exact |

---

## 4. Retargeting Limitations & Visual Consequences

1. **Robot Morphology Artifacts:**
   Because MotionBricks was trained on the G1 robot's mechanical limits, arm swings and hip sways exhibit robot-like planar articulation rather than organic human shoulder scapulohumeral rhythm.
2. **Missing Neck/Head Animation:**
   The head maintains a fixed orientation relative to the chest. Future extensions can incorporate synthetic look-at constraints or camera trajectory trackers.
3. **Rest Pose Offsets:**
   The G1 robot neutral rest pose has arms slightly pitched forward with knees extended. When retargeted to A-pose or T-pose VRM models, our retargeter uses relative matrix transforms from rest to eliminate unwanted initial offsets.
