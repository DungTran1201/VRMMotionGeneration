#!/usr/bin/env python3
"""
benchmark_generation.py — Automated performance benchmarking suite for ARDY to VRM pipeline.
Runs cold start + 5 warm passes, measures timings using monotonic clock,
and outputs structured JSON metrics to artifacts/benchmark/results.json.
"""

import json
import os
import sys
import time
from pathlib import Path

# Add backend package to path
repo_root = Path(__file__).resolve().parent.parent
backend_src = repo_root / "backend" / "src"
if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

import numpy as np
from ardy_vrm_demo.ardy_runtime.model_engine import ArdyEngine


def run_benchmark(num_warm_runs: int = 5, duration: float = 3.0) -> dict:
    engine = ArdyEngine.get_instance()
    prompt = "A person walks forward."

    runs = []

    # 1. Cold start run
    print("=== Executing Cold Start Pass ===")
    t_cold_start = time.monotonic()
    cold_payload = engine.generate(prompt=prompt, duration_seconds=duration, seed=42)
    t_cold_total = time.monotonic() - t_cold_start
    cold_telemetry = cold_payload.telemetry.model_dump()
    cold_telemetry["is_cold_start"] = True
    runs.append(cold_telemetry)
    print(f"Cold start complete in {t_cold_total:.2f}s (Generation: {cold_payload.telemetry.generation_time_seconds:.3f}s)")

    # 2. Warm runs
    print(f"\n=== Executing {num_warm_runs} Warm Benchmark Passes ===")
    warm_gen_times = []
    warm_throughputs = []
    warm_rtfs = []
    warm_retarget_times = []

    for i in range(num_warm_runs):
        seed = 1000 + i
        t_start = time.monotonic()
        payload = engine.generate(prompt=prompt, duration_seconds=duration, seed=seed)
        t_total = time.monotonic() - t_start

        telem = payload.telemetry.model_dump()
        telem["is_cold_start"] = False
        telem["run_index"] = i + 1
        runs.append(telem)

        warm_gen_times.append(telem["generation_time_seconds"])
        warm_throughputs.append(telem["effective_generated_fps"])
        warm_rtfs.append(telem["real_time_factor"])
        warm_retarget_times.append(telem["retarget_time_ms"])

        print(
            f"Run {i+1}/{num_warm_runs}: Gen={telem['generation_time_seconds']:.3f}s, "
            f"Throughput={telem['effective_generated_fps']:.2f} FPS, RTF={telem['real_time_factor']:.3f}, "
            f"Retarget={telem['retarget_time_ms']:.2f}ms"
        )

    # Compute statistics
    summary = {
        "model_name": engine.model_name,
        "device": engine.device,
        "native_fps": 20.0,
        "requested_duration_seconds": duration,
        "generated_frames_per_run": int(duration * 20.0),
        "num_warm_runs": num_warm_runs,
        "cold_start": {
            "model_load_time_seconds": cold_payload.telemetry.model_load_time_seconds,
            "generation_time_seconds": cold_payload.telemetry.generation_time_seconds,
            "total_latency_seconds": round(t_cold_total, 3),
        },
        "warm_metrics": {
            "generation_time_seconds": {
                "median": round(float(np.median(warm_gen_times)), 3),
                "min": round(float(np.min(warm_gen_times)), 3),
                "max": round(float(np.max(warm_gen_times)), 3),
                "mean": round(float(np.mean(warm_gen_times)), 3),
            },
            "throughput_fps": {
                "median": round(float(np.median(warm_throughputs)), 2),
                "min": round(float(np.min(warm_throughputs)), 2),
                "max": round(float(np.max(warm_throughputs)), 2),
                "mean": round(float(np.mean(warm_throughputs)), 2),
            },
            "real_time_factor_rtf": {
                "median": round(float(np.median(warm_rtfs)), 3),
                "min": round(float(np.min(warm_rtfs)), 3),
                "max": round(float(np.max(warm_rtfs)), 3),
                "mean": round(float(np.mean(warm_rtfs)), 3),
            },
            "retargeting_time_ms": {
                "median": round(float(np.median(warm_retarget_times)), 2),
                "min": round(float(np.min(warm_retarget_times)), 2),
                "max": round(float(np.max(warm_retarget_times)), 2),
                "mean": round(float(np.mean(warm_retarget_times)), 2),
            },
            "peak_vram_mb": cold_payload.telemetry.peak_vram_mb,
        },
        "runs": runs,
    }

    out_file = repo_root / "artifacts" / "benchmark" / "results.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n=== Benchmark Summary Saved to {out_file} ===")
    print(f"Median Generation Time: {summary['warm_metrics']['generation_time_seconds']['median']}s")
    print(f"Median Throughput: {summary['warm_metrics']['throughput_fps']['median']} FPS")
    print(f"Median RTF: {summary['warm_metrics']['real_time_factor_rtf']['median']} (<1 means faster than real-time)")
    print(f"Median Retargeting Time: {summary['warm_metrics']['retargeting_time_ms']['median']} ms")
    return summary


def main():
    run_benchmark(num_warm_runs=5, duration=3.0)


if __name__ == "__main__":
    main()
