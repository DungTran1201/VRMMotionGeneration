"""Schemas package for motionbricks_vrm."""

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
    validate_quaternion_xyzw,
    validate_vec3,
)

__all__ = [
    "AnimationFrame",
    "BoneTransform",
    "CanonicalHumanoidMotion",
    "CoordinateSystem",
    "FootContacts",
    "HumanoidBoneName",
    "MotionDiagnostics",
    "MotionMetadata",
    "MotionSource",
    "RootTransform",
    "RotationFormat",
    "validate_quaternion_xyzw",
    "validate_vec3",
]
