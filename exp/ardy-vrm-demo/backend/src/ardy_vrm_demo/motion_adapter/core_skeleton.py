"""CoreSkeleton27 definitions, forward kinematics, and coordinate mappings."""

from typing import List, Optional, Tuple
import numpy as np

# 27 humanoid bones of NVIDIA ARDY CoreSkeleton
CORE_SKELETON_27_BONES = [
    ("Hips", None),
    ("Spine", "Hips"),
    ("Spine1", "Spine"),
    ("Spine2", "Spine1"),
    ("Spine3", "Spine2"),
    ("Neck", "Spine3"),
    ("Head", "Neck"),
    ("RightShoulder", "Spine3"),
    ("RightArm", "RightShoulder"),
    ("RightForeArm", "RightArm"),
    ("RightHand", "RightForeArm"),
    ("RightHandEnd", "RightHand"),
    ("RightHandThumb1", "RightHand"),
    ("LeftShoulder", "Spine3"),
    ("LeftArm", "LeftShoulder"),
    ("LeftForeArm", "LeftArm"),
    ("LeftHand", "LeftForeArm"),
    ("LeftHandEnd", "LeftHand"),
    ("LeftHandThumb1", "LeftHand"),
    ("RightUpLeg", "Hips"),
    ("RightLeg", "RightUpLeg"),
    ("RightFoot", "RightLeg"),
    ("RightToeBase", "RightFoot"),
    ("LeftUpLeg", "Hips"),
    ("LeftLeg", "LeftUpLeg"),
    ("LeftFoot", "LeftLeg"),
    ("LeftToeBase", "LeftFoot"),
]

CORE_BONE_NAMES: List[str] = [b[0] for b in CORE_SKELETON_27_BONES]
CORE_PARENT_INDICES: List[int] = [
    CORE_BONE_NAMES.index(p) if p is not None else -1 for _, p in CORE_SKELETON_27_BONES
]

# Bone line connectivity pairs (parent_idx, child_idx) for 3D skeleton rendering
BONE_CONNECTIVITY_PAIRS: List[Tuple[int, int]] = [
    (p, i) for i, p in enumerate(CORE_PARENT_INDICES) if p >= 0
]

# Canonical T-pose joint positions relative to root in meters
REST_JOINTS_CORE = np.array([
    [0.000000000, 0.000000000, 0.000000000],
    [0.000000000, 0.070989100, -0.047326100],
    [0.000000000, 0.164203318, -0.063762289],
    [0.000000000, 0.258495331, -0.072011823],
    [0.000000000, 0.353147527, -0.072011917],
    [0.000000000, 0.601609551, -0.036517567],
    [0.000000000, 0.729779339, -0.013917897],
    [-0.031994900, 0.525919572, -0.018687292],
    [-0.190902900, 0.525919517, -0.018687292],
    [-0.486338900, 0.525919415, -0.018687292],
    [-0.718990900, 0.525919334, -0.018687292],
    [-0.788602400, 0.525919310, -0.018687292],
    [-0.746835494, 0.507356272, 0.027720424],
    [0.031994900, 0.525919572, -0.018687292],
    [0.190902900, 0.525919572, -0.018687292],
    [0.486338900, 0.525919572, -0.018687292],
    [0.718990900, 0.525919572, -0.018687292],
    [0.788602400, 0.525919572, -0.018687292],
    [0.746835500, 0.507356519, 0.027720424],
    [-0.094918200, -0.027728900, 0.000000000],
    [-0.094918200, -0.439846900, 0.000000000],
    [-0.094918200, -0.895937900, 0.000000000],
    [-0.094918200, -0.954412825, 0.160658266],
    [0.094918200, -0.027728900, 0.000000000],
    [0.094918200, -0.439846900, 0.000000000],
    [0.094918200, -0.895937900, 0.000000000],
    [0.094918200, -0.954412825, 0.160658266]
], dtype=np.float64)


def compute_offsets() -> np.ndarray:
    """Compute local bone offsets from parent bones in rest pose."""
    offsets = REST_JOINTS_CORE.copy()
    for i, p in enumerate(CORE_PARENT_INDICES):
        if p >= 0:
            offsets[i] = REST_JOINTS_CORE[i] - REST_JOINTS_CORE[p]
        else:
            offsets[i] = np.zeros(3)
    return offsets


def forward_kinematics(local_rot_mats: np.ndarray, root_positions: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Reconstruct world joint positions from local rotation matrices and root translations."""
    T, J = local_rot_mats.shape[:2]
    offsets = compute_offsets()
    global_rots = np.zeros((T, J, 3, 3), dtype=np.float64)
    global_pos = np.zeros((T, J, 3), dtype=np.float64)

    for i in range(J):
        parent = CORE_PARENT_INDICES[i]
        if parent < 0:
            global_rots[:, i] = local_rot_mats[:, i]
            global_pos[:, i] = root_positions
        else:
            p_rot = global_rots[:, parent]
            global_rots[:, i] = np.matmul(p_rot, local_rot_mats[:, i])
            off = offsets[i]
            rotated_off = np.einsum("tij,j->ti", p_rot, off)
            global_pos[:, i] = global_pos[:, parent] + rotated_off

    return global_pos, global_rots
