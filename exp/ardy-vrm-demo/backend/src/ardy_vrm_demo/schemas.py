"""Pydantic schemas for ARDY VRM Demo API contracts and motion representations."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str = "ok"
    mode: str = "LIVE ARDY"  # LIVE ARDY | BATCH ARDY | FIXTURE PREVIEW | MODEL UNAVAILABLE
    device: str
    torch_version: str
    cuda_available: bool
    gpu_name: Optional[str] = None
    vram_free_mb: Optional[float] = None
    checkpoint_ready: bool
    model_name: str
    active_jobs: int


class ModelInfo(BaseModel):
    alias: str
    full_name: str
    skeleton: str
    fps: float
    horizon: int
    available: bool
    description: str


class ModelsResponse(BaseModel):
    models: List[ModelInfo]


class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=500, description="Text conditioning prompt")
    duration_seconds: float = Field(3.0, ge=0.5, le=10.0, description="Desired motion duration in seconds")
    model: str = Field("ARDY-Core-RP-20FPS-Horizon8", description="Target ARDY checkpoint alias")
    seed: Optional[int] = Field(None, description="Optional random seed for reproducible generation")

    @field_validator("prompt")
    @classmethod
    def validate_prompt_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Prompt must not be empty or whitespace only.")
        return v.strip()


class GenerationTelemetry(BaseModel):
    model_name: str
    device: str
    prompt: str
    seed: int
    requested_duration: float
    actual_duration: float
    total_frames: int
    fps: float
    model_load_time_seconds: Optional[float] = None
    generation_time_seconds: float
    effective_generated_fps: float
    real_time_factor: float
    retarget_time_ms: float
    end_to_end_latency_ms: float
    peak_vram_mb: Optional[float] = None


class SkeletonJointFrame(BaseModel):
    name: str
    index: int
    parent: Optional[int]
    position: List[float]  # [x, y, z] in Three.js coordinates


class SkeletonTrack(BaseModel):
    bone_names: List[str]
    parent_indices: List[int]
    # positions[frame_idx][joint_idx] = [x, y, z]
    joint_positions: List[List[List[float]]]


class VRMRotationTrack(BaseModel):
    # rotations[bone_name][frame_idx] = [x, y, z, w]
    bones: Dict[str, List[List[float]]]
    root_translation: List[List[float]]  # [frame_idx] = [x, y, z]


class UnifiedMotionPayload(BaseModel):
    schema_version: str = "1.0.0"
    source_model: str
    prompt: str
    seed: int
    fps: float
    total_frames: int
    duration_seconds: float
    timestamps: List[float]
    mode: str  # LIVE ARDY | BATCH ARDY | FIXTURE PREVIEW
    telemetry: GenerationTelemetry
    skeleton: SkeletonTrack
    vrm: VRMRotationTrack


class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # queued | loading_model | generating | decoding | retargeting | completed | failed | cancelled
    progress: float  # 0.0 to 1.0
    error: Optional[str] = None
    telemetry: Optional[GenerationTelemetry] = None
    result: Optional[UnifiedMotionPayload] = None
