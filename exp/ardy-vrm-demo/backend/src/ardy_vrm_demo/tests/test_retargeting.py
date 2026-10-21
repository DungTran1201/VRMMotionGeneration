"""Unit tests for CoreSkeleton27 to VRM Humanoid retargeting and payload creation."""

import numpy as np
import pytest

from ardy_vrm_demo.motion_adapter.vrm_retargeter import (
    CORE_TO_VRM_BONE_MAP,
    create_unified_motion_payload,
)
from ardy_vrm_demo.schemas import GenerationTelemetry


def test_vrm_retargeting_payload_structure():
    """Verify retargeting creates proper VRM 1.0 bone tracks and valid skeleton data."""
    T, J = 60, 27
    fps = 20.0
    rot_mats = np.tile(np.eye(3), (T, J, 1, 1)).astype(np.float32)
    root_pos = np.zeros((T, 3), dtype=np.float32)

    telemetry = GenerationTelemetry(
        model_name="ARDY-Core-RP-20FPS-Horizon8",
        device="cuda:0",
        prompt="A person walks forward.",
        seed=42,
        requested_duration=3.0,
        actual_duration=3.0,
        total_frames=60,
        fps=20.0,
        generation_time_seconds=1.6,
        effective_generated_fps=37.5,
        real_time_factor=0.53,
        retarget_time_ms=10.0,
        end_to_end_latency_ms=1610.0,
        peak_vram_mb=885.0,
    )

    payload = create_unified_motion_payload(
        local_rot_mats=rot_mats,
        root_positions=root_pos,
        fps=fps,
        prompt="A person walks forward.",
        seed=42,
        source_model="ARDY-Core-RP-20FPS-Horizon8",
        telemetry=telemetry,
        mode="LIVE ARDY",
    )

    assert payload.total_frames == 60
    assert payload.fps == 20.0
    assert len(payload.timestamps) == 60
    assert payload.timestamps[0] == 0.0
    assert round(payload.timestamps[-1], 2) == 2.95

    # Check that all mapped bones exist in VRM payload
    for _, (_, vrm_bone) in CORE_TO_VRM_BONE_MAP.items():
        assert vrm_bone in payload.vrm.bones
        assert len(payload.vrm.bones[vrm_bone]) == 60
        # Each bone frame has 4 quaternion elements [x, y, z, w]
        assert len(payload.vrm.bones[vrm_bone][0]) == 4

    # Check skeleton joint positions
    assert len(payload.skeleton.joint_positions) == 60
    assert len(payload.skeleton.joint_positions[0]) == 27
    assert len(payload.skeleton.bone_names) == 27


def test_retargeting_rejects_non_finite_values():
    """Retargeting engine must throw ValueError when encountering NaN or Inf values."""
    T, J = 10, 27
    rot_mats = np.tile(np.eye(3), (T, J, 1, 1)).astype(np.float32)
    rot_mats[5, 0, 0, 0] = np.nan
    root_pos = np.zeros((T, 3), dtype=np.float32)

    telemetry = GenerationTelemetry(
        model_name="test",
        device="cpu",
        prompt="test",
        seed=0,
        requested_duration=1.0,
        actual_duration=1.0,
        total_frames=10,
        fps=10.0,
        generation_time_seconds=0.1,
        effective_generated_fps=100.0,
        real_time_factor=0.1,
        retarget_time_ms=1.0,
        end_to_end_latency_ms=101.0,
    )

    with pytest.raises(ValueError, match="Non-finite"):
        create_unified_motion_payload(
            local_rot_mats=rot_mats,
            root_positions=root_pos,
            fps=10.0,
            prompt="test",
            seed=0,
            source_model="test",
            telemetry=telemetry,
        )


