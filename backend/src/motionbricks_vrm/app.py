"""FastAPI Application for MotionBricks-to-VRM Integration Service.

Provides REST and WebSocket endpoints for schema inspection, motion validation,
retargeting, fixture access, and real inference execution.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError

from motionbricks_vrm.reconstruction.g1_skeleton import (
    G1SkeletonReconstructor,
    ReconstructedG1Frame,
)
from motionbricks_vrm.retargeting.retargeter import G1ToHumanoidRetargeter
from motionbricks_vrm.schemas.canonical_motion import (
    CanonicalHumanoidMotion,
    MotionSource,
)
from motionbricks_vrm.source_adapter.inference_adapter import (
    MotionBricksInferenceAdapter,
    inspect_motionbricks_checkpoints,
)
from motionbricks_vrm.streaming.session import StreamingSessionManager


adapter: Optional[MotionBricksInferenceAdapter] = None
session_manager = StreamingSessionManager()
fixture_cache: Optional[Dict[str, Any]] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global adapter, fixture_cache
    adapter = MotionBricksInferenceAdapter()
    fixture_path = Path(__file__).resolve().parent.parent.parent.parent / "fixtures" / "sample_motion.json"
    if fixture_path.exists():
        with open(fixture_path, "r", encoding="utf-8") as f:
            fixture_cache = json.load(f)
    yield
    # Cleanup on shutdown
    adapter = None
    fixture_cache = None


app = FastAPI(
    title="MotionBricks to VRM Integration Service",
    description="Transforms MotionBricks G1 motion into CanonicalHumanoidMotion/v1 for real-time VRM avatar rendering.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    mode_a_fixture_ready: bool
    mode_b_real_inference_ready: bool
    checkpoint_details: str
    environment: Dict[str, Any]


class ValidationRequest(BaseModel):
    motion: Dict[str, Any] = Field(..., description="Motion document to validate")


class ValidationResponse(BaseModel):
    valid: bool
    schema_version: Optional[str] = None
    frame_count: Optional[int] = None
    duration: Optional[float] = None
    errors: List[str] = Field(default_factory=list)


class RetargetRequest(BaseModel):
    raw_features: List[List[float]] = Field(
        ..., description="List of 414-dimensional decoded G1 feature vectors"
    )
    fps: float = Field(30.0, gt=0.0)
    profile_name: str = "g1_to_humanoid_standard"


class InferenceRequest(BaseModel):
    prompt: Optional[str] = None
    command: str = "walk"
    duration_seconds: float = Field(2.0, gt=0.0, le=10.0)


@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    ckpt_status = inspect_motionbricks_checkpoints()
    return HealthResponse(
        status="healthy",
        mode_a_fixture_ready=fixture_cache is not None,
        mode_b_real_inference_ready=ckpt_status.all_available,
        checkpoint_details=ckpt_status.detail_message,
        environment={
            "pose_ckpt_present": ckpt_status.pose_ckpt_present,
            "pose_ckpt_lfs": ckpt_status.pose_ckpt_is_lfs_pointer,
            "root_ckpt_present": ckpt_status.root_ckpt_present,
            "root_ckpt_lfs": ckpt_status.root_ckpt_is_lfs_pointer,
            "vqvae_ckpt_present": ckpt_status.vqvae_ckpt_present,
            "vqvae_ckpt_lfs": ckpt_status.vqvae_ckpt_is_lfs_pointer,
        },
    )


@app.get("/api/motion/schema")
async def get_motion_schema() -> Dict[str, Any]:
    """Return JSON Schema specification for CanonicalHumanoidMotion/v1."""
    return CanonicalHumanoidMotion.model_json_schema()


@app.get("/api/motion/fixture")
async def get_sample_fixture() -> Dict[str, Any]:
    """Return the pre-validated Mode A deterministic walking fixture."""
    if not fixture_cache:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample motion fixture not found on server",
        )
    return fixture_cache


@app.post("/api/motion/validate", response_model=ValidationResponse)
async def validate_motion_payload(req: ValidationRequest) -> ValidationResponse:
    """Validate any motion document against CanonicalHumanoidMotion/v1 rules."""
    try:
        motion = CanonicalHumanoidMotion.model_validate(req.motion)
        return ValidationResponse(
            valid=True,
            schema_version=motion.schema_,
            frame_count=motion.metadata.num_frames,
            duration=motion.metadata.duration,
            errors=[],
        )
    except ValidationError as ve:
        err_list = [f"[{' -> '.join(str(p) for p in e['loc'])}] {e['msg']}" for e in ve.errors()]
        return ValidationResponse(
            valid=False,
            errors=err_list,
        )
    except Exception as e:
        return ValidationResponse(
            valid=False,
            errors=[str(e)],
        )


@app.post("/api/motion/retarget", response_model=Dict[str, Any])
async def retarget_raw_motion(req: RetargetRequest) -> Dict[str, Any]:
    """Retarget raw 414-dim MotionBricks G1 features into CanonicalHumanoidMotion/v1."""
    reconstructor = G1SkeletonReconstructor()
    retargeter = G1ToHumanoidRetargeter(profile_name=req.profile_name)

    try:
        g1_frames = []
        import numpy as np
        for feat in req.raw_features:
            arr = np.array(feat, dtype=np.float64)
            g1_frames.append(reconstructor.reconstruct_from_feature_vector(arr))

        canonical = retargeter.retarget_sequence(
            g1_frames,
            fps=req.fps,
            source=MotionSource.MOTIONBRICKS,
            generator_info=f"POST /api/motion/retarget ({req.profile_name})"
        )
        return canonical.model_dump(by_alias=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Retargeting failed: {str(e)}",
        )


@app.post("/api/inference/generate")
async def generate_motion_inference(req: InferenceRequest) -> Dict[str, Any]:
    """Execute real MotionBricks inference when checkpoints and environment are present.
    
    Returns explicit error and instructions if checkpoints are unavailable.
    """
    ckpt_status = inspect_motionbricks_checkpoints()
    if not ckpt_status.all_available:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "Real MotionBricks inference unavailable",
                "reason": ckpt_status.detail_message,
                "suggested_action": "Fetch checkpoints via `git lfs pull --include=\"motionbricks/out/**\"` or use Mode A Fixture Demo.",
            },
        )

    # If checkpoints are available, execute genuine adapter initialization
    assert adapter is not None
    success, msg = adapter.initialize_real_inference()
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference initialization failed: {msg}",
        )

    # Run genuine inference
    motion = adapter.run_inference(
        command=req.command,
        duration_seconds=req.duration_seconds,
    )
    return motion.model_dump(by_alias=True)


@app.websocket("/ws/motion")
async def websocket_motion_stream(websocket: WebSocket):
    """WebSocket streaming endpoint for real-time frame streaming."""
    await session_manager.connect(websocket)
    try:
        while True:
            raw_msg = await websocket.receive_text()
            try:
                data = json.loads(raw_msg)
            except Exception:
                await websocket.send_text(json.dumps({"type": "error", "message": "Invalid JSON format"}))
                continue

            cmd = data.get("command")
            if cmd == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif cmd == "stream_fixture":
                if not fixture_cache:
                    await websocket.send_text(json.dumps({"type": "error", "message": "Fixture not loaded"}))
                    continue
                motion = CanonicalHumanoidMotion.model_validate(fixture_cache)
                loop = data.get("loop", False)
                speed = float(data.get("speed", 1.0))
                await session_manager.stream_motion(websocket, motion, loop=loop, speed=speed)
            else:
                await websocket.send_text(json.dumps({"type": "error", "message": f"Unknown command '{cmd}'"}))
    except WebSocketDisconnect:
        session_manager.disconnect(websocket)
    except Exception as e:
        session_manager.disconnect(websocket)
