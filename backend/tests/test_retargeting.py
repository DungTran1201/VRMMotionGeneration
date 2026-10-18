"""Unit tests for G1 skeleton reconstruction and humanoid retargeting."""

import numpy as np
import pytest

from motionbricks_vrm.reconstruction.g1_skeleton import (
    G1_JOINT_NAMES,
    G1SkeletonReconstructor,
    ReconstructedG1Frame,
)
from motionbricks_vrm.retargeting.retargeter import G1ToHumanoidRetargeter
from motionbricks_vrm.schemas.canonical_motion import (
    CanonicalHumanoidMotion,
    HumanoidBoneName,
)


def make_synthetic_g1_feature_vector(
    root_x: float = 0.0,
    root_y: float = 0.95,
    root_z: float = 0.0,
    heading_deg: float = 0.0,
) -> np.ndarray:
    """Create a synthetic 414-dimensional MotionBricks feature vector."""
    feat = np.zeros(414, dtype=np.float64)

    # 1. Root position (0..2)
    feat[0] = root_x
    feat[1] = root_y
    feat[2] = root_z

    # 2. Heading (3..4)
    rad = np.radians(heading_deg)
    feat[3] = np.cos(rad)
    feat[4] = np.sin(rad)

    # 3. ric_data (5..103) - 33 joints * 3
    # leave as zeros or basic offsets

    # 4. global_rot_data (104..307) - 34 joints * 6D cont rotation
    # Default to identity for all joints: [1, 0, 0, 0, 1, 0]
    for j in range(34):
        offset = 104 + j * 6
        feat[offset:offset + 6] = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]

    # 5. local_vel (308..409) - 102
    # 6. foot_contacts (410..413)
    feat[410] = 1.0  # left ankle
    feat[411] = 1.0  # left toe
    feat[412] = 0.0  # right ankle
    feat[413] = 0.0  # right toe

    return feat


def test_g1_reconstructor_parses_features():
    reconstructor = G1SkeletonReconstructor()
    feat = make_synthetic_g1_feature_vector(root_x=0.2, root_y=0.98, root_z=1.5, heading_deg=0.0)

    g1_frame = reconstructor.reconstruct_from_feature_vector(feat)

    assert np.allclose(g1_frame.root_pos, [0.2, 0.98, 1.5])
    assert g1_frame.global_rot_mats.shape == (34, 3, 3)
    assert g1_frame.local_rot_mats.shape == (34, 3, 3)
    assert g1_frame.local_rot_quats.shape == (34, 4)
    assert g1_frame.foot_contacts["left_ankle"] is True
    assert g1_frame.foot_contacts["right_ankle"] is False


def test_retargeter_produces_valid_canonical_frame():
    reconstructor = G1SkeletonReconstructor()
    retargeter = G1ToHumanoidRetargeter()

    feat = make_synthetic_g1_feature_vector(root_x=0.0, root_y=1.0, root_z=0.5)
    g1_frame = reconstructor.reconstruct_from_feature_vector(feat)

    can_frame = retargeter.retarget_frame(g1_frame, timestamp=0.0, frame_index=0)

    # Root position in canonical space (180 deg Y flip: x' = -x, z' = -z)
    assert np.isclose(can_frame.root.position[0], 0.0)
    assert np.isclose(can_frame.root.position[1], 1.0)
    assert np.isclose(can_frame.root.position[2], -0.5)

    # Required humanoid bones present
    assert HumanoidBoneName.HIPS.value in can_frame.bones
    assert HumanoidBoneName.SPINE.value in can_frame.bones
    assert HumanoidBoneName.LEFT_UPPER_LEG.value in can_frame.bones
    assert HumanoidBoneName.RIGHT_UPPER_LEG.value in can_frame.bones

    # Check foot contacts transferred
    assert can_frame.contacts.leftFoot is True
    assert can_frame.contacts.rightFoot is False


def test_retargeter_full_sequence_validation():
    reconstructor = G1SkeletonReconstructor()
    retargeter = G1ToHumanoidRetargeter()

    g1_frames = [
        reconstructor.reconstruct_from_feature_vector(make_synthetic_g1_feature_vector(root_z=0.0)),
        reconstructor.reconstruct_from_feature_vector(make_synthetic_g1_feature_vector(root_z=0.1)),
        reconstructor.reconstruct_from_feature_vector(make_synthetic_g1_feature_vector(root_z=0.2)),
    ]

    canonical_motion = retargeter.retarget_sequence(g1_frames, fps=30.0)

    assert isinstance(canonical_motion, CanonicalHumanoidMotion)
    assert canonical_motion.metadata.num_frames == 3
    assert len(canonical_motion.frames) == 3
    assert canonical_motion.frames[2].timestamp == pytest.approx(2.0 / 30.0)
