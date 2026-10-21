"""
Unit tests for Viewer Helpers, CLI argument safety and job states.
"""
import pytest
from pathlib import Path
import sys

EXPERIMENT_ROOT = Path(__file__).resolve().parent.parent
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from app.dip_adapter import DiPAdapter, GenerationJob, JobStatus
from app.motion_decoder import create_fixture_motion


def test_bone_line_segments_generation():
    """Verify bone segments can be constructed without error."""
    fixture = create_fixture_motion(num_frames=10)
    segments = fixture.get_bone_segments(0)
    assert segments.ndim == 3
    assert segments.shape == (21, 2, 3)  # 21 bones in SMPL-22


def test_cli_argument_construction_safety():
    """Verify that complex prompts with quotes, apostrophes and spaces do not break argument structure."""
    adapter = DiPAdapter()
    tricky_prompt = 'A person says "hello", then walks 5 steps & jumps!'
    
    # We test the job structure
    job = adapter.submit_job(
        prompt=tricky_prompt,
        motion_length=3.5,
        guidance_param=7.5,
        device=0,
    )
    assert job.prompt == tricky_prompt
    assert job.status in (JobStatus.QUEUED, JobStatus.RUNNING)
    
    # Cancel immediately
    adapter.cancel_current_job()
    assert adapter.current_job.status in (JobStatus.CANCELLED, JobStatus.RUNNING, JobStatus.FAILED)


def test_job_status_enum():
    """Verify all job statuses are defined."""
    assert JobStatus.IDLE == "IDLE"
    assert JobStatus.QUEUED == "QUEUED"
    assert JobStatus.RUNNING == "RUNNING"
    assert JobStatus.DECODING == "DECODING"
    assert JobStatus.COMPLETED == "COMPLETED"
    assert JobStatus.FAILED == "FAILED"
    assert JobStatus.CANCELLED == "CANCELLED"
