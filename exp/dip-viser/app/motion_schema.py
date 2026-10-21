"""
Motion Schema for DiP-Viser Experiment.
Defines versioned motion representations, validation rules, and serialization.
"""
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from .config import (
    MOTION_FPS,
    NUM_JOINTS,
    SMPL_22_JOINT_NAMES,
    JOINT_PARENTS,
    SKELETON_BONES,
)


class MotionValidationError(ValueError):
    """Raised when motion data fails contract validation."""
    pass


@dataclass
class MotionClip:
    """
    Standardized, validated 3D skeleton motion clip.
    Coordinate system: Metric (meters), Right-Handed (+X: Left, +Y: Up, +Z: Forward).
    """
    schema_version: str = "1.0.0"
    source_model: str = "DiP"
    source_checkpoint: str = "unknown"
    prompt: str = ""
    provenance: str = "real_inference"  # 'real_inference' or 'fixture'
    fps: float = MOTION_FPS
    num_frames: int = 0
    duration_seconds: float = 0.0
    timestamps: List[float] = field(default_factory=list)
    # Shape: (num_frames, num_joints, 3) in meters
    joint_positions: np.ndarray = field(default_factory=lambda: np.zeros((0, NUM_JOINTS, 3), dtype=np.float32))
    joint_names: List[str] = field(default_factory=lambda: list(SMPL_22_JOINT_NAMES))
    joint_parents: List[int] = field(default_factory=lambda: list(JOINT_PARENTS))
    bones: List[Tuple[int, int]] = field(default_factory=lambda: list(SKELETON_BONES))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Sync num_frames and duration if joint_positions provided
        if isinstance(self.joint_positions, np.ndarray) and self.joint_positions.ndim == 3:
            if self.num_frames == 0:
                self.num_frames = int(self.joint_positions.shape[0])
            if self.fps > 0 and self.duration_seconds == 0.0:
                self.duration_seconds = float(self.num_frames) / self.fps
            if not self.timestamps and self.num_frames > 0 and self.fps > 0:
                self.timestamps = [float(i) / self.fps for i in range(self.num_frames)]

    def validate(self) -> None:
        """
        Strict validation against contract requirements.
        Raises MotionValidationError if any invariant is violated.
        """
        if self.schema_version != "1.0.0":
            raise MotionValidationError(f"Unsupported schema version: {self.schema_version}")

        if self.provenance not in ("real_inference", "fixture"):
            raise MotionValidationError(f"Invalid provenance '{self.provenance}'. Must be 'real_inference' or 'fixture'.")

        if not isinstance(self.joint_positions, np.ndarray):
            raise MotionValidationError(f"joint_positions must be a numpy.ndarray, got {type(self.joint_positions)}")

        if self.joint_positions.ndim != 3:
            raise MotionValidationError(
                f"joint_positions must have shape (num_frames, num_joints, 3), got shape {self.joint_positions.shape}"
            )

        n_frames, n_joints, n_coords = self.joint_positions.shape

        if n_frames == 0:
            raise MotionValidationError("Motion clip contains 0 frames.")

        if n_joints != NUM_JOINTS:
            raise MotionValidationError(f"Expected {NUM_JOINTS} joints, got {n_joints}")

        if n_coords != 3:
            raise MotionValidationError(f"Expected 3 spatial coordinates (X, Y, Z), got {n_coords}")

        if self.num_frames != n_frames:
            raise MotionValidationError(f"num_frames mismatch: declared {self.num_frames}, actual {n_frames}")

        if not np.isfinite(self.joint_positions).all():
            raise MotionValidationError("joint_positions contains NaN or Inf values.")

        if self.fps <= 0.0:
            raise MotionValidationError(f"FPS must be positive, got {self.fps}")

        expected_duration = float(n_frames) / self.fps
        if abs(self.duration_seconds - expected_duration) > 0.05:
            raise MotionValidationError(
                f"duration_seconds {self.duration_seconds:.3f} does not match num_frames/fps ({expected_duration:.3f})"
            )

        if len(self.timestamps) != n_frames:
            raise MotionValidationError(
                f"timestamps length {len(self.timestamps)} does not match num_frames {n_frames}"
            )

        if len(self.joint_names) != n_joints:
            raise MotionValidationError(
                f"joint_names count {len(self.joint_names)} does not match n_joints {n_joints}"
            )

        if len(self.joint_parents) != n_joints:
            raise MotionValidationError(
                f"joint_parents count {len(self.joint_parents)} does not match n_joints {n_joints}"
            )

        # Validate hierarchy: root parent is -1, no self-parenting, no cycles
        for child_idx, parent_idx in enumerate(self.joint_parents):
            if child_idx == 0:
                if parent_idx != -1:
                    raise MotionValidationError(f"Root joint (0) must have parent -1, got {parent_idx}")
            else:
                if parent_idx < 0 or parent_idx >= n_joints:
                    raise MotionValidationError(f"Joint {child_idx} has invalid parent index {parent_idx}")
                if parent_idx == child_idx:
                    raise MotionValidationError(f"Joint {child_idx} is self-parented.")

        # Cycle detection
        for start_idx in range(n_joints):
            visited = set()
            curr = start_idx
            while curr != -1:
                if curr in visited:
                    raise MotionValidationError(f"Cycle detected in joint hierarchy involving joint {curr}")
                visited.add(curr)
                curr = self.joint_parents[curr]

        # Validate bones
        for b_idx, (j1, j2) in enumerate(self.bones):
            if not (0 <= j1 < n_joints and 0 <= j2 < n_joints):
                raise MotionValidationError(f"Bone {b_idx} references invalid joints ({j1}, {j2})")

    def get_frame(self, frame_idx: int) -> np.ndarray:
        """Return (22, 3) joint coordinates for given frame index (clamped)."""
        clamped_idx = max(0, min(self.num_frames - 1, frame_idx))
        return self.joint_positions[clamped_idx]

    def get_bone_segments(self, frame_idx: int) -> np.ndarray:
        """
        Return line segments for all bones at given frame.
        Output shape: (num_bones, 2, 3) for Viser add_line_segments.
        """
        joints = self.get_frame(frame_idx)
        segments = np.zeros((len(self.bones), 2, 3), dtype=np.float32)
        for i, (j1, j2) in enumerate(self.bones):
            segments[i, 0] = joints[j1]
            segments[i, 1] = joints[j2]
        return segments

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata and summary to dict (without huge arrays for lightweight sidecar)."""
        return {
            "schema_version": self.schema_version,
            "source_model": self.source_model,
            "source_checkpoint": self.source_checkpoint,
            "prompt": self.prompt,
            "provenance": self.provenance,
            "fps": self.fps,
            "num_frames": self.num_frames,
            "duration_seconds": round(self.duration_seconds, 4),
            "joint_count": len(self.joint_names),
            "joint_names": self.joint_names,
            "joint_parents": self.joint_parents,
            "bones": [list(b) for b in self.bones],
            "metadata": self.metadata,
        }

    def save_sidecar(self, path: Union[str, Path]) -> None:
        """Save lightweight JSON metadata sidecar."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
