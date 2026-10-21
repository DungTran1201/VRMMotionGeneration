"""
Batch generation script for DiP Text-to-Motion.
Processes a list of text prompts and exports decoded motion sequences with sidecars.
"""
import argparse
import json
from pathlib import Path
import sys
import time

# Add experiment root to sys.path
EXPERIMENT_ROOT = Path(__file__).resolve().parent.parent
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from app.config import (
    CHECKPOINT_MODEL_PATH,
    DEFAULT_DURATION_SECONDS,
    DEFAULT_GUIDANCE_PARAM,
    PROMPTS_FILE,
    SAMPLES_DIR,
)
from app.dip_adapter import DiPAdapter, JobStatus


def main():
    parser = argparse.ArgumentParser(description="Run DiP Text-to-Motion Batch Generation")
    parser.add_argument("--prompts_file", type=Path, default=PROMPTS_FILE, help="Path to prompts JSON")
    parser.add_argument("--prompt", type=str, default=None, help="Single prompt to generate")
    parser.add_argument("--output_dir", type=Path, default=SAMPLES_DIR, help="Directory to save outputs")
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION_SECONDS, help="Motion length in seconds")
    parser.add_argument("--guidance", type=float, default=DEFAULT_GUIDANCE_PARAM, help="Guidance scale")
    parser.add_argument("--device", type=int, default=0, help="CUDA device index or -1 for CPU")
    args = parser.parse_args()

    prompts = []
    if args.prompt:
        prompts.append({"id": "cli_prompt", "text": args.prompt, "duration": args.duration})
    elif args.prompts_file.exists():
        with open(args.prompts_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for p in data.get("prompts", []):
                prompts.append({
                    "id": p.get("id", "p"),
                    "text": p.get("text", ""),
                    "duration": p.get("default_duration", args.duration),
                })
    else:
        prompts = [
            {"id": "p1", "text": "A person walks forward and waves.", "duration": 4.0},
            {"id": "p2", "text": "A person runs forward and jumps.", "duration": 4.0},
        ]

    print("=" * 60)
    print(" DiP Text-to-Motion Batch Generation")
    print("=" * 60)
    print(f"Total Prompts: {len(prompts)}")
    print(f"Device: {'cuda:' + str(args.device) if args.device >= 0 else 'cpu'}")
    print(f"Output Directory: {args.output_dir}\n")

    adapter = DiPAdapter(samples_dir=args.output_dir)
    if not adapter.is_checkpoint_available():
        print(f"ERROR: Checkpoint not available at {CHECKPOINT_MODEL_PATH}")
        sys.exit(1)

    for i, p_item in enumerate(prompts, 1):
        text = p_item["text"]
        dur = p_item.get("duration", args.duration)
        print(f"[{i}/{len(prompts)}] Generating: \"{text}\" ({dur}s)...")
        
        job = adapter.submit_job(
            prompt=text,
            motion_length=dur,
            guidance_param=args.guidance,
            device=args.device,
        )

        while job.status in (JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.DECODING):
            time.sleep(0.5)

        if job.status == JobStatus.COMPLETED and job.motion_clip:
            print(f"  -> SUCCESS: {job.motion_clip.num_frames} frames generated in {job.telemetry.inference_seconds:.2f}s (RTF: {job.telemetry.real_time_factor:.2f}x)")
            print(f"  -> Saved to: {job.output_dir}\n")
        else:
            print(f"  -> FAILED: {job.error_message}\n")


if __name__ == "__main__":
    main()
