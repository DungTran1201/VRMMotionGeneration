"""ARDY Model Runtime Engine.

Manages model lifecycle on GPU, provides decoupled text conditioning, executes
diffusion generation passes, and extracts high-resolution performance telemetry.
"""

import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

import numpy as np
import torch

from ..motion_adapter.vrm_retargeter import create_unified_motion_payload
from ..schemas import GenerationTelemetry, UnifiedMotionPayload


class ArdyEngine:
    """Singleton model runner maintaining ARDY model state and truthful readiness."""

    _instance: Optional["ArdyEngine"] = None

    def __init__(self, checkpoints_dir: Optional[str] = None, device: Optional[str] = None):
        self.repo_root = Path(__file__).resolve().parents[4]  # exp/ardy-vrm-demo
        self.vendor_path = self.repo_root / "vendor" / "ardy"
        if str(self.vendor_path) not in sys.path:
            sys.path.insert(0, str(self.vendor_path))

        self.device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
        self.checkpoints_dir = (
            Path(checkpoints_dir) if checkpoints_dir else (self.repo_root / "checkpoints")
        ).resolve()
        self.model_name = "ARDY-Core-RP-20FPS-Horizon8"
        self.model = None
        self.text_encoder = None
        self.model_load_time_seconds: Optional[float] = None
        self.text_encoder_ready: bool = False
        self.blocking_reason: Optional[str] = None

        # Probe readiness immediately
        self.probe_text_encoder()

    @classmethod
    def get_instance(cls, checkpoints_dir: Optional[str] = None, device: Optional[str] = None) -> "ArdyEngine":
        if cls._instance is None:
            cls._instance = cls(checkpoints_dir=checkpoints_dir, device=device)
        return cls._instance

    def is_checkpoint_ready(self) -> bool:
        """Verify that all required checkpoint files are present."""
        model_path = self.checkpoints_dir / self.model_name
        if not model_path.exists():
            return False
        has_config = (model_path / "config.yaml").exists()
        has_denoiser = (model_path / "denoiser.safetensors").exists()
        has_tokenizer = (model_path / "tokenizer.safetensors").exists()
        return has_config and has_denoiser and has_tokenizer

    def probe_text_encoder(self) -> bool:
        """Probe availability of genuine ARDY text encoder (remote service or local LLM2Vec)."""
        try:
            from ardy.model.load_model import load_text_encoder
            enc = load_text_encoder(mode="auto")
            self.text_encoder = enc
            self.text_encoder_ready = True
            self.blocking_reason = None
            return True
        except Exception as e:
            self.text_encoder = None
            self.text_encoder_ready = False
            self.blocking_reason = (
                f"Official ARDY semantic text encoder unavailable ({type(e).__name__}): {e}. "
                "Requires access to gated model meta-llama/Meta-Llama-3-8B-Instruct or running TEXT_ENCODER_URL service."
            )
            return False

    @property
    def inference_ready(self) -> bool:
        """Inference is ready only if both complete checkpoint and genuine text encoder are ready."""
        return self.is_checkpoint_ready() and self.text_encoder_ready

    @property
    def mode(self) -> str:
        """Computed truthful operational mode."""
        if self.inference_ready:
            return "LIVE ARDY"
        elif self.is_checkpoint_ready():
            return "MODEL UNAVAILABLE"
        return "MODEL UNAVAILABLE"

    def load_model(self) -> float:
        """Load the ARDY model into memory using genuine text encoder."""
        if self.model is not None:
            return self.model_load_time_seconds or 0.0

        if not self.is_checkpoint_ready():
            raise FileNotFoundError(f"Checkpoint incomplete or missing at: {self.checkpoints_dir / self.model_name}")

        if not self.text_encoder_ready or self.text_encoder is None:
            raise RuntimeError(
                f"Cannot load ARDY for live inference without genuine semantic text encoder: {self.blocking_reason}"
            )

        t0 = time.monotonic()
        from ardy.model import load_model

        model_path = self.checkpoints_dir / self.model_name
        self.model = load_model(
            str(model_path),
            device=self.device,
            checkpoints_dir=str(self.checkpoints_dir),
            text_encoder=self.text_encoder,
        )
        self.model_load_time_seconds = round(time.monotonic() - t0, 3)
        return self.model_load_time_seconds

    def generate(
        self,
        prompt: str,
        duration_seconds: float = 3.0,
        seed: Optional[int] = None,
    ) -> UnifiedMotionPayload:
        """Generate full-body motion sequence for given prompt and duration."""
        if not self.inference_ready:
            raise RuntimeError(
                f"Live ARDY generation unavailable: {self.blocking_reason} "
                "Fake or hash-seeded embeddings are strictly disallowed in live mode."
            )

        t_start_e2e = time.monotonic()
        seed_val = seed if seed is not None else int(time.time() * 1000) % 1_000_000

        # Set seeds
        torch.manual_seed(seed_val)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed_val)
            try:
                torch.cuda.reset_peak_memory_stats(self.device)
            except Exception:
                pass

        # Ensure model is warm
        load_time = self.load_model()

        fps = float(self.model.motion_rep.fps)
        num_frames = int(duration_seconds * fps)
        diffusion_steps = int(self.model.diffusion.num_base_steps)
        patch = self.model.num_frames_per_token
        history_frames = max(patch, (self.model.gen_horizon_len // patch) * patch)

        pad_mask = torch.ones(1, num_frames, device=self.device, dtype=torch.bool)
        first_heading_angle = torch.zeros(1, device=self.device)

        # Monotonic timing for generation pass
        t_gen_start = time.monotonic()
        with torch.no_grad():
            motion = self.model(
                [prompt],
                num_frames,
                num_denoising_steps=diffusion_steps,
                pad_mask=pad_mask,
                first_heading_angle=first_heading_angle,
                motion_mask=None,
                observed_motion=None,
                cfg_weight=2.0,
                crop_history_length=history_frames,
            )
            output = self.model.motion_rep.inverse(motion, is_normalized=True)
        t_gen_end = time.monotonic()

        gen_time = t_gen_end - t_gen_start
        effective_fps = round(num_frames / max(gen_time, 0.001), 2)
        rtf = round(gen_time / max(duration_seconds, 0.001), 3)

        # Peak VRAM
        peak_vram = None
        if torch.cuda.is_available():
            try:
                peak_vram = round(torch.cuda.max_memory_allocated(self.device) / (1024**2), 2)
            except Exception:
                pass

        # Extract numpy tensors
        local_rot_mats = output["local_rot_mats"]
        root_positions = output["root_positions"]
        posed_joints = output.get("posed_joints")
        global_rot_mats = output.get("global_rot_mats")

        if isinstance(local_rot_mats, torch.Tensor):
            local_rot_mats = local_rot_mats.detach().cpu().numpy()
        if isinstance(root_positions, torch.Tensor):
            root_positions = root_positions.detach().cpu().numpy()
        if isinstance(posed_joints, torch.Tensor):
            posed_joints = posed_joints.detach().cpu().numpy()
        if isinstance(global_rot_mats, torch.Tensor):
            global_rot_mats = global_rot_mats.detach().cpu().numpy()

        # Retargeting pass timing
        t_retarget_start = time.monotonic()
        telemetry_preliminary = GenerationTelemetry(
            model_name=self.model_name,
            device=self.device,
            prompt=prompt,
            seed=seed_val,
            requested_duration=duration_seconds,
            actual_duration=round(num_frames / fps, 3),
            total_frames=num_frames,
            fps=fps,
            model_load_time_seconds=load_time,
            generation_time_seconds=round(gen_time, 3),
            effective_generated_fps=effective_fps,
            real_time_factor=rtf,
            retarget_time_ms=0.0,
            end_to_end_latency_ms=0.0,
            peak_vram_mb=peak_vram,
        )

        payload = create_unified_motion_payload(
            local_rot_mats=local_rot_mats,
            root_positions=root_positions,
            fps=fps,
            prompt=prompt,
            seed=seed_val,
            source_model=self.model_name,
            telemetry=telemetry_preliminary,
            mode=self.mode,
            posed_joints=posed_joints,
            global_rot_mats=global_rot_mats,
        )

        t_retarget_end = time.monotonic()
        retarget_ms = round((t_retarget_end - t_retarget_start) * 1000, 2)
        total_latency_ms = round((time.monotonic() - t_start_e2e) * 1000, 2)

        # Finalize telemetry
        payload.telemetry.retarget_time_ms = retarget_ms
        payload.telemetry.end_to_end_latency_ms = total_latency_ms

        return payload
