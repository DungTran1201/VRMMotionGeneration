"""
DiP Model Execution Adapter for DiP-Viser Experiment.
Manages isolated execution of upstream DiP text-to-motion generation,
capturing logs, job states, telemetry, and decoding results.
"""
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from typing import Any, Callable, Dict, List, Optional
import uuid

from .config import (
    CHECKPOINT_MODEL_PATH,
    DEFAULT_DURATION_SECONDS,
    DEFAULT_GUIDANCE_PARAM,
    EXPERIMENT_DIR,
    SAMPLES_DIR,
    UPSTREAM_DIR,
)
from .motion_decoder import decode_results_npy
from .motion_schema import MotionClip
from .telemetry import TelemetryRecord


class JobStatus(str, Enum):
    IDLE = "IDLE"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    DECODING = "DECODING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class GenerationJob:
    job_id: str
    prompt: str
    motion_length: float
    guidance_param: float
    seed: Optional[int]
    device: int
    status: JobStatus = JobStatus.QUEUED
    error_message: Optional[str] = None
    output_dir: Optional[Path] = None
    motion_clip: Optional[MotionClip] = None
    telemetry: Optional[TelemetryRecord] = None
    log_content: str = ""
    start_time: float = 0.0
    end_time: float = 0.0


class DiPAdapter:
    """
    Subprocess-isolated adapter for official DiP text-to-motion generation.
    Protects Viser server memory and CUDA context while providing asynchronous progress.
    """
    def __init__(
        self,
        checkpoint_path: Optional[Path] = None,
        python_exe: Optional[Path] = None,
        upstream_dir: Optional[Path] = None,
        samples_dir: Optional[Path] = None,
    ):
        self.checkpoint_path = checkpoint_path or CHECKPOINT_MODEL_PATH
        self.python_exe = python_exe or (EXPERIMENT_DIR / ".venv" / "Scripts" / "python.exe")
        self.upstream_dir = upstream_dir or UPSTREAM_DIR
        self.samples_dir = samples_dir or SAMPLES_DIR
        self.samples_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_job: Optional[GenerationJob] = None
        self._lock = threading.Lock()
        self._active_process: Optional[subprocess.Popen] = None

    def is_checkpoint_available(self) -> bool:
        return self.checkpoint_path.exists() and self.checkpoint_path.stat().st_size > 100_000_000

    def submit_job(
        self,
        prompt: str,
        motion_length: float = DEFAULT_DURATION_SECONDS,
        guidance_param: float = DEFAULT_GUIDANCE_PARAM,
        seed: Optional[int] = None,
        device: int = 0,
        on_complete: Optional[Callable[[GenerationJob], None]] = None,
    ) -> GenerationJob:
        """Submit a new generation request in background thread."""
        with self._lock:
            job_id = f"job_{int(time.time())}_{uuid.uuid4().hex[:6]}"
            job = GenerationJob(
                job_id=job_id,
                prompt=prompt.strip(),
                motion_length=float(motion_length),
                guidance_param=float(guidance_param),
                seed=seed,
                device=device,
                output_dir=self.samples_dir / job_id,
            )
            self.current_job = job

        thread = threading.Thread(
            target=self._run_job,
            args=(job, on_complete),
            daemon=True,
            name=f"dip-worker-{job_id}",
        )
        thread.start()
        return job

    def cancel_current_job(self) -> None:
        """Cancel the actively running job if any."""
        with self._lock:
            if self._active_process and self._active_process.poll() is None:
                try:
                    self._active_process.terminate()
                except Exception:
                    pass
            if self.current_job and self.current_job.status in (JobStatus.QUEUED, JobStatus.RUNNING):
                self.current_job.status = JobStatus.CANCELLED
                self.current_job.error_message = "Cancelled by user"

    def _run_job(self, job: GenerationJob, on_complete: Optional[Callable[[GenerationJob], None]]) -> None:
        job.start_time = time.time()
        job.status = JobStatus.RUNNING
        
        telemetry = TelemetryRecord(
            prompt=job.prompt,
            seed=job.seed,
            device=f"cuda:{job.device}" if job.device >= 0 else "cpu",
            checkpoint_name=self.checkpoint_path.name,
            requested_duration_seconds=job.motion_length,
        )

        try:
            if not self.is_checkpoint_available():
                raise FileNotFoundError(
                    f"DiP checkpoint not found at {self.checkpoint_path}. Please download official weights."
                )

            job.output_dir.mkdir(parents=True, exist_ok=True)
            log_file = job.output_dir / "generation.log"

            # Construct safe typed CLI arguments
            cmd: List[str] = [
                str(self.python_exe),
                "-m",
                "sample.generate",
                "--model_path",
                str(self.checkpoint_path),
                "--output_dir",
                str(job.output_dir),
                "--text_prompt",
                job.prompt,
                "--motion_length",
                str(job.motion_length),
                "--guidance_param",
                str(job.guidance_param),
                "--num_samples",
                "1",
                "--num_repetitions",
                "1",
                "--autoregressive",
                "--device",
                str(job.device),
            ]
            if job.seed is not None:
                cmd.extend(["--seed", str(job.seed)])

            inf_start = time.time()
            process = subprocess.Popen(
                cmd,
                cwd=str(self.upstream_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            with self._lock:
                self._active_process = process

            captured_output = []
            for line in process.stdout:
                captured_output.append(line)
                job.log_content = "".join(captured_output[-50:])

            exit_code = process.wait()
            inf_end = time.time()
            telemetry.inference_seconds = round(inf_end - inf_start, 3)

            # Write full log after process finishes to avoid file-locking on Windows
            try:
                with open(log_file, "w", encoding="utf-8") as lf:
                    lf.write(f"Command: {' '.join(cmd)}\n\n")
                    lf.writelines(captured_output)
            except Exception:
                pass

            with self._lock:
                self._active_process = None

            if exit_code != 0:
                job.status = JobStatus.FAILED
                error_summary = "".join(captured_output[-10:])
                job.error_message = f"Process exited with code {exit_code}.\n{error_summary}"
                telemetry.status = "FAILED"
                telemetry.error_message = job.error_message
                return

            # Check for results.npy
            job.status = JobStatus.DECODING
            decode_start = time.time()
            
            # The upstream script creates results.npy either directly in output_dir or in a subfolder
            results_path = job.output_dir / "results.npy"
            if not results_path.exists():
                # Search subdirectories if any
                found = list(job.output_dir.glob("**/results.npy"))
                if found:
                    results_path = found[0]
                else:
                    raise FileNotFoundError(f"Generation finished but results.npy was not found in {job.output_dir}")

            motion_clip = decode_results_npy(
                results_path,
                prompt=job.prompt,
                checkpoint_path=self.checkpoint_path.name,
                provenance="real_inference",
            )
            
            decode_end = time.time()
            telemetry.decode_seconds = round(decode_end - decode_start, 3)
            telemetry.actual_duration_seconds = motion_clip.duration_seconds
            telemetry.num_frames = motion_clip.num_frames
            telemetry.motion_fps = motion_clip.fps
            telemetry.status = "SUCCESS"

            # Save metadata sidecar
            motion_clip.save_sidecar(job.output_dir / "metadata.json")

            job.motion_clip = motion_clip
            job.status = JobStatus.COMPLETED

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            telemetry.status = "FAILED"
            telemetry.error_message = str(e)

        finally:
            job.end_time = time.time()
            telemetry.calculate_derived_metrics()
            job.telemetry = telemetry
            if on_complete:
                try:
                    on_complete(job)
                except Exception as cb_err:
                    print(f"Error in on_complete callback: {cb_err}", file=sys.stderr)
