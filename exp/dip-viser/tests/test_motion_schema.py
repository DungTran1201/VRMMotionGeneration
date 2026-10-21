"""
Unit tests for MotionClip schema validation, topology, cycles and constraints.
"""
import pytest
import numpy as np
import sys
from pathlib import Path

# Add experiment root to sys.path
EXPERIMENT_ROOT = Path(__file__).resolve().parent.parent
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from app.config import NUM_JOINTS
from app.motion_schema import MotionClip, MotionValidationError


def test_valid_motion_clip():
    """Verify that a properly constructed motion clip passes validation."""
    n_frames = 40
    positions = np.zeros((n_frames, NUM_JOINTS, 3), dtype=np.float32)
    clip = MotionClip(
        num_frames=n_frames,
        fps=20.0,
        joint_positions=positions,
        prompt="A person walks.",
        provenance="real_inference",
    )
    clip.validate()
    assert clip.num_frames == 40
    assert clip.duration_seconds == 2.0
    assert len(clip.timestamps) == 40
    assert clip.timestamps[0] == 0.0
    assert clip.timestamps[-1] == 39.0 / 20.0


def test_reject_nan_values():
    """Verify that non-finite values (NaN / Inf) trigger validation failure."""
    positions = np.zeros((20, NUM_JOINTS, 3), dtype=np.float32)
    positions[5, 2, 1] = np.nan
    clip = MotionClip(joint_positions=positions)
    with pytest.raises(MotionValidationError, match="NaN or Inf"):
        clip.validate()


def test_reject_inf_values():
    """Verify that infinity values trigger validation failure."""
    positions = np.zeros((20, NUM_JOINTS, 3), dtype=np.float32)
    positions[2, 0, 0] = np.inf
    clip = MotionClip(joint_positions=positions)
    with pytest.raises(MotionValidationError, match="NaN or Inf"):
        clip.validate()


def test_reject_invalid_shape():
    """Verify that incorrect number of joints or dimensions is rejected."""
    # 21 joints instead of 22
    wrong_joints = np.zeros((20, 21, 3), dtype=np.float32)
    clip = MotionClip(joint_positions=wrong_joints)
    with pytest.raises(MotionValidationError, match="Expected 22 joints"):
        clip.validate()

    # 2D instead of 3D
    wrong_dim = np.zeros((20, 22), dtype=np.float32)
    clip_dim = MotionClip(joint_positions=wrong_dim)
    with pytest.raises(MotionValidationError, match="must have shape"):
        clip_dim.validate()


def test_reject_invalid_provenance():
    """Verify that provenance must be 'real_inference' or 'fixture'."""
    positions = np.zeros((10, NUM_JOINTS, 3), dtype=np.float32)
    clip = MotionClip(joint_positions=positions, provenance="unverified_fake")
    with pytest.raises(MotionValidationError, match="Invalid provenance"):
        clip.validate()


def test_topology_cycle_detection():
    """Verify that cyclic joint hierarchies are detected and rejected."""
    positions = np.zeros((10, NUM_JOINTS, 3), dtype=np.float32)
    clip = MotionClip(joint_positions=positions)
    # Create an artificial cycle: joint 3 -> joint 6 -> joint 3
    corrupt_parents = list(clip.joint_parents)
    corrupt_parents[3] = 6
    corrupt_parents[6] = 3
    clip.joint_parents = corrupt_parents
    with pytest.raises(MotionValidationError, match="Cycle detected"):
        clip.validate()


def test_topology_self_parenting():
    """Verify that a non-root joint parenting itself is rejected."""
    positions = np.zeros((10, NUM_JOINTS, 3), dtype=np.float32)
    clip = MotionClip(joint_positions=positions)
    corrupt_parents = list(clip.joint_parents)
    corrupt_parents[4] = 4  # L_Knee parents L_Knee
    clip.joint_parents = corrupt_parents
    with pytest.raises(MotionValidationError, match="self-parented"):
        clip.validate()


def test_frame_clamping():
    """Verify get_frame clamps bounds and returns correct slice."""
    positions = np.arange(10 * NUM_JOINTS * 3, dtype=np.float32).reshape(10, NUM_JOINTS, 3)
    clip = MotionClip(joint_positions=positions)
    clip.validate()
    
    # Frame 0
    np.testing.assert_array_equal(clip.get_frame(0), positions[0])
    # Frame 9
    np.testing.assert_array_equal(clip.get_frame(9), positions[9])
    # Negative frame clamps to 0
    np.testing.assert_array_equal(clip.get_frame(-5), positions[0])
    # Exceeded frame clamps to last frame
    np.testing.assert_array_equal(clip.get_frame(100), positions[9])


def test_bone_segments_shape():
    """Verify get_bone_segments returns (num_bones, 2, 3) correctly."""
    positions = np.ones((5, NUM_JOINTS, 3), dtype=np.float32)
    clip = MotionClip(joint_positions=positions)
    segments = clip.get_bone_segments(0)
    assert segments.shape == (len(clip.bones), 2, 3)
    # Both endpoints should equal 1.0
    assert np.all(segments == 1.0)
