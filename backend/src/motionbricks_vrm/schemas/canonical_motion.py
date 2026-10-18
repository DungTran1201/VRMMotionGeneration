"""CanonicalHumanoidMotion/v1 Schema and Validation Engine.

Defines a model-independent, engine-independent humanoid motion specification
with strict mathematical validation for quaternions, timestamps, and hierarchy.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CoordinateSystem(str, Enum):
    """Supported coordinate conventions.
    
    glTF / Three.js / VRM standard convention:
    +Y is Up, +X is Right, -Z is Forward (Right-handed).
    """
    GLTF_Y_UP = "glTF_Y_UP_Z_BACK_X_RIGHT"
    MOTIONBRICKS_Y_UP = "MOTIONBRICKS_Y_UP_Z_FORWARD_X_RIGHT"


class RotationFormat(str, Enum):
    """Format for serialized rotations."""
    QUATERNION_XYZW = "quaternion_xyzw"


class MotionSource(str, Enum):
    """Origin of motion data."""
    FIXTURE = "fixture"
    MOTIONBRICKS = "motionbricks"
    SYNTHETIC = "synthetic"


class HumanoidBoneName(str, Enum):
    """Standard VRM humanoid bone identities."""
    HIPS = "hips"
    SPINE = "spine"
    CHEST = "chest"
    UPPER_CHEST = "upperChest"
    NECK = "neck"
    HEAD = "head"
    LEFT_EYE = "leftEye"
    RIGHT_EYE = "rightEye"
    JAW = "jaw"
    LEFT_SHOULDER = "leftShoulder"
    LEFT_UPPER_ARM = "leftUpperArm"
    LEFT_LOWER_ARM = "leftLowerArm"
    LEFT_HAND = "leftHand"
    RIGHT_SHOULDER = "rightShoulder"
    RIGHT_UPPER_ARM = "rightUpperArm"
    RIGHT_LOWER_ARM = "rightLowerArm"
    RIGHT_HAND = "rightHand"
    LEFT_UPPER_LEG = "leftUpperLeg"
    LEFT_LOWER_LEG = "leftLowerLeg"
    LEFT_FOOT = "leftFoot"
    LEFT_TOES = "leftToes"
    RIGHT_UPPER_LEG = "rightUpperLeg"
    RIGHT_LOWER_LEG = "rightLowerLeg"
    RIGHT_FOOT = "rightFoot"
    RIGHT_TOES = "rightToes"


def validate_quaternion_xyzw(q: List[float], tol: float = 1e-3) -> List[float]:
    """Validate 4-element quaternion [x, y, z, w] for finiteness and unit norm."""
    if len(q) != 4:
        raise ValueError(f"Quaternion must have exactly 4 elements [x, y, z, w], got {len(q)}")
    for val in q:
        if math.isnan(val) or math.isinf(val):
            raise ValueError(f"Quaternion contains NaN or Infinite value: {q}")
    norm_sq = sum(v * v for v in q)
    norm = math.sqrt(norm_sq)
    if abs(norm - 1.0) > tol:
        raise ValueError(f"Quaternion norm ({norm:.6f}) deviates from unit length by > {tol}: {q}")
    return q


def validate_vec3(v: List[float]) -> List[float]:
    """Validate 3-element vector [x, y, z] for finiteness."""
    if len(v) != 3:
        raise ValueError(f"Vector3 must have exactly 3 elements [x, y, z], got {len(v)}")
    for val in v:
        if math.isnan(val) or math.isinf(val):
            raise ValueError(f"Vector3 contains NaN or Infinite value: {v}")
    return v


class RootTransform(BaseModel):
    """World-space translation and orientation of humanoid root (hips)."""
    position: List[float] = Field(..., description="[x, y, z] world coordinates in meters")
    rotation: List[float] = Field(..., description="[x, y, z, w] world quaternion")

    @field_validator("position")
    @classmethod
    def check_position(cls, v: List[float]) -> List[float]:
        return validate_vec3(v)

    @field_validator("rotation")
    @classmethod
    def check_rotation(cls, v: List[float]) -> List[float]:
        return validate_quaternion_xyzw(v)


class BoneTransform(BaseModel):
    """Local-space rotation of a humanoid bone relative to its parent."""
    rotation: List[float] = Field(..., description="[x, y, z, w] local quaternion")
    position: Optional[List[float]] = Field(None, description="Optional local translation offset [x, y, z]")

    @field_validator("rotation")
    @classmethod
    def check_rotation(cls, v: List[float]) -> List[float]:
        return validate_quaternion_xyzw(v)

    @field_validator("position")
    @classmethod
    def check_position(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        if v is not None:
            return validate_vec3(v)
        return v


class FootContacts(BaseModel):
    """Binary foot contact states for IK and foot locking."""
    leftFoot: bool = False
    rightFoot: bool = False
    leftToe: Optional[bool] = None
    rightToe: Optional[bool] = None


class MotionDiagnostics(BaseModel):
    """Diagnostic annotations for quality, IK solver status, or retargeting."""
    ik_residual: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)
    approximate_bones: List[str] = Field(default_factory=list)


class AnimationFrame(BaseModel):
    """A single discrete time-step in a Canonical Humanoid animation."""
    timestamp: float = Field(..., ge=0.0, description="Time in seconds from motion onset")
    frame_index: Optional[int] = Field(None, ge=0, description="0-indexed frame sequence number")
    root: RootTransform
    bones: Dict[str, BoneTransform] = Field(
        ..., description="Map of humanoid bone names to their local rotation/translation"
    )
    contacts: Optional[FootContacts] = None
    diagnostics: Optional[MotionDiagnostics] = None

    @field_validator("bones")
    @classmethod
    def check_bones(cls, v: Dict[str, BoneTransform]) -> Dict[str, BoneTransform]:
        if not v:
            raise ValueError("Frame must define at least one bone transform")
        valid_bone_names = {b.value for b in HumanoidBoneName}
        for bone_name in v.keys():
            if bone_name not in valid_bone_names:
                raise ValueError(
                    f"Unknown humanoid bone identifier '{bone_name}'. Must be one of {valid_bone_names}"
                )
        return v


class MotionMetadata(BaseModel):
    """Header metadata for Canonical Humanoid Motion sequence."""
    source: MotionSource = Field(..., description="Origin of motion data")
    fps: float = Field(..., gt=0.0, le=240.0, description="Sampling rate in frames per second")
    duration: float = Field(..., ge=0.0, description="Total sequence duration in seconds")
    num_frames: int = Field(..., gt=0, description="Total number of frames")
    coordinate_system: CoordinateSystem = CoordinateSystem.GLTF_Y_UP
    units: str = Field("meters", description="Linear measurement unit")
    rotation_format: RotationFormat = RotationFormat.QUATERNION_XYZW
    retargeting_profile: Optional[str] = None
    retargeting_version: Optional[str] = None
    generator_info: Optional[str] = None


class CanonicalHumanoidMotion(BaseModel):
    """Canonical Humanoid Motion Document (Schema CanonicalHumanoidMotion/v1)."""
    schema_: str = Field("CanonicalHumanoidMotion/v1", alias="schema")
    metadata: MotionMetadata
    frames: List[AnimationFrame]

    @model_validator(mode="after")
    def validate_motion_consistency(self) -> CanonicalHumanoidMotion:
        if self.schema_ != "CanonicalHumanoidMotion/v1":
            raise ValueError(
                f"Unsupported schema version '{self.schema_}'. Expected 'CanonicalHumanoidMotion/v1'"
            )

        num_frames = len(self.frames)
        if num_frames != self.metadata.num_frames:
            raise ValueError(
                f"Frame count mismatch: metadata specifies {self.metadata.num_frames} frames, "
                f"but frames list contains {num_frames}"
            )

        # Validate timestamps strictly monotonic
        prev_t = -1e-9
        for i, frame in enumerate(self.frames):
            if frame.timestamp < prev_t:
                raise ValueError(
                    f"Timestamps must be monotonically non-decreasing. Frame {i} has timestamp "
                    f"{frame.timestamp:.6f}s < previous timestamp {prev_t:.6f}s"
                )
            prev_t = frame.timestamp

        # Validate duration consistency (with tolerance for 1/fps)
        expected_duration = (num_frames - 1) / self.metadata.fps if num_frames > 1 else 0.0
        if abs(self.metadata.duration - expected_duration) > (2.0 / self.metadata.fps):
            raise ValueError(
                f"Duration mismatch: metadata duration {self.metadata.duration:.4f}s deviates "
                f"significantly from calculated duration {expected_duration:.4f}s at {self.metadata.fps} fps"
            )

        return self

    model_config = ConfigDict(populate_by_name=True)
