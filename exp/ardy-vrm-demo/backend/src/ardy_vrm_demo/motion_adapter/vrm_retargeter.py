"""Retargets ARDY CoreSkeleton27 outputs to standard VRM Humanoid animation tracks."""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy.spatial.transform import Rotation

from .core_skeleton import (
    CORE_BONE_NAMES,
    CORE_PARENT_INDICES,
    forward_kinematics,
)
from ..schemas import GenerationTelemetry, SkeletonTrack, UnifiedMotionPayload, VRMRotationTrack

# Explicit 1-to-1 mapping from CoreSkeleton27 index to VRM Humanoid bone name
CORE_TO_VRM_BONE_MAP: Dict[int, Tuple[str, str]] = {
    0: ("Hips", "hips"),
    1: ("Spine", "spine"),
    2: ("Spine1", "chest"),
    4: ("Spine3", "upperChest"),
    5: ("Neck", "neck"),
    6: ("Head", "head"),
    7: ("RightShoulder", "rightShoulder"),
    8: ("RightArm", "rightUpperArm"),
    9: ("RightForeArm", "rightLowerArm"),
    10: ("RightHand", "rightHand"),
    13: ("LeftShoulder", "leftShoulder"),
    14: ("LeftArm", "leftUpperArm"),
    15: ("LeftForeArm", "leftLowerArm"),
    16: ("LeftHand", "leftHand"),
    19: ("RightUpLeg", "rightUpperLeg"),
    20: ("RightLeg", "rightLowerLeg"),
    21: ("RightFoot", "rightFoot"),
    22: ("RightToeBase", "rightToes"),
    23: ("LeftUpLeg", "leftUpperLeg"),
    24: ("LeftLeg", "leftLowerLeg"),
    25: ("LeftFoot", "leftFoot"),
    26: ("LeftToeBase", "leftToes"),
}

# Standard VRM Humanoid parent hierarchy
VRM_HUMANOID_PARENT_MAP: Dict[str, Optional[str]] = {
    "hips": None,
    "spine": "hips",
    "chest": "spine",
    "upperChest": "chest",
    "neck": "upperChest",
    "head": "neck",
    "rightShoulder": "upperChest",
    "rightUpperArm": "rightShoulder",
    "rightLowerArm": "rightUpperArm",
    "rightHand": "rightLowerArm",
    "leftShoulder": "upperChest",
    "leftUpperArm": "leftShoulder",
    "leftLowerArm": "leftUpperArm",
    "leftHand": "leftLowerArm",
    "rightUpperLeg": "hips",
    "rightLowerLeg": "rightUpperLeg",
    "rightFoot": "rightLowerLeg",
    "rightToes": "rightFoot",
    "leftUpperLeg": "hips",
    "leftLowerLeg": "leftUpperLeg",
    "leftFoot": "leftLowerLeg",
    "leftToes": "leftFoot",
}

VRM_TO_CORE_INDEX_MAP: Dict[str, int] = {
    "hips": 0,
    "spine": 1,
    "chest": 2,       # Spine1
    "upperChest": 4,  # Spine3
    "neck": 5,
    "head": 6,
    "rightShoulder": 7,
    "rightUpperArm": 8,
    "rightLowerArm": 9,
    "rightHand": 10,
    "leftShoulder": 13,
    "leftUpperArm": 14,
    "leftLowerArm": 15,
    "leftHand": 16,
    "rightUpperLeg": 19,
    "rightLowerLeg": 20,
    "rightFoot": 21,
    "rightToes": 22,
    "leftUpperLeg": 23,
    "leftLowerLeg": 24,
    "leftFoot": 25,
    "leftToes": 26,
}


