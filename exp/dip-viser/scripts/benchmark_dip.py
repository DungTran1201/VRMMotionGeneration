"""
Automated Benchmarking Protocol for DiP Text-to-Motion.
Measures cold start latency, warm inference latency, RTF, generated FPS, and resource utilization.
Outputs raw JSON results and structured Markdown reports.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional
import numpy as np

# Add experiment root to sys.path
EXPERIMENT_ROOT = Path(__file__).resolve().parent.parent
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from app.config import (
    BENCHMARKS_DIR,
    CHECKPOINT_MODEL_PATH,
    DEFAULT_DURATION_SECONDS,
    DEFAULT_GUIDANCE_PARAM,
    SAMPLES_DIR,
)
from app.dip_adapter import DiPAdapter, JobStatus
from app.telemetry import TelemetryLogger, TelemetryRecord


def compute_file_sha256(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    if not path.exists():
        return "MISSING"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024 * 4):
            h.update(chunk)
    return h.hexdigest()


def get_gpu_info(device_idx: int = 0) -> Dict[str, Any]:
    """Retrieve GPU model and memory usage."""
    try:
        import torch
        if torch.cuda.is_available() and device_idx >= 0:
            name = torch.cuda.get_device_name(device_idx)
            props = torch.cuda.get_device_properties(device_idx)
            total_mb = props.total_memory / (1024 * 1024)
            allocated_mb = torch.cuda.memory_allocated(device_idx) / (1024 * 1024)
            return {
                "name": name,
                "total_mb": round(total_mb, 1),
                "allocated_mb": round(allocated_mb, 1),
                "cuda_version": torch.version.cuda or "N/A",
                "torch_version": torch.__version__,
            }
    except Exception:
        pass
    return {
        "name": "CPU/Generic",
        "total_mb": 0.0,
        "allocated_mb": 0.0,
        "cuda_version": "N/A",
        "torch_version": "N/A",
    }


def main():
    parser = argparse.ArgumentParser(description="Benchmark DiP Text-to-Motion Inference")
    parser.add_argument("--trials", type=int, default=3, help="Number of warm trials to run after cold trial")
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION_SECONDS, help="Motion length in seconds")
    parser.add_argument("--device", type=int, default=0, help="Device index (0 for GPU, -1 for CPU)")
    parser.add_argument("--prompt", type=str, default="A person walks forward and waves.", help="Benchmark prompt")
    args = parser.parse_args()

    print("=" * 65)
    print(" DiP Text-to-Motion Formal Benchmark Protocol")
    print("=" * 65)

    if not CHECKPOINT_MODEL_PATH.exists():
        print(f"FATAL: Checkpoint {CHECKPOINT_MODEL_PATH} not found.")
        sys.exit(1)

    print("Calculating checkpoint hash...")
    ckpt_hash = compute_file_sha256(CHECKPOINT_MODEL_PATH)
    print(f"Checkpoint: {CHECKPOINT_MODEL_PATH.name}")
    print(f"Size: {CHECKPOINT_MODEL_PATH.stat().st_size:,} bytes")
    print(f"SHA-256: {ckpt_hash}")

    gpu_info = get_gpu_info(args.device)
    print(f"Compute Device: {gpu_info['name']}")
    print(f"PyTorch Version: {gpu_info['torch_version']}")
    print(f"CUDA Version: {gpu_info['cuda_version']}\n")

    logger = TelemetryLogger(output_dir=BENCHMARKS_DIR)
    bench_samples_dir = SAMPLES_DIR / "benchmark_runs"
    adapter = DiPAdapter(samples_dir=bench_samples_dir)

    total_runs = 1 + args.trials  # 1 cold + N warm
    prompts_to_test = [
        ("A person walks forward and waves.", False),  # Cold
    ]
    for _ in range(args.trials):
        prompts_to_test.append((args.prompt, True))   # Warm

    print(f"Executing {total_runs} benchmark runs (1 Cold start + {args.trials} Warm runs)...")

    for i, (prompt, is_warm) in enumerate(prompts_to_test, 1):
        run_type = "WARM" if is_warm else "COLD START"
        print(f"\n--- Run {i}/{total_runs} [{run_type}] ---")
        print(f"Prompt: \"{prompt}\"")
        print(f"Requested Duration: {args.duration}s")

        job = adapter.submit_job(
            prompt=prompt,
            motion_length=args.duration,
            guidance_param=DEFAULT_GUIDANCE_PARAM,
            device=args.device,
        )

        while job.status in (JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.DECODING):
            time.sleep(0.4)

        if job.status == JobStatus.COMPLETED and job.telemetry:
            tel = job.telemetry
            tel.is_warm = is_warm
            tel.device_name = gpu_info["name"]
            tel.checkpoint_sha256 = ckpt_hash
            tel.pytorch_version = gpu_info["torch_version"]
            tel.cuda_version = gpu_info["cuda_version"]
            tel.gpu_vram_total_mb = gpu_info["total_mb"]
            tel.gpu_vram_used_mb = gpu_info["allocated_mb"]
            
            logger.log(tel)

            print(f"Result: SUCCESS")
            print(f"  - Inference Latency: {tel.inference_seconds:.3f} s")
            print(f"  - Decoded Frames: {tel.num_frames} frames ({tel.actual_duration_seconds:.2f} s @ {tel.motion_fps:.1f} FPS)")
            print(f"  - Generated FPS: {tel.generated_fps:.1f} frames/sec")
            print(f"  - Real-Time Factor (RTF): {tel.real_time_factor:.3f}x")
            print(f"  - Time to First Motion: {tel.time_to_first_motion_seconds:.3f} s")
        else:
            print(f"Result: FAILED - {job.error_message}")
            if job.telemetry:
                logger.log(job.telemetry)

    # Export results
    json_path = logger.save_json("benchmark_results.json")
    md_path = logger.save_markdown_summary("benchmark_summary.md")
    
    # Also write formal docs/benchmark-report.md
    docs_report = EXPERIMENT_ROOT / "docs" / "benchmark-report.md"
    with open(md_path, "r", encoding="utf-8") as f:
        docs_report.write_text(f.read(), encoding="utf-8")

    print("\n" + "=" * 65)
    print(" Benchmark Complete!")
    print(f" Raw JSON saved to: {json_path}")
    print(f" Markdown Summary saved to: {md_path}")
    print(f" Formal Report written to: {docs_report}")
    print("=" * 65)


if __name__ == "__main__":
    main()
