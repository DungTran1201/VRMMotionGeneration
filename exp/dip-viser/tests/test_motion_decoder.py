"""
Unit tests for Motion Decoder (decoding results.npy, fixtures, shapes and errors).
"""
import pytest
import numpy as np
from pathlib import Path
import sys

EXPERIMENT_ROOT = Path(__file__).resolve().parent.parent
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from app.config import NUM_JOINTS, SAMPLES_DIR
from app.motion_decoder import create_fixture_motion, decode_results_npy
from app.motion_schema import MotionValidationError


def test_decode_real_sample_if_present():
    """Verify that actual generated DiP results.npy decodes correctly."""
    sample_path = SAMPLES_DIR / "sample_01" / "results.npy"
    if not sample_path.exists():
        pytest.skip("sample_01 not present; skipped real inference check.")

    clip = decode_results_npy(sample_path, provenance="real_inference")
    assert clip.num_frames == 80
    assert clip.joint_positions.shape == (80, 22, 3)
    assert clip.fps == 20.0
    assert clip.duration_seconds == 4.0
    assert clip.provenance == "real_inference"
    assert clip.prompt == "A person walks forward and waves."
    assert not np.isnan(clip.joint_positions).any()


def test_procedural_fixture_motion():
    """Verify procedural fixture creation and explicit 'fixture' provenance."""
    fixture = create_fixture_motion(num_frames=60, fps=20.0)
    assert fixture.provenance == "fixture"
    assert fixture.num_frames == 60
    assert fixture.duration_seconds == 3.0
    assert fixture.joint_positions.shape == (60, 22, 3)
    assert not np.isnan(fixture.joint_positions).any()
    # Check that root joint oscillates
    pelvis_heights = fixture.joint_positions[:, 0, 1]
    assert np.std(pelvis_heights) > 0.005  # Pelvis has vertical bounce


def test_decode_missing_file():
    """Verify FileNotFoundError on non-existent path."""
    with pytest.raises(FileNotFoundError):
        decode_results_npy("non_existent_results_path_12345.npy")


def test_decode_raw_array_4d():
    """Verify decoding a raw 4D array of shape (1, 22, 3, 50)."""
    raw_array = np.random.randn(1, 22, 3, 50).astype(np.float32)
    clip = decode_results_npy({"motion": raw_array}, prompt="Synthetic test")
    assert clip.num_frames == 50
    assert clip.joint_positions.shape == (50, 22, 3)
    assert clip.prompt == "Synthetic test"


def test_decode_rejects_missing_motion_key():
    """Verify rejection when dictionary lacks 'motion' key."""
    with pytest.raises(MotionValidationError, match="Missing 'motion' key"):
        decode_results_npy({"wrong_key": np.zeros((1, 22, 3, 10))})
