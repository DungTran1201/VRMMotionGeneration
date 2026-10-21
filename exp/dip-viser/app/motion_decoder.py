"""
Motion Decoder for DiP-Viser Experiment.
Parses official DiP results.npy and constructs validated MotionClip instances.
Provides procedural fixture generator explicitly tagged with provenance='fixture'.
"""
from pathlib import Path
from typing import Any, Dict, Optional, Union
import math
import numpy as np

from .config import (
    CHECKPOINT_MODEL_PATH,
    MOTION_FPS,
    NUM_JOINTS,
    SMPL_22_JOINT_NAMES,
    JOINT_PARENTS,
    SKELETON_BONES,
)
from .motion_schema import MotionClip, MotionValidationError


def decode_results_npy(
    source: Union[str, Path, Dict[str, Any], np.ndarray],
    prompt: Optional[str] = None,
    checkpoint_path: Optional[str] = None,
    provenance: str = "real_inference",
) -> MotionClip:
    """
    Decodes DiP generation output into a standardized, validated MotionClip.
    
    Official DiP results.npy layout:
    - np.load(path, allow_pickle=True)[None][0]
    - keys: 'motion', 'text', 'lengths', 'num_samples', 'num_repetitions'
    - 'motion': shape (num_samples, 22, 3, seq_len) float32
    - 'text': list of prompts
    - 'lengths': list of valid frame counts
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Results file not found: {path}")
        raw_data = np.load(path, allow_pickle=True)
        if hasattr(raw_data, "item"):
            try:
                dict_data = raw_data.item()
            except Exception:
                dict_data = raw_data[None][0]
        elif isinstance(raw_data, np.ndarray) and raw_data.ndim > 0:
            dict_data = raw_data[None][0]
        else:
            dict_data = raw_data
    elif isinstance(source, dict):
        dict_data = source
    elif isinstance(source, np.ndarray):
        # Direct motion array
        dict_data = {"motion": source}
    else:
        raise TypeError(f"Unsupported source type: {type(source)}")

    if not isinstance(dict_data, dict):
        raise MotionValidationError(f"Expected dict data inside results.npy, got {type(dict_data)}")

    if "motion" not in dict_data:
        raise MotionValidationError(f"Missing 'motion' key in generation results. Keys found: {list(dict_data.keys())}")

    raw_motion = dict_data["motion"]
    if not isinstance(raw_motion, np.ndarray):
        raw_motion = np.array(raw_motion, dtype=np.float32)

    # Official DiP output shape is typically (num_samples, 22, 3, seq_len)
    if raw_motion.ndim == 4:
        # Take sample 0: shape is (22, 3, seq_len)
        sample = raw_motion[0]
        # Transpose to (seq_len, 22, 3)
        joint_positions = np.transpose(sample, (2, 0, 1)).astype(np.float32)
    elif raw_motion.ndim == 3:
        if raw_motion.shape[0] == NUM_JOINTS and raw_motion.shape[1] == 3:
            # (22, 3, seq_len) -> (seq_len, 22, 3)
            joint_positions = np.transpose(raw_motion, (2, 0, 1)).astype(np.float32)
        elif raw_motion.shape[1] == NUM_JOINTS and raw_motion.shape[2] == 3:
            # Already (seq_len, 22, 3)
            joint_positions = raw_motion.astype(np.float32)
        else:
            raise MotionValidationError(f"Unexpected 3D motion shape: {raw_motion.shape}")
    else:
        raise MotionValidationError(f"Unexpected motion array dimensions: {raw_motion.ndim} (shape: {raw_motion.shape})")

    # Handle sequence length truncation if lengths provided
    if "lengths" in dict_data and len(dict_data["lengths"]) > 0:
        valid_len = int(dict_data["lengths"][0])
        if 0 < valid_len <= joint_positions.shape[0]:
            joint_positions = joint_positions[:valid_len]

    # Resolve text prompt
    resolved_prompt = prompt
    if not resolved_prompt and "text" in dict_data and len(dict_data["text"]) > 0:
        resolved_prompt = str(dict_data["text"][0])
    if not resolved_prompt:
        resolved_prompt = "Unknown prompt"

    resolved_ckpt = checkpoint_path or str(CHECKPOINT_MODEL_PATH.name)

    clip = MotionClip(
        schema_version="1.0.0",
        source_model="DiP",
        source_checkpoint=resolved_ckpt,
        prompt=resolved_prompt,
        provenance=provenance,
        fps=MOTION_FPS,
        num_frames=int(joint_positions.shape[0]),
        duration_seconds=float(joint_positions.shape[0]) / MOTION_FPS,
        joint_positions=joint_positions,
        joint_names=list(SMPL_22_JOINT_NAMES),
        joint_parents=list(JOINT_PARENTS),
        bones=list(SKELETON_BONES),
        metadata={
            "num_samples": dict_data.get("num_samples", 1),
            "num_repetitions": dict_data.get("num_repetitions", 1),
            "coord_system": "Right-Handed Metric (Y-Up, Z-Forward)",
        },
    )
    clip.validate()
    return clip


def create_fixture_motion(
    prompt: str = "FIXTURE: Procedural walking human",
    num_frames: int = 80,
    fps: float = MOTION_FPS,
) -> MotionClip:
    """
    Creates a deterministic procedural 22-joint HumanML3D walking skeleton motion.
    EXPLICITLY TAGGED WITH provenance='fixture'.
    Used for UI testing, offline viewer validation, and fallback verification.
    """
    positions = np.zeros((num_frames, NUM_JOINTS, 3), dtype=np.float32)
    dt = 1.0 / fps

    # Reference neutral SMPL-22 T-pose heights in meters
    base_pose = np.zeros((NUM_JOINTS, 3), dtype=np.float32)
    base_pose[0]  = [0.0, 0.92, 0.0]    # Pelvis
    base_pose[1]  = [0.10, 0.85, 0.0]   # L_Hip
    base_pose[2]  = [-0.10, 0.85, 0.0]  # R_Hip
    base_pose[3]  = [0.0, 1.05, 0.0]    # Spine1
    base_pose[4]  = [0.10, 0.45, 0.0]   # L_Knee
    base_pose[5]  = [-0.10, 0.45, 0.0]  # R_Knee
    base_pose[6]  = [0.0, 1.20, 0.0]    # Spine2
    base_pose[7]  = [0.10, 0.08, 0.0]   # L_Ankle
    base_pose[8]  = [-0.10, 0.08, 0.0]  # R_Ankle
    base_pose[9]  = [0.0, 1.35, 0.0]    # Spine3
    base_pose[10] = [0.10, 0.02, 0.12]  # L_Foot
    base_pose[11] = [-0.10, 0.02, 0.12] # R_Foot
    base_pose[12] = [0.0, 1.48, 0.0]    # Neck
    base_pose[13] = [0.08, 1.40, 0.0]   # L_Collar
    base_pose[14] = [-0.08, 1.40, 0.0]  # R_Collar
    base_pose[15] = [0.0, 1.62, 0.0]    # Head
    base_pose[16] = [0.18, 1.40, 0.0]   # L_Shoulder
    base_pose[17] = [-0.18, 1.40, 0.0]  # R_Shoulder
    base_pose[18] = [0.22, 1.15, 0.0]   # L_Elbow
    base_pose[19] = [-0.22, 1.15, 0.0]  # R_Elbow
    base_pose[20] = [0.24, 0.90, 0.0]   # L_Wrist
    base_pose[21] = [-0.24, 0.90, 0.0]  # R_Wrist

    walk_speed = 1.0  # meters per second forward
    cadence = 2.0 * math.pi * 1.2  # stride frequency

    for f in range(num_frames):
        t = f * dt
        z_root = walk_speed * t
        phase = cadence * t

        # Copy base pose
        frame_joints = base_pose.copy()

        # Pelvis bounce & forward motion
        frame_joints[0, 1] += 0.02 * math.cos(2.0 * phase)
        frame_joints[:, 2] += z_root

        # Leg swing (L and R in antiphase)
        swing_l = 0.15 * math.sin(phase)
        swing_r = 0.15 * math.sin(phase + math.pi)

        frame_joints[4, 2] += swing_l * 0.8
        frame_joints[7, 2] += swing_l
        frame_joints[10, 2] += swing_l
        frame_joints[4, 1] += max(0.0, swing_l * 0.2)
        frame_joints[7, 1] += max(0.0, swing_l * 0.3)

        frame_joints[5, 2] += swing_r * 0.8
        frame_joints[8, 2] += swing_r
        frame_joints[11, 2] += swing_r
        frame_joints[5, 1] += max(0.0, swing_r * 0.2)
        frame_joints[8, 1] += max(0.0, swing_r * 0.3)

        # Arm swing (opposite to legs)
        frame_joints[18, 2] += -swing_l * 0.7
        frame_joints[20, 2] += -swing_l * 0.9
        frame_joints[19, 2] += -swing_r * 0.7
        frame_joints[21, 2] += -swing_r * 0.9

        positions[f] = frame_joints

    clip = MotionClip(
        schema_version="1.0.0",
        source_model="ProceduralFixture",
        source_checkpoint="fixture_synthetic_v1",
        prompt=prompt,
        provenance="fixture",
        fps=fps,
        num_frames=num_frames,
        duration_seconds=float(num_frames) / fps,
        joint_positions=positions,
        joint_names=list(SMPL_22_JOINT_NAMES),
        joint_parents=list(JOINT_PARENTS),
        bones=list(SKELETON_BONES),
        metadata={"note": "Procedural synthetic test fixture for UI/offline testing."},
    )
    clip.validate()
    return clip
