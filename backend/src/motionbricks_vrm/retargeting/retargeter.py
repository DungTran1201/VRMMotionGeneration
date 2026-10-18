"""G1-to-Humanoid Retargeting Engine.

Transforms reconstructed G1 robot kinematics into CanonicalHumanoidMotion/v1
animation sequences compatible with standard VRM humanoid skeletons.
"""

from __future__ import annotations

from typing import Dict, List, Optional
import numpy as np

from motionbricks_vrm.reconstruction.g1_skeleton import (
    G1_JOINT_NAMES,
    ReconstructedG1Frame,
)
from motionbricks_vrm.reconstruction.math_utils import (
    R_Y_180,
    matrix_to_quaternion_xyzw,
    motionbricks_pos_to_canonical,
    motionbricks_rot_to_canonical,
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


class G1ToHumanoidRetargeter:
    """Configurable retargeter mapping G1 34-joint hierarchy to standard Humanoid."""

    def __init__(self, profile_name: str = "g1_to_humanoid_standard", root_scale: Optional[List[float]] = None):
        self.profile_name = profile_name
        self.root_scale = np.array(root_scale or [1.0, 1.0, 1.0], dtype=np.float64)

        # Build joint index lookup
        self.j_idx = {name: i for i, name in enumerate(G1_JOINT_NAMES)}

    def retarget_frame(self, g1_frame: ReconstructedG1Frame, timestamp: float, frame_index: int) -> AnimationFrame:
        """Retarget a single reconstructed G1 frame into a Canonical AnimationFrame."""
        # 1. Root translation with coordinate conversion and scaling
        raw_root_pos = g1_frame.root_pos * self.root_scale
        can_root_pos = motionbricks_pos_to_canonical(raw_root_pos)

        # 2. Root orientation (pelvis)
        # Convert pelvis world rotation from Motion space to Canonical space
        r_pelvis_motion = g1_frame.global_rot_mats[self.j_idx["pelvis_skel"]]
        r_pelvis_can = motionbricks_rot_to_canonical(r_pelvis_motion)
        q_root = matrix_to_quaternion_xyzw(r_pelvis_can)

        # 3. Composed humanoid bone rotations
        # For any joint relative to ancestor: R_rel = (R_world[ancestor])^T * R_world[child]
        # Then convert to canonical space: R_can = R_Y_180 * R_rel * R_Y_180^T
        mats = g1_frame.global_rot_mats

        def get_rel_rot_quat(ancestor_idx: int, child_idx: int) -> List[float]:
            r_anc = mats[ancestor_idx]
            r_ch = mats[child_idx]
            r_rel_motion = r_anc.T @ r_ch
            r_rel_can = motionbricks_rot_to_canonical(r_rel_motion)
            return matrix_to_quaternion_xyzw(r_rel_can).tolist()

        bones: Dict[str, BoneTransform] = {}

        # Hips (local rotation relative to parent root: identity since root is hips)
        bones[HumanoidBoneName.HIPS.value] = BoneTransform(
            rotation=[0.0, 0.0, 0.0, 1.0]
        )

        # Spine: waist_pitch (17) relative to pelvis (0)
        bones[HumanoidBoneName.SPINE.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["pelvis_skel"], self.j_idx["waist_pitch_skel"])
        )

        # Chest / UpperChest: G1 has a single waist chain, so chest keeps neutral relative to spine
        bones[HumanoidBoneName.CHEST.value] = BoneTransform(
            rotation=[0.0, 0.0, 0.0, 1.0]
        )

        # Neck and Head: G1 torso has fixed head mount, keep neutral
        bones[HumanoidBoneName.NECK.value] = BoneTransform(
            rotation=[0.0, 0.0, 0.0, 1.0]
        )
        bones[HumanoidBoneName.HEAD.value] = BoneTransform(
            rotation=[0.0, 0.0, 0.0, 1.0]
        )

        # Left Leg
        # UpperLeg: left_hip_yaw (3) relative to pelvis (0)
        bones[HumanoidBoneName.LEFT_UPPER_LEG.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["pelvis_skel"], self.j_idx["left_hip_yaw_skel"])
        )
        # LowerLeg: left_knee (4) relative to left_hip_yaw (3)
        bones[HumanoidBoneName.LEFT_LOWER_LEG.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["left_hip_yaw_skel"], self.j_idx["left_knee_skel"])
        )
        # Foot: left_ankle_roll (6) relative to left_knee (4)
        bones[HumanoidBoneName.LEFT_FOOT.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["left_knee_skel"], self.j_idx["left_ankle_roll_skel"])
        )
        # Toes: left_toe_base (7) relative to left_ankle_roll (6)
        bones[HumanoidBoneName.LEFT_TOES.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["left_ankle_roll_skel"], self.j_idx["left_toe_base"])
        )

        # Right Leg
        # UpperLeg: right_hip_yaw (10) relative to pelvis (0)
        bones[HumanoidBoneName.RIGHT_UPPER_LEG.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["pelvis_skel"], self.j_idx["right_hip_yaw_skel"])
        )
        # LowerLeg: right_knee (11) relative to right_hip_yaw (10)
        bones[HumanoidBoneName.RIGHT_LOWER_LEG.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["right_hip_yaw_skel"], self.j_idx["right_knee_skel"])
        )
        # Foot: right_ankle_roll (13) relative to right_knee (11)
        bones[HumanoidBoneName.RIGHT_FOOT.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["right_knee_skel"], self.j_idx["right_ankle_roll_skel"])
        )
        # Toes: right_toe_base (14) relative to right_ankle_roll (13)
        bones[HumanoidBoneName.RIGHT_TOES.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["right_ankle_roll_skel"], self.j_idx["right_toe_base"])
        )

        # Left Arm
        # Shoulder: left_shoulder_pitch (18) relative to waist_pitch (17)
        bones[HumanoidBoneName.LEFT_SHOULDER.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["waist_pitch_skel"], self.j_idx["left_shoulder_pitch_skel"])
        )
        # UpperArm: left_shoulder_yaw (20) relative to left_shoulder_pitch (18)
        bones[HumanoidBoneName.LEFT_UPPER_ARM.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["left_shoulder_pitch_skel"], self.j_idx["left_shoulder_yaw_skel"])
        )
        # LowerArm: left_elbow (21) relative to left_shoulder_yaw (20)
        bones[HumanoidBoneName.LEFT_LOWER_ARM.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["left_shoulder_yaw_skel"], self.j_idx["left_elbow_skel"])
        )
        # Hand: left_hand_roll (25) relative to left_elbow (21)
        bones[HumanoidBoneName.LEFT_HAND.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["left_elbow_skel"], self.j_idx["left_hand_roll_skel"])
        )

        # Right Arm
        # Shoulder: right_shoulder_pitch (26) relative to waist_pitch (17)
        bones[HumanoidBoneName.RIGHT_SHOULDER.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["waist_pitch_skel"], self.j_idx["right_shoulder_pitch_skel"])
        )
        # UpperArm: right_shoulder_yaw (28) relative to right_shoulder_pitch (26)
        bones[HumanoidBoneName.RIGHT_UPPER_ARM.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["right_shoulder_pitch_skel"], self.j_idx["right_shoulder_yaw_skel"])
        )
        # LowerArm: right_elbow (29) relative to right_shoulder_yaw (28)
        bones[HumanoidBoneName.RIGHT_LOWER_ARM.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["right_shoulder_yaw_skel"], self.j_idx["right_elbow_skel"])
        )
        # Hand: right_hand_roll (33) relative to right_elbow (29)
        bones[HumanoidBoneName.RIGHT_HAND.value] = BoneTransform(
            rotation=get_rel_rot_quat(self.j_idx["right_elbow_skel"], self.j_idx["right_hand_roll_skel"])
        )

        # Foot contacts
        contacts = FootContacts(
            leftFoot=g1_frame.foot_contacts.get("left_ankle", False),
            rightFoot=g1_frame.foot_contacts.get("right_ankle", False),
            leftToe=g1_frame.foot_contacts.get("left_toe", False),
            rightToe=g1_frame.foot_contacts.get("right_toe", False),
        )

        diagnostics = MotionDiagnostics(
            approximate_bones=["chest", "neck", "head", "leftShoulder", "rightShoulder"]
        )

        return AnimationFrame(
            timestamp=float(timestamp),
            frame_index=int(frame_index),
            root=RootTransform(
                position=can_root_pos.tolist(),
                rotation=q_root.tolist(),
            ),
            bones=bones,
            contacts=contacts,
            diagnostics=diagnostics,
        )

    def retarget_sequence(
        self,
        g1_frames: List[ReconstructedG1Frame],
        fps: float = 30.0,
        source: MotionSource = MotionSource.MOTIONBRICKS,
        generator_info: Optional[str] = None
    ) -> CanonicalHumanoidMotion:
        """Retarget a full sequence of reconstructed G1 frames into CanonicalHumanoidMotion/v1."""
        num_frames = len(g1_frames)
        if num_frames == 0:
            raise ValueError("Cannot retarget empty sequence")

        duration = (num_frames - 1) / fps if num_frames > 1 else 0.0

        retargeted_frames: List[AnimationFrame] = []
        for i, frame in enumerate(g1_frames):
            t = i / fps
            retargeted_frames.append(self.retarget_frame(frame, timestamp=t, frame_index=i))

        metadata = MotionMetadata(
            source=source,
            fps=float(fps),
            duration=float(duration),
            num_frames=num_frames,
            coordinate_system=CoordinateSystem.GLTF_Y_UP,
            units="meters",
            rotation_format=RotationFormat.QUATERNION_XYZW,
            retargeting_profile=self.profile_name,
            retargeting_version="1.0.0",
            generator_info=generator_info or "G1ToHumanoidRetargeter/v1",
        )

        return CanonicalHumanoidMotion(
            schema="CanonicalHumanoidMotion/v1",
            metadata=metadata,
            frames=retargeted_frames,
        )
