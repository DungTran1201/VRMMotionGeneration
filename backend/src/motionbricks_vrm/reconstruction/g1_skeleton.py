"""G1Skeleton34 source kinematic model and skeleton reconstruction.

Implements the official Unitree G1 34-joint hierarchy used in MotionBricks,
reconstructing parent-relative local rotations and world joint positions
from decoded motion feature tensors.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, List, Optional, Tuple
import numpy as np

from motionbricks_vrm.reconstruction.math_utils import (
    cont6d_to_matrix,
    matrix_to_quaternion_xyzw,
    normalize_quaternion,
)


# The canonical 34 joints in exact order from MotionBricks G1Skeleton34
G1_JOINT_NAMES: List[str] = [
    "pelvis_skel",               # 0
    "left_hip_pitch_skel",       # 1
    "left_hip_roll_skel",        # 2
    "left_hip_yaw_skel",         # 3
    "left_knee_skel",            # 4
    "left_ankle_pitch_skel",     # 5
    "left_ankle_roll_skel",      # 6
    "left_toe_base",             # 7 (dummy)
    "right_hip_pitch_skel",      # 8
    "right_hip_roll_skel",       # 9
    "right_hip_yaw_skel",        # 10
    "right_knee_skel",           # 11
    "right_ankle_pitch_skel",    # 12
    "right_ankle_roll_skel",     # 13
    "right_toe_base",            # 14 (dummy)
    "waist_yaw_skel",            # 15
    "waist_roll_skel",           # 16
    "waist_pitch_skel",          # 17
    "left_shoulder_pitch_skel",  # 18
    "left_shoulder_roll_skel",   # 19
    "left_shoulder_yaw_skel",    # 20
    "left_elbow_skel",           # 21
    "left_wrist_roll_skel",      # 22
    "left_wrist_pitch_skel",     # 23
    "left_wrist_yaw_skel",       # 24
    "left_hand_roll_skel",       # 25
    "right_shoulder_pitch_skel", # 26
    "right_shoulder_roll_skel",  # 27
    "right_shoulder_yaw_skel",   # 28
    "right_elbow_skel",          # 29
    "right_wrist_roll_skel",     # 30
    "right_wrist_pitch_skel",    # 31
    "right_wrist_yaw_skel",      # 32
    "right_hand_roll_skel",      # 33
]

# Parent indices corresponding to each of the 34 joints (-1 for root pelvis)
G1_PARENT_INDICES: List[int] = [
    -1,                          # 0: pelvis_skel
     0,  1,  2,  3,  4,  5,  6,  # 1-7: left leg chain
     0,  8,  9, 10, 11, 12, 13,  # 8-14: right leg chain
     0, 15, 16,                  # 15-17: waist chain
    17, 18, 19, 20, 21, 22, 23, 24, # 18-25: left arm chain
    17, 26, 27, 28, 29, 30, 31, 32  # 26-33: right arm chain
]

# Ground-truth rest pose offsets (meters) extracted from upstream joints.p
G1_REST_OFFSETS: np.ndarray = np.array([
    [ 0.0000e+00,  0.0000e+00,  0.0000e+00], # 0: pelvis
    [ 6.4452e-02, -1.0270e-01,  0.0000e+00], # 1: left_hip_pitch
    [ 1.1645e-01, -1.3316e-01,  0.0000e+00], # 2: left_hip_roll
    [ 1.1645e-01, -2.5728e-01,  2.5001e-02], # 3: left_hip_yaw
    [ 1.1860e-01, -4.3462e-01, -5.3272e-02], # 4: left_knee
    [ 1.1851e-01, -7.3463e-01, -5.3272e-02], # 5: left_ankle_pitch
    [ 1.1851e-01, -7.5219e-01, -5.3272e-02], # 6: left_ankle_roll
    [ 1.1851e-01, -7.8719e-01,  8.6728e-02], # 7: left_toe_base
    [-6.4452e-02, -1.0270e-01,  0.0000e+00], # 8: right_hip_pitch
    [-1.1645e-01, -1.3316e-01,  0.0000e+00], # 9: right_hip_roll
    [-1.1645e-01, -2.5728e-01,  2.5001e-02], # 10: right_hip_yaw
    [-1.1860e-01, -4.3462e-01, -5.3272e-02], # 11: right_knee
    [-1.1851e-01, -7.3463e-01, -5.3272e-02], # 12: right_ankle_pitch
    [-1.1851e-01, -7.5219e-01, -5.3272e-02], # 13: right_ankle_roll
    [-1.1851e-01, -7.8719e-01,  8.6728e-02], # 14: right_toe_base
    [ 0.0000e+00,  0.0000e+00,  0.0000e+00], # 15: waist_yaw
    [ 0.0000e+00,  4.4000e-02, -3.9635e-03], # 16: waist_roll
    [ 0.0000e+00,  4.4000e-02, -3.9635e-03], # 17: waist_pitch
    [ 1.0022e-01,  2.9178e-01,  0.0000e+00], # 18: left_shoulder_pitch
    [ 1.3822e-01,  2.7795e-01,  0.0000e+00], # 19: left_shoulder_roll
    [ 1.4446e-01,  1.7475e-01,  0.0000e+00], # 20: left_shoulder_yaw
    [ 1.4446e-01,  9.4231e-02,  1.5776e-02], # 21: left_elbow
    [ 1.4635e-01,  8.4231e-02,  1.1578e-01], # 22: left_wrist_roll
    [ 1.4635e-01,  8.4231e-02,  1.5378e-01], # 23: left_wrist_pitch
    [ 1.4635e-01,  8.4231e-02,  1.9978e-01], # 24: left_wrist_yaw
    [ 1.4635e-01,  8.4231e-02,  2.9978e-01], # 25: left_hand_roll
    [-1.0021e-01,  2.9178e-01,  0.0000e+00], # 26: right_shoulder_pitch
    [-1.3821e-01,  2.7795e-01,  0.0000e+00], # 27: right_shoulder_roll
    [-1.4445e-01,  1.7475e-01,  0.0000e+00], # 28: right_shoulder_yaw
    [-1.4445e-01,  9.4231e-02,  1.5776e-02], # 29: right_elbow
    [-1.4634e-01,  8.4231e-02,  1.1578e-01], # 30: right_wrist_roll
    [-1.4634e-01,  8.4231e-02,  1.5378e-01], # 31: right_wrist_pitch
    [-1.4634e-01,  8.4231e-02,  1.9978e-01], # 32: right_wrist_yaw
    [-1.4634e-01,  8.4231e-02,  2.9978e-01]  # 33: right_hand_roll
], dtype=np.float64)


@dataclass
class ReconstructedG1Frame:
    """Decoded and reconstructed pose data for a single frame of G1 robot."""
    root_pos: np.ndarray             # (3,) [x, y, z] in MotionBricks world frame
    root_rot_quat: np.ndarray        # (4,) [x, y, z, w]
    global_rot_mats: np.ndarray      # (34, 3, 3) world rotation matrix per joint
    local_rot_mats: np.ndarray       # (34, 3, 3) parent-relative rotation matrix per joint
    local_rot_quats: np.ndarray      # (34, 4) parent-relative [x, y, z, w]
    joint_world_positions: np.ndarray # (34, 3) world coordinates
    foot_contacts: Dict[str, bool]   # left_ankle, left_toe, right_ankle, right_toe


class G1SkeletonReconstructor:
    """Reconstructs the G1 kinematic tree from decoded MotionBricks features."""

    def __init__(self):
        self.joint_names = G1_JOINT_NAMES
        self.parents = G1_PARENT_INDICES
        self.num_joints = len(self.joint_names)
        self.name_to_idx = {name: idx for idx, name in enumerate(self.joint_names)}

    def reconstruct_from_feature_vector(self, feat: np.ndarray) -> ReconstructedG1Frame:
        """Parse a 414-dimensional global motion feature vector into full skeleton transforms.
        
        Indices:
        - 0..2: global_root_pos (3)
        - 3..4: global_root_heading cos/sin (2)
        - 5..103: ric_data (99) = 33 joints * 3
        - 104..307: global_rot_data (204) = 34 joints * 6D cont rotation
        - 308..409: local_vel (102) = 34 joints * 3
        - 410..413: foot_contacts (4)
        """
        if len(feat) != 414:
            raise ValueError(f"Expected 414-dimensional feature vector, got {len(feat)}")

        # 1. Root position
        root_pos = feat[0:3].copy()

        # 2. Heading
        cos_h, sin_h = feat[3], feat[4]
        heading_angle = math.atan2(sin_h, cos_h)
        # Root heading quaternion in MotionBricks space (rotation around Y):
        # [0, sin(h/2), 0, cos(h/2)] in [x, y, z, w] format
        root_rot_quat = np.array([
            0.0,
            math.sin(heading_angle / 2.0),
            0.0,
            math.cos(heading_angle / 2.0)
        ], dtype=np.float64)

        # 3. 6D rotations -> 3x3 matrices
        c6d = feat[104:308].reshape(34, 6)
        global_rot_mats = cont6d_to_matrix(c6d)  # (34, 3, 3)

        # 4. Compute parent-relative local rotation matrices:
        # R_local[i] = R_global[parent[i]]^T * R_global[i]
        local_rot_mats = np.zeros((34, 3, 3), dtype=np.float64)
        local_rot_quats = np.zeros((34, 4), dtype=np.float64)

        for i in range(34):
            parent_idx = self.parents[i]
            if parent_idx == -1:
                local_rot_mats[i] = global_rot_mats[i]
            else:
                r_parent = global_rot_mats[parent_idx]
                r_child = global_rot_mats[i]
                local_rot_mats[i] = r_parent.T @ r_child

            local_rot_quats[i] = matrix_to_quaternion_xyzw(local_rot_mats[i])

        # 5. World joint positions from ric_data
        # ric_data gives positions of joints 1..33 with projected root (X_root, 0, Z_root) subtracted
        ric = feat[5:104].reshape(33, 3)
        joint_world_positions = np.zeros((34, 3), dtype=np.float64)
        joint_world_positions[0] = root_pos
        root_proj = np.array([root_pos[0], 0.0, root_pos[2]], dtype=np.float64)
        joint_world_positions[1:] = ric + root_proj

        # 6. Foot contacts
        contacts = {
            "left_ankle": bool(feat[410] > 0.5),
            "left_toe": bool(feat[411] > 0.5),
            "right_ankle": bool(feat[412] > 0.5),
            "right_toe": bool(feat[413] > 0.5),
        }

        return ReconstructedG1Frame(
            root_pos=root_pos,
            root_rot_quat=normalize_quaternion(root_rot_quat),
            global_rot_mats=global_rot_mats,
            local_rot_mats=local_rot_mats,
            local_rot_quats=local_rot_quats,
            joint_world_positions=joint_world_positions,
            foot_contacts=contacts,
        )
