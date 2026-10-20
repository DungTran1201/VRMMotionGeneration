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
    T, J = quats.shape[:2]
    continuous = quats.copy()
    for t in range(1, T):
        dots = np.sum(continuous[t] * continuous[t - 1], axis=-1)
        flips = dots < 0
        continuous[t, flips] = -continuous[t, flips]
    return continuous


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
) -> UnifiedMotionPayload:
    """Build unified motion payload for synchronized dual-viewport visualization."""
    if local_rot_mats.ndim == 5:
        local_rot_mats = local_rot_mats[0]
    if root_positions.ndim == 3:
        root_positions = root_positions[0]

    T, J = local_rot_mats.shape[:2]
    if J != 27:
        raise ValueError(f"Expected 27 joints for CoreSkeleton, got {J}")

    # Validate finite values
    if not np.all(np.isfinite(local_rot_mats)):
        raise ValueError("Non-finite values found in local_rot_mats")
    if not np.all(np.isfinite(root_positions)):
        raise ValueError("Non-finite values found in root_positions")

    # 1. Compute 3D joint positions for Skeleton Viewport
    if posed_joints is not None:
        if posed_joints.ndim == 4:
            posed_joints = posed_joints[0]
        joint_positions_arr = posed_joints
    else:
        joint_positions_arr, _ = forward_kinematics(local_rot_mats, root_positions)

    # 2. Convert rotation matrices to unit quaternions with continuity check
    quats = matrix_to_quaternion_xyzw(local_rot_mats)
    quats = ensure_quaternion_continuity(quats)

    # 3. Assemble VRM Bone tracks
    vrm_bones: Dict[str, List[List[float]]] = {}
    for joint_idx, (_, vrm_name) in CORE_TO_VRM_BONE_MAP.items():
        vrm_bones[vrm_name] = quats[:, joint_idx].tolist()

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
