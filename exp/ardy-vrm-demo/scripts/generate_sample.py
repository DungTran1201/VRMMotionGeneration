#!/usr/bin/env python3
"""
generate_sample.py — CLI motion generator for ARDY Core model.
Generates genuine autoregressive diffusion motion, retargets to VRM,
and writes structured payload to disk.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add backend package to path
repo_root = Path(__file__).resolve().parent.parent
backend_src = repo_root / "backend" / "src"
if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

from ardy_vrm_demo.ardy_runtime.model_engine import ArdyEngine


def main():
    parser = argparse.ArgumentParser(description="Generate ARDY motion and retarget to VRM.")
    parser.add_argument("--prompt", default="A person walks forward.", help="Text conditioning prompt")
    parser.add_argument("--duration", type=float, default=3.0, help="Duration in seconds (default: 3.0)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", default="artifacts/sample-motion/generated_sample.vrm.json", help="Output path")
    args = parser.parse_args()

    engine = ArdyEngine.get_instance()
    print(f"Executing generation for prompt: '{args.prompt}' (duration: {args.duration}s, seed: {args.seed})...")

    payload = engine.generate(
        prompt=args.prompt,
        duration_seconds=args.duration,
        seed=args.seed,
    )

    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = repo_root / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(payload.model_dump_json(indent=2))

    t = payload.telemetry
    print(f"\nGeneration complete!")
    print(f"Output saved to: {out_path} ({os.path.getsize(out_path)} bytes)")
    print(f"Frames: {payload.total_frames} @ {payload.fps} FPS ({payload.duration_seconds}s)")
    print(f"Generation Time: {t.generation_time_seconds:.3f}s")
    print(f"Throughput: {t.effective_generated_fps:.2f} FPS")
    print(f"Real-Time Factor (RTF): {t.real_time_factor:.3f} (RTF < 1 means faster than real-time)")
    print(f"Retargeting Time: {t.retarget_time_ms:.2f} ms")
    print(f"Total Latency: {t.end_to_end_latency_ms:.2f} ms")
    if t.peak_vram_mb:
        print(f"Peak VRAM: {t.peak_vram_mb:.1f} MB")


if __name__ == "__main__":
    main()
