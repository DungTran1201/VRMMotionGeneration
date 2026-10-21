"""
Configuration constants for DiP-Viser experiment.
"""
from pathlib import Path
from typing import List, Tuple

# Base paths
EXPERIMENT_DIR = Path(__file__).resolve().parent.parent
UPSTREAM_DIR = EXPERIMENT_DIR / "upstream" / "motion-diffusion-model"
CHECKPOINT_DIR = EXPERIMENT_DIR / "checkpoints" / "DiP_no-target_10steps_context20_predict40"
CHECKPOINT_MODEL_PATH = CHECKPOINT_DIR / "model000600343.pt"
CHECKPOINT_ARGS_PATH = CHECKPOINT_DIR / "args.json"

ARTIFACTS_DIR = EXPERIMENT_DIR / "artifacts"
SAMPLES_DIR = ARTIFACTS_DIR / "samples"
BENCHMARKS_DIR = ARTIFACTS_DIR / "benchmarks"
ASSETS_DIR = EXPERIMENT_DIR / "assets"
FIXTURES_DIR = ASSETS_DIR / "fixtures"
PROMPTS_FILE = ASSETS_DIR / "prompts.json"

# Motion parameters
MOTION_FPS = 20.0
DEFAULT_DURATION_SECONDS = 4.0
DEFAULT_GUIDANCE_PARAM = 7.5
NUM_JOINTS = 22

# HumanML3D / SMPL-22 Joint Names
SMPL_22_JOINT_NAMES: List[str] = [
    "Pelvis",        # 0
    "L_Hip",         # 1
    "R_Hip",         # 2
    "Spine1",        # 3
    "L_Knee",        # 4
    "R_Knee",        # 5
    "Spine2",        # 6
    "L_Ankle",       # 7
    "R_Ankle",       # 8
    "Spine3",        # 9 (Thorax / Chest)
    "L_Foot",        # 10
    "R_Foot",        # 11
    "Neck",          # 12
    "L_Collar",      # 13
    "R_Collar",      # 14
    "Head",          # 15
    "L_Shoulder",    # 16
    "R_Shoulder",    # 17
    "L_Elbow",       # 18
    "R_Elbow",       # 19
    "L_Wrist",       # 20
    "R_Wrist",       # 21
]

# Official Kinematic chains from paramUtil.t2m_kinematic_chain
KINEMATIC_CHAINS: List[List[int]] = [
    [0, 2, 5, 8, 11],       # Right leg
    [0, 1, 4, 7, 10],       # Left leg
    [0, 3, 6, 9, 12, 15],   # Spine, neck, head
    [9, 14, 17, 19, 21],    # Right shoulder & arm
    [9, 13, 16, 18, 20],    # Left shoulder & arm
]

# Derived bone connections (pairs of joint indices)
SKELETON_BONES: List[Tuple[int, int]] = [
    # Right Leg
    (0, 2), (2, 5), (5, 8), (8, 11),
    # Left Leg
    (0, 1), (1, 4), (4, 7), (7, 10),
    # Spine & Head
    (0, 3), (3, 6), (6, 9), (9, 12), (12, 15),
    # Right Arm
    (9, 14), (14, 17), (17, 19), (19, 21),
    # Left Arm
    (9, 13), (13, 16), (16, 18), (18, 20),
]

# Parent map: parent of root (0) is -1
JOINT_PARENTS: List[int] = [
    -1,  # 0: Pelvis
     0,  # 1: L_Hip
     0,  # 2: R_Hip
     0,  # 3: Spine1
     1,  # 4: L_Knee
     2,  # 5: R_Knee
     3,  # 6: Spine2
     4,  # 7: L_Ankle
     5,  # 8: R_Ankle
     6,  # 9: Spine3
     7,  # 10: L_Foot
     8,  # 11: R_Foot
     9,  # 12: Neck
     9,  # 13: L_Collar
     9,  # 14: R_Collar
    12,  # 15: Head
    13,  # 16: L_Shoulder
    14,  # 17: R_Shoulder
    16,  # 18: L_Elbow
    17,  # 19: R_Elbow
    18,  # 20: L_Wrist
    19,  # 21: R_Wrist
]

# Viser Server Defaults
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080
