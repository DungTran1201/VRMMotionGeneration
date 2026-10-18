"""Unit tests for CanonicalHumanoidMotion/v1 schemas and validation rules."""

import pytest
from pydantic import ValidationError

from motionbricks_vrm.schemas.canonical_motion import (
    AnimationFrame,
    BoneTransform,
    CanonicalHumanoidMotion,
    CoordinateSystem,
    HumanoidBoneName,
    MotionMetadata,
    MotionSource,
    RootTransform,
    RotationFormat,
    validate_quaternion_xyzw,
    validate_vec3,
)


def make_valid_frame(timestamp: float = 0.0, frame_index: int = 0) -> AnimationFrame:
    return AnimationFrame(
        timestamp=timestamp,
        frame_index=frame_index,
        root=RootTransform(
            position=[0.0, 1.0, 0.0],
            rotation=[0.0, 0.0, 0.0, 1.0]
        ),
        bones={
            "hips": BoneTransform(rotation=[0.0, 0.0, 0.0, 1.0]),
            "spine": BoneTransform(rotation=[0.0, 0.0, 0.0, 1.0]),
        }
    )


def test_valid_canonical_motion():
    frames = [make_valid_frame(0.0, 0), make_valid_frame(1.0 / 30.0, 1)]
    meta = MotionMetadata(
        source=MotionSource.FIXTURE,
        fps=30.0,
        duration=1.0 / 30.0,
        num_frames=2,
        coordinate_system=CoordinateSystem.GLTF_Y_UP,
        units="meters",
        rotation_format=RotationFormat.QUATERNION_XYZW
    )
    motion = CanonicalHumanoidMotion(
        schema="CanonicalHumanoidMotion/v1",
        metadata=meta,
        frames=frames
    )
    assert motion.schema_ == "CanonicalHumanoidMotion/v1"
    assert len(motion.frames) == 2


def test_reject_invalid_schema_version():
    frames = [make_valid_frame(0.0, 0)]
    meta = MotionMetadata(
        source=MotionSource.FIXTURE,
        fps=30.0,
        duration=0.0,
        num_frames=1
    )
    with pytest.raises(ValidationError) as exc:
        CanonicalHumanoidMotion(
            schema="CanonicalHumanoidMotion/v2-invalid",
            metadata=meta,
            frames=frames
        )
    assert "Unsupported schema version" in str(exc.value)


def test_reject_quaternion_nan_and_inf():
    with pytest.raises(ValueError, match="NaN or Infinite"):
        validate_quaternion_xyzw([float("nan"), 0.0, 0.0, 1.0])

    with pytest.raises(ValueError, match="NaN or Infinite"):
        validate_quaternion_xyzw([0.0, float("inf"), 0.0, 1.0])


def test_reject_non_unit_quaternion():
    # Length != 1
    with pytest.raises(ValueError, match="deviates from unit length"):
        validate_quaternion_xyzw([2.0, 0.0, 0.0, 0.0])  # norm = 2.0 -> invalid!

    with pytest.raises(ValueError, match="deviates from unit length"):
        validate_quaternion_xyzw([1.0, 1.0, 0.0, 0.0])  # norm = sqrt(2) = 1.414 -> invalid!


def test_reject_invalid_quaternion_length():
    with pytest.raises(ValueError, match="must have exactly 4 elements"):
        validate_quaternion_xyzw([0.0, 0.0, 1.0])


def test_reject_vec3_nan_and_dimension():
    with pytest.raises(ValueError, match="must have exactly 3 elements"):
        validate_vec3([0.0, 1.0])
    with pytest.raises(ValueError, match="NaN or Infinite"):
        validate_vec3([0.0, float("nan"), 1.0])


def test_reject_unknown_humanoid_bone():
    with pytest.raises(ValidationError, match="Unknown humanoid bone identifier"):
        AnimationFrame(
            timestamp=0.0,
            frame_index=0,
            root=RootTransform(position=[0.0, 0.0, 0.0], rotation=[0.0, 0.0, 0.0, 1.0]),
            bones={
                "hips": BoneTransform(rotation=[0.0, 0.0, 0.0, 1.0]),
                "fictional_tail_bone": BoneTransform(rotation=[0.0, 0.0, 0.0, 1.0]),
            }
        )


def test_reject_non_monotonic_timestamps():
    frames = [make_valid_frame(0.5, 0), make_valid_frame(0.2, 1)]
    meta = MotionMetadata(
        source=MotionSource.FIXTURE,
        fps=30.0,
        duration=1.0 / 30.0,
        num_frames=2
    )
    with pytest.raises(ValidationError, match="monotonically non-decreasing"):
        CanonicalHumanoidMotion(
            schema="CanonicalHumanoidMotion/v1",
            metadata=meta,
            frames=frames
        )


def test_reject_frame_count_mismatch():
    frames = [make_valid_frame(0.0, 0)]
    meta = MotionMetadata(
        source=MotionSource.FIXTURE,
        fps=30.0,
        duration=0.0,
        num_frames=10  # mismatch
    )
    with pytest.raises(ValidationError, match="Frame count mismatch"):
        CanonicalHumanoidMotion(
            schema="CanonicalHumanoidMotion/v1",
            metadata=meta,
            frames=frames
        )
