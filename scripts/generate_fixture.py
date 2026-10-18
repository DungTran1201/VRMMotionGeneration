"""Deterministic generator for CanonicalHumanoidMotion/v1 sample fixture.

Generates a mathematically defined, biomechanically plausible humanoid
locomotion cycle with root translation, spine twist, arm swings,
leg flexion/extension, and synchronized foot contacts.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List

import numpy as np

from motionbricks_vrm.reconstruction.math_utils import (
    euler_to_matrix,
    matrix_to_quaternion_xyzw,
    normalize_quaternion,
)
from motionbricks_vrm.schemas.canonical_motion import (
    AnimationFrame,
    BoneTransform,
    CanonicalHumanoidMotion,
    CoordinateSystem,
    FootContacts,
    HumanoidBoneName,
    MotionDiagnostics,
    MotionMetadata,
    MotionSource,
    RootTransform,
    RotationFormat,
)


def generate_walking_fixture(
    num_frames: int = 60,
    fps: float = 30.0,
    stride_speed: float = 1.0,
) -> CanonicalHumanoidMotion:
    """Generate a 2-second (60 frames at 30 fps) walking cycle."""
    duration = (num_frames - 1) / fps
    cycle_freq = 1.0  # 1 full double-step cycle per second (2 Hz step frequency)

    frames: List[AnimationFrame] = []

    for i in range(num_frames):
        t = i / fps
        phase = 2.0 * math.pi * cycle_freq * t

        # 1. Root Motion (in Canonical glTF space: +X right, +Y up, -Z forward)
        # Forward translation along -Z
        root_z = -stride_speed * t
        # Vertical bounce: 2 bounces per cycle (one per step)
        root_y = 0.95 + 0.03 * math.cos(2.0 * phase)
        # Lateral sway: 1 sway cycle per gait cycle
        root_x = 0.04 * math.sin(phase)

        # Root slight roll and yaw with sway
        root_yaw = 0.05 * math.sin(phase)
        root_pitch = 0.03 * math.sin(2.0 * phase)
        r_root = euler_to_matrix(0.0, root_pitch, root_yaw)
        q_root = matrix_to_quaternion_xyzw(r_root).tolist()

        # 2. Spine & Torso Counter-twist
        spine_twist = -0.08 * math.sin(phase)  # counter-rotates with hips
        r_spine = euler_to_matrix(0.0, 0.0, spine_twist)
        q_spine = matrix_to_quaternion_xyzw(r_spine).tolist()

        # 3. Leg Kinematics (Flexion / Extension)
        # Left Leg
        hip_left_pitch = 0.35 * math.sin(phase)
        knee_left_flex = 0.50 * max(0.0, -math.sin(phase)) ** 1.5
        ankle_left_pitch = -0.15 * math.sin(phase)

        # Right Leg (180 deg phase shift)
        hip_right_pitch = -0.35 * math.sin(phase)
        knee_right_flex = 0.50 * max(0.0, math.sin(phase)) ** 1.5
        ankle_right_pitch = 0.15 * math.sin(phase)

        q_l_hip = matrix_to_quaternion_xyzw(euler_to_matrix(hip_left_pitch, 0.0, 0.0)).tolist()
        q_l_knee = matrix_to_quaternion_xyzw(euler_to_matrix(-knee_left_flex, 0.0, 0.0)).tolist()
        q_l_foot = matrix_to_quaternion_xyzw(euler_to_matrix(ankle_left_pitch, 0.0, 0.0)).tolist()

        q_r_hip = matrix_to_quaternion_xyzw(euler_to_matrix(hip_right_pitch, 0.0, 0.0)).tolist()
        q_r_knee = matrix_to_quaternion_xyzw(euler_to_matrix(-knee_right_flex, 0.0, 0.0)).tolist()
        q_r_foot = matrix_to_quaternion_xyzw(euler_to_matrix(ankle_right_pitch, 0.0, 0.0)).tolist()

        # 4. Arm Swings (Left arm swings opposite to left leg)
        arm_left_pitch = -0.30 * math.sin(phase)
        arm_right_pitch = 0.30 * math.sin(phase)
        elbow_base_flex = -0.25

        q_l_arm = matrix_to_quaternion_xyzw(euler_to_matrix(arm_left_pitch, 0.0, 0.05)).tolist()
        q_r_arm = matrix_to_quaternion_xyzw(euler_to_matrix(arm_right_pitch, 0.0, -0.05)).tolist()
        q_l_elbow = matrix_to_quaternion_xyzw(euler_to_matrix(elbow_base_flex, 0.0, 0.0)).tolist()
        q_r_elbow = matrix_to_quaternion_xyzw(euler_to_matrix(elbow_base_flex, 0.0, 0.0)).tolist()

        # Neutral identity for stationary / stabilized joints
        q_identity = [0.0, 0.0, 0.0, 1.0]

        bones: Dict[str, BoneTransform] = {
            HumanoidBoneName.HIPS.value: BoneTransform(rotation=q_identity),
            HumanoidBoneName.SPINE.value: BoneTransform(rotation=q_spine),
            HumanoidBoneName.CHEST.value: BoneTransform(rotation=q_identity),
            HumanoidBoneName.NECK.value: BoneTransform(rotation=q_identity),
            HumanoidBoneName.HEAD.value: BoneTransform(rotation=q_identity),

            HumanoidBoneName.LEFT_UPPER_LEG.value: BoneTransform(rotation=q_l_hip),
            HumanoidBoneName.LEFT_LOWER_LEG.value: BoneTransform(rotation=q_l_knee),
            HumanoidBoneName.LEFT_FOOT.value: BoneTransform(rotation=q_l_foot),
            HumanoidBoneName.LEFT_TOES.value: BoneTransform(rotation=q_identity),

            HumanoidBoneName.RIGHT_UPPER_LEG.value: BoneTransform(rotation=q_r_hip),
            HumanoidBoneName.RIGHT_LOWER_LEG.value: BoneTransform(rotation=q_r_knee),
            HumanoidBoneName.RIGHT_FOOT.value: BoneTransform(rotation=q_r_foot),
            HumanoidBoneName.RIGHT_TOES.value: BoneTransform(rotation=q_identity),

            HumanoidBoneName.LEFT_SHOULDER.value: BoneTransform(rotation=q_identity),
            HumanoidBoneName.LEFT_UPPER_ARM.value: BoneTransform(rotation=q_l_arm),
            HumanoidBoneName.LEFT_LOWER_ARM.value: BoneTransform(rotation=q_l_elbow),
            HumanoidBoneName.LEFT_HAND.value: BoneTransform(rotation=q_identity),

            HumanoidBoneName.RIGHT_SHOULDER.value: BoneTransform(rotation=q_identity),
            HumanoidBoneName.RIGHT_UPPER_ARM.value: BoneTransform(rotation=q_r_arm),
            HumanoidBoneName.RIGHT_LOWER_ARM.value: BoneTransform(rotation=q_r_elbow),
            HumanoidBoneName.RIGHT_HAND.value: BoneTransform(rotation=q_identity),
        }

        # 5. Foot Contacts (Stance vs Swing)
        # Left foot in stance when hip is extending (pitch >= -0.05)
        left_stance = math.sin(phase) > -0.1
        right_stance = math.sin(phase) < 0.1

        contacts = FootContacts(
            leftFoot=bool(left_stance),
            rightFoot=bool(right_stance),
            leftToe=bool(left_stance and math.sin(phase) > 0.3),
            rightToe=bool(right_stance and math.sin(phase) < -0.3),
        )

        frames.append(
            AnimationFrame(
                timestamp=float(round(t, 6)),
                frame_index=int(i),
                root=RootTransform(
                    position=[round(root_x, 5), round(root_y, 5), round(root_z, 5)],
                    rotation=[round(v, 6) for v in q_root],
                ),
                bones=bones,
                contacts=contacts,
                diagnostics=MotionDiagnostics(warnings=[]),
            )
        )

    metadata = MotionMetadata(
        source=MotionSource.FIXTURE,
        fps=float(fps),
        duration=float(round(duration, 6)),
        num_frames=int(num_frames),
        coordinate_system=CoordinateSystem.GLTF_Y_UP,
        units="meters",
        rotation_format=RotationFormat.QUATERNION_XYZW,
        retargeting_profile="deterministic_bipedal_walk_v1",
        retargeting_version="1.0.0",
        generator_info="generate_fixture.py (Mode A Offline Fixture)",
    )

    motion = CanonicalHumanoidMotion(
        schema="CanonicalHumanoidMotion/v1",
        metadata=metadata,
        frames=frames,
    )
    return motion


if __name__ == "__main__":
    out_path = Path(__file__).resolve().parent.parent / "fixtures" / "sample_motion.json"
    motion = generate_walking_fixture(num_frames=60, fps=30.0)
    data = motion.model_dump(by_alias=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Successfully generated validated sample fixture: {out_path} ({len(motion.frames)} frames)")
