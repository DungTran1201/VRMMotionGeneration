"""FastAPI application for ARDY VRM Demo."""

import asyncio
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .ardy_runtime.model_engine import ArdyEngine
from .jobs.job_manager import JobManager
from .schemas import (
    GenerationRequest,
    HealthResponse,
    JobStatusResponse,
    ModelInfo,
    ModelsResponse,
    UnifiedMotionPayload,
)

app = FastAPI(
    title="ARDY to VRM Motion Lab API",
    description="Backend API and streaming engine for ARDY Text-to-Motion-to-VRM demonstration.",
    version="1.0.0",
)

# CORS middleware for local web viewing
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine & job manager
engine = ArdyEngine.get_instance()
job_manager = JobManager(engine)

REPO_ROOT = Path(__file__).resolve().parents[3]  # exp/ardy-vrm-demo
FRONTEND_DIR = REPO_ROOT / "frontend"
SAMPLE_DIR = REPO_ROOT / "artifacts" / "sample-motion"


@app.get("/api/health", response_model=HealthResponse)
def get_health():
    import torch

    gpu_name = None
    vram_free = None
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        # Query free VRAM
        try:
            free_bytes, total_bytes = torch.cuda.mem_get_info(0)
            vram_free = round(free_bytes / (1024**2), 1)
        except Exception:
            pass

    ckpt_ready = engine.is_checkpoint_ready()

    return HealthResponse(
        status="ok",
        server_ready=True,
        mode=engine.mode,
        device=engine.device,
        torch_version=torch.__version__,
        cuda_available=torch.cuda.is_available(),
        gpu_name=gpu_name,
        vram_free_mb=vram_free,
        checkpoint_ready=ckpt_ready,
        model_loaded=engine.model is not None,
        text_encoder_ready=engine.text_encoder_ready,
        inference_ready=engine.inference_ready,
        blocking_reason=engine.blocking_reason,
        model_name=engine.model_name,
        active_jobs=job_manager.active_job_count,
    )


@app.get("/api/models", response_model=ModelsResponse)
def get_models():
    ckpt_ready = engine.is_checkpoint_ready()
    return ModelsResponse(
        models=[
            ModelInfo(
                alias="core8",
                full_name="ARDY-Core-RP-20FPS-Horizon8",
                skeleton="CoreSkeleton27",
                fps=20.0,
                horizon=8,
                available=ckpt_ready,
                description="Official NVIDIA ARDY Core model, 20 FPS, 8-frame autoregressive horizon.",
            ),
            ModelInfo(
                alias="core40",
                full_name="ARDY-Core-RP-20FPS-Horizon40",
                skeleton="CoreSkeleton27",
                fps=20.0,
                horizon=40,
                available=False,
                description="Longer horizon (40 frames), requires 20 FPS Core40 checkpoint.",
            ),
        ]
    )


@app.post("/api/generations")
async def create_generation(req: GenerationRequest):
    if not engine.inference_ready:
        raise HTTPException(
            status_code=503,
            detail=f"MODEL UNAVAILABLE: {engine.blocking_reason}",
        )

    if job_manager.active_job_count >= 1:
        raise HTTPException(status_code=429, detail="A generation job is already running on the GPU.")

    job_id = job_manager.create_job(
        prompt=req.prompt,
        duration_seconds=req.duration_seconds,
        seed=req.seed,
    )
    return {"job_id": job_id, "status": "queued"}


@app.get("/api/generations/{job_id}", response_model=JobStatusResponse)
def get_generation_status(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    return job


@app.post("/api/generations/{job_id}/cancel")
def cancel_generation(job_id: str):
    success = job_manager.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel job (not found or already completed/cancelled).")
    return {"job_id": job_id, "status": "cancelled"}


@app.get("/api/samples/default")
def get_default_sample():
    sample_file = SAMPLE_DIR / "waves.vrm.json"
    if not sample_file.exists():
        sample_file = SAMPLE_DIR / "sample_00.vrm.json"
    if not sample_file.exists():
        raise HTTPException(status_code=404, detail="Default sample motion not found.")
    with open(sample_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@app.websocket("/api/generations/{job_id}/events")
async def generation_events_ws(websocket: WebSocket, job_id: str):
    await websocket.accept()
    queue = job_manager.subscribe(job_id)
    try:
        current_job = job_manager.get_job(job_id)
        if current_job:
            await websocket.send_text(current_job.model_dump_json())

        while True:
            data = await queue.get()
            await websocket.send_text(json.dumps(data))
            if data.get("status") in ("completed", "failed", "cancelled"):
                break
    except WebSocketDisconnect:
        pass
    finally:
        job_manager.unsubscribe(job_id, queue)


# Mount static frontend directory if present
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "ARDY VRM Demo API active. Frontend index.html not yet built."}