def test_arm_raise_retargeting_matches_skeleton():
    """Verify that when arms are raised, VRM bone orientations match Skeleton bone vectors."""
    from scipy.spatial.transform import Rotation
    from ardy_vrm_demo.motion_adapter.core_skeleton import forward_kinematics

    T, J = 5, 27
    fps = 20.0
    rot_mats = np.tile(np.eye(3), (T, J, 1, 1)).astype(np.float64)

    # In rest pose, RightArm points along -X [-1, 0, 0].
    # Raise RightArm 90 deg (Euler 'z', 90 deg) -> points down along -Y
    r_raise = Rotation.from_euler("z", 90, degrees=True).as_matrix()
    rot_mats[:, 8] = r_raise  # RightArm (8)

    root_pos = np.zeros((T, 3), dtype=np.float64)
    telemetry = GenerationTelemetry(
        model_name="test",
        device="cpu",
        prompt="test arm raise",
        seed=1,
        requested_duration=0.25,
        actual_duration=0.25,
        total_frames=T,
        fps=fps,
        generation_time_seconds=0.01,
        effective_generated_fps=500.0,
        real_time_factor=0.04,
        retarget_time_ms=1.0,
        end_to_end_latency_ms=11.0,
    )

    payload = create_unified_motion_payload(
        local_rot_mats=rot_mats,
        root_positions=root_pos,
        fps=fps,
        prompt="test arm raise",
        seed=1,
        source_model="test",
        telemetry=telemetry,
    )

    # 1. Compute Skeleton Right Upper Arm direction: joint 8 to joint 9
    p8 = np.array(payload.skeleton.joint_positions[0][8])
    p9 = np.array(payload.skeleton.joint_positions[0][9])
    skel_arm_dir = (p9 - p8) / np.linalg.norm(p9 - p8)

    # 2. Compute VRM Right Upper Arm direction:
    # In VRM T-pose, rightUpperArm points along -X [-1, 0, 0].
    # Apply VRM rightShoulder and rightUpperArm quaternions
    q_shoulder = payload.vrm.bones["rightShoulder"][0]
    q_arm = payload.vrm.bones["rightUpperArm"][0]
    r_shoulder = Rotation.from_quat(q_shoulder)
    r_arm = Rotation.from_quat(q_arm)
    vrm_arm_dir = (r_shoulder * r_arm).apply([-1.0, 0.0, 0.0])

    assert np.allclose(skel_arm_dir, vrm_arm_dir, atol=1e-4), (
        f"Skeleton arm dir {skel_arm_dir} does not match VRM arm dir {vrm_arm_dir}"
    )


def test_asymmetric_arm_raise_no_left_right_swap():
    """Verify that raising only the right arm leaves the left arm in resting horizontal position."""
    from scipy.spatial.transform import Rotation

    T, J = 3, 27
    rot_mats = np.tile(np.eye(3), (T, J, 1, 1)).astype(np.float64)

    # Right arm raised 60 deg, left arm identity (rest horizontal +X)
    rot_mats[:, 8] = Rotation.from_euler("z", 60, degrees=True).as_matrix()

    root_pos = np.zeros((T, 3), dtype=np.float64)
    telemetry = GenerationTelemetry(
        model_name="test",
        device="cpu",
        prompt="asymmetric arm test",
        seed=2,
        requested_duration=0.15,
        actual_duration=0.15,
        total_frames=T,
        fps=20.0,
        generation_time_seconds=0.01,
        effective_generated_fps=300.0,
        real_time_factor=0.06,
        retarget_time_ms=1.0,
        end_to_end_latency_ms=11.0,
    )

    payload = create_unified_motion_payload(
        local_rot_mats=rot_mats,
        root_positions=root_pos,
        fps=20.0,
        prompt="asymmetric arm test",
        seed=2,
        source_model="test",
        telemetry=telemetry,
    )

    # Left arm in VRM: should be near identity
    q_left_arm = payload.vrm.bones["leftUpperArm"][0]
    left_rot = Rotation.from_quat(q_left_arm)
    v_left = left_rot.apply([1.0, 0.0, 0.0])
    assert np.allclose(v_left, [1.0, 0.0, 0.0], atol=1e-4), "Left arm must remain in rest pose!"

    # Right arm in VRM: must be rotated
    q_right_arm = payload.vrm.bones["rightUpperArm"][0]
    right_rot = Rotation.from_quat(q_right_arm)
    v_right = right_rot.apply([-1.0, 0.0, 0.0])
    assert not np.allclose(v_right, [-1.0, 0.0, 0.0], atol=1e-2), "Right arm must be actively rotated!"

