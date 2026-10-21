"""
Telemetry and Benchmarking Utilities for DiP-Viser Experiment.
Measures and records inference latency, generated FPS, RTF, memory, and playback metrics.
"""
from dataclasses import asdict, dataclass, field
import datetime
import json
from pathlib import Path
import platform
import time
from typing import Any, Dict, List, Optional
import numpy as np


@dataclass
class TelemetryRecord:
    timestamp_utc: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    prompt: str = ""
    seed: Optional[int] = None
    device: str = "cpu"
    device_name: str = "Unknown"
    checkpoint_name: str = ""
    checkpoint_sha256: str = ""
    
    # Timing (seconds)
    load_time_seconds: float = 0.0
    inference_seconds: float = 0.0
    decode_seconds: float = 0.0
    total_latency_seconds: float = 0.0
    time_to_first_motion_seconds: float = 0.0
    
    # Motion characteristics
    requested_duration_seconds: float = 0.0
    actual_duration_seconds: float = 0.0
    num_frames: int = 0
    motion_fps: float = 20.0
    
    # Derived Performance Metrics
    generated_fps: float = 0.0       # num_frames / inference_seconds
    real_time_factor: float = 0.0    # inference_seconds / actual_duration_seconds
    
    # System / Hardware utilization
    gpu_vram_used_mb: float = 0.0
    gpu_vram_total_mb: float = 0.0
    ram_used_mb: float = 0.0
    ram_total_mb: float = 0.0
    
    # Environment info
    os_version: str = field(default_factory=platform.platform)
    python_version: str = field(default_factory=platform.python_version)
    pytorch_version: str = ""
    cuda_version: str = ""
    
    is_warm: bool = False
    status: str = "SUCCESS"  # SUCCESS, FAILED, TIMEOUT
    error_message: Optional[str] = None
    
    def calculate_derived_metrics(self) -> None:
        if self.inference_seconds > 0.0:
            self.generated_fps = round(float(self.num_frames) / self.inference_seconds, 2)
            if self.actual_duration_seconds > 0.0:
                self.real_time_factor = round(self.inference_seconds / self.actual_duration_seconds, 3)
            else:
                self.real_time_factor = 0.0
        self.total_latency_seconds = round(self.load_time_seconds + self.inference_seconds + self.decode_seconds, 3)
        self.time_to_first_motion_seconds = self.total_latency_seconds

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TelemetryLogger:
    """Manages collection and serialization of telemetry records."""
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (Path(__file__).resolve().parent.parent / "artifacts" / "benchmarks")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.records: List[TelemetryRecord] = []

    def log(self, record: TelemetryRecord) -> None:
        record.calculate_derived_metrics()
        self.records.append(record)

    def save_json(self, filename: str = "benchmark_results.json") -> Path:
        out_file = self.output_dir / filename
        data = [r.to_dict() for r in self.records]
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return out_file

    def save_markdown_summary(self, filename: str = "benchmark_summary.md") -> Path:
        out_file = self.output_dir / filename
        if not self.records:
            out_file.write_text("# DiP Benchmark Summary\n\nNo records logged.\n", encoding="utf-8")
            return out_file

        successful = [r for r in self.records if r.status == "SUCCESS"]
        inf_times = [r.inference_seconds for r in successful]
        rtf_vals = [r.real_time_factor for r in successful]
        gfps_vals = [r.generated_fps for r in successful]

        content = [
            "# DiP Text-to-Motion Benchmark Summary",
            "",
            f"- **Total Runs**: {len(self.records)}",
            f"- **Successful Runs**: {len(successful)}",
            f"- **Device**: {self.records[0].device_name} ({self.records[0].device})",
            f"- **Checkpoint**: `{self.records[0].checkpoint_name}`",
            "",
            "## Summary Metrics",
            "",
            "| Metric | Min | Median | Max |",
            "|---|---|---|---|",
            f"| Inference Latency (s) | {min(inf_times):.3f} | {float(np.median(inf_times)):.3f} | {max(inf_times):.3f} |",
            f"| Real-Time Factor (RTF) | {min(rtf_vals):.3f} | {float(np.median(rtf_vals)):.3f} | {max(rtf_vals):.3f} |",
            f"| Generated Motion FPS | {min(gfps_vals):.1f} | {float(np.median(gfps_vals)):.1f} | {max(gfps_vals):.1f} |",
            "",
            "> **Note on Real-Time**: RTF < 1.0 means generation is faster than playback duration.",
            "",
            "## Trial Details",
            "",
            "| # | Prompt | Warm | Latency (s) | RTF | Gen FPS | VRAM (MB) |",
            "|---|---|---|---|---|---|---|",
        ]

        for i, r in enumerate(self.records, 1):
            warm_str = "Yes" if r.is_warm else "No (Cold)"
            content.append(
                f"| {i} | \"{r.prompt}\" | {warm_str} | {r.inference_seconds:.3f} | {r.real_time_factor:.3f} | {r.generated_fps:.1f} | {r.gpu_vram_used_mb:.1f} |"
            )

        content.append("")
        out_file.write_text("\n".join(content), encoding="utf-8")
        return out_file