def matrix_to_quaternion_xyzw(rot_mats: np.ndarray) -> np.ndarray:
    """Convert (..., 3, 3) rotation matrices to normalized (..., 4) quaternions [x, y, z, w]."""
    shape = rot_mats.shape[:-2]
    flat = rot_mats.reshape(-1, 3, 3)
    r = Rotation.from_matrix(flat)
    quats = r.as_quat()  # Scipy convention: [x, y, z, w]
    norms = np.linalg.norm(quats, axis=-1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    quats = quats / norms
    return quats.reshape(*shape, 4)


def ensure_quaternion_continuity(quats: np.ndarray) -> np.ndarray:
    """Ensure quaternion signs do not arbitrarily negate across consecutive frames (avoid slerp flips)."""
    T = quats.shape[0]
    continuous = quats.copy()
    for t in range(1, T):
        dots = np.sum(continuous[t] * continuous[t - 1], axis=-1)
        if dots < 0:
            continuous[t] = -continuous[t]
    return continuous


def compute_vrm_local_rotations(global_rot_mats: np.ndarray) -> Dict[str, np.ndarray]:
    """Compute exact local rotations for VRM Humanoid hierarchy from global rotations.

    Given desired global rotations for each mapped bone, computes the relative local rotation:
    R_local(B) = (R_global(parent(B)))^T @ R_global(B)
    For hips (root): R_local(hips) = R_global(hips)
    """
    T = global_rot_mats.shape[0]
    vrm_local_mats: Dict[str, np.ndarray] = {}

    for vrm_bone, core_idx in VRM_TO_CORE_INDEX_MAP.items():
        r_global_bone = global_rot_mats[:, core_idx]
        parent_bone = VRM_HUMANOID_PARENT_MAP.get(vrm_bone)

        if parent_bone is None:
            vrm_local_mats[vrm_bone] = r_global_bone
        else:
            parent_core_idx = VRM_TO_CORE_INDEX_MAP[parent_bone]
            r_global_parent = global_rot_mats[:, parent_core_idx]
            # (R_parent)^T @ R_bone
            r_local = np.matmul(np.swapaxes(r_global_parent, -1, -2), r_global_bone)
            vrm_local_mats[vrm_bone] = r_local

    return vrm_local_mats


def create_unified_motion_payload(
    local_rot_mats: np.ndarray,
    root_positions: np.ndarray,
    fps: float,
    prompt: str,
    seed: int,
    source_model: str,
    telemetry: GenerationTelemetry,
    mode: str = "LIVE ARDY",
    posed_joints: Optional[np.ndarray] = None,
    global_rot_mats: Optional[np.ndarray] = None,
) -> UnifiedMotionPayload:
    """Build unified motion payload for synchronized dual-viewport visualization."""
    if local_rot_mats.ndim == 5:
        local_rot_mats = local_rot_mats[0]
    if root_positions.ndim == 3:
        root_positions = root_positions[0]
    if global_rot_mats is not None and global_rot_mats.ndim == 5:
        global_rot_mats = global_rot_mats[0]

    T, J = local_rot_mats.shape[:2]
    if J != 27:
        raise ValueError(f"Expected 27 joints for CoreSkeleton, got {J}")

    # Validate finite values
    if not np.all(np.isfinite(local_rot_mats)):
        raise ValueError("Non-finite values found in local_rot_mats")
    if not np.all(np.isfinite(root_positions)):
        raise ValueError("Non-finite values found in root_positions")

    # 1. Compute 3D joint positions and global rotations
    fk_pos, fk_rots = forward_kinematics(local_rot_mats, root_positions)
    if posed_joints is not None:
        if posed_joints.ndim == 4:
            posed_joints = posed_joints[0]
        joint_positions_arr = posed_joints
    else:
        joint_positions_arr = fk_pos

    effective_global_rots = global_rot_mats if global_rot_mats is not None else fk_rots

    # 2. Retarget global rotations to VRM Humanoid hierarchy
    vrm_local_mats = compute_vrm_local_rotations(effective_global_rots)

    # 3. Assemble VRM Bone tracks with unit quaternions and continuity
    vrm_bones: Dict[str, List[List[float]]] = {}
    for vrm_name, rot_mats in vrm_local_mats.items():
        quats = matrix_to_quaternion_xyzw(rot_mats)
        quats = ensure_quaternion_continuity(quats)
        vrm_bones[vrm_name] = quats.tolist()

    # Hips translation (meters)
    hips_translations = root_positions.tolist()

    timestamps = [round(float(t / fps), 4) for t in range(T)]

    # Skeleton positions list [frame][joint] = [x, y, z]
    skeleton_positions = joint_positions_arr.tolist()

    return UnifiedMotionPayload(
        schema_version="1.0.0",
        source_model=source_model,
        prompt=prompt,
        seed=seed,
        fps=float(fps),
        total_frames=int(T),
        duration_seconds=round(float(T / fps), 3),
        timestamps=timestamps,
        mode=mode,
        telemetry=telemetry,
        skeleton=SkeletonTrack(
            bone_names=CORE_BONE_NAMES,
            parent_indices=CORE_PARENT_INDICES,
            joint_positions=skeleton_positions,
        ),
        vrm=VRMRotationTrack(
            bones=vrm_bones,
            root_translation=hips_translations,
        ),
    )
