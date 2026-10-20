#!/usr/bin/env python3
"""Quick smoke test for ARDY model loading and generation."""

import sys
import time
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
vendor_path = repo_root / "vendor" / "ardy"
sys.path.insert(0, str(vendor_path))

import torch
from ardy.model import load_model


class DecoupledTextEncoder(torch.nn.Module):
    def __init__(self, dim: int = 4096, device: str = "cuda:0"):
        super().__init__()
        self.dim = dim
        self.device = device

    def __call__(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        L = len(texts[0].split())
        t = torch.randn(len(texts), L, self.dim, device=self.device)
        t = t / torch.norm(t, dim=-1, keepdim=True)
        return t, [L]


def main():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    ckpt_dir = repo_root / "checkpoints"
    model_path = ckpt_dir / "ARDY-Core-RP-20FPS-Horizon8"
    te = DecoupledTextEncoder(device=device)

    t0 = time.time()
    print(f"Loading ARDY model on {device}...")
    model = load_model(str(model_path), device=device, checkpoints_dir=str(ckpt_dir), text_encoder=te)
    t_load = time.time() - t0
    print(f"Model loaded in {t_load:.2f}s! Native FPS: {model.motion_rep.fps}")

    fps = model.motion_rep.fps
    num_frames = 40
    diffusion_steps = int(model.diffusion.num_base_steps)
    patch = model.num_frames_per_token
    history_frames = max(patch, (model.gen_horizon_len // patch) * patch)

    pad_mask = torch.ones(1, num_frames, device=device, dtype=torch.bool)
    first_heading_angle = torch.zeros(1, device=device)

    print("Generating 40 frames on GPU...")
    t_gen0 = time.time()
    with torch.no_grad():
        motion = model(
            ["A person walks forward."],
            num_frames,
            num_denoising_steps=diffusion_steps,
            pad_mask=pad_mask,
            first_heading_angle=first_heading_angle,
            motion_mask=None,
            observed_motion=None,
            cfg_weight=2.0,
            crop_history_length=history_frames,
        )
        output = model.motion_rep.inverse(motion, is_normalized=True)
    t_gen = time.time() - t_gen0
    print(f"Generation completed in {t_gen:.2f}s! (Throughput: {num_frames / t_gen:.2f} FPS)")
    print(f"Output keys: {list(output.keys())}")
    print(f"posed_joints shape: {output['posed_joints'].shape}")
    print(f"local_rot_mats shape: {output['local_rot_mats'].shape}")
    print(f"Peak VRAM: {torch.cuda.max_memory_allocated(0) / (1024**2):.2f} MB")


if __name__ == "__main__":
    main()
