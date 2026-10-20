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
