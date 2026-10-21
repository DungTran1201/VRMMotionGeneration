"""
Unit tests for Timing Metrics, Playback Clock Controller, and Telemetry Logging.
"""
import pytest
from pathlib import Path
import sys

EXPERIMENT_ROOT = Path(__file__).resolve().parent.parent
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from app.playback import PlaybackController
from app.telemetry import TelemetryLogger, TelemetryRecord


def test_telemetry_derived_metrics():
    """Verify generated_fps, RTF and latency calculations."""
    record = TelemetryRecord(
        prompt="Walk forward",
        inference_seconds=2.0,
        load_time_seconds=0.5,
        decode_seconds=0.1,
        num_frames=80,
        actual_duration_seconds=4.0,
        motion_fps=20.0,
    )
    record.calculate_derived_metrics()
    
    # 80 frames / 2.0 s = 40.0 fps
    assert record.generated_fps == 40.0
    # 2.0 s / 4.0 s = 0.5x RTF (faster than realtime)
    assert record.real_time_factor == 0.5
    # 0.5 + 2.0 + 0.1 = 2.6 s
    assert record.total_latency_seconds == 2.6


def test_playback_controller_stepping_and_clamping():
    """Verify playback seek, stepping and boundary clamping."""
    pc = PlaybackController(num_frames=100, fps=20.0, loop=True)
    assert pc.duration == 5.0
    assert pc.current_frame == 0
    
    # Seek frame
    pc.seek_frame(50)
    assert pc.current_frame == 50
    assert pc.current_time == 2.5
    
    # Negative clamp
    pc.seek_frame(-10)
    assert pc.current_frame == 0
    
    # Overshoot clamp
    pc.seek_frame(250)
    assert pc.current_frame == 99


def test_playback_controller_looping():
    """Verify that looping wraps time and frame without stopping."""
    pc = PlaybackController(num_frames=40, fps=20.0, loop=True)
    pc.play()
    
    # Advance 1.5 seconds (30 frames)
    frame, changed = pc.update(1.5)
    assert frame == 30
    assert changed is True
    assert pc.is_playing is True
    
    # Advance past end (duration is 2.0s; advance another 1.0s -> 2.5s total -> wraps to 0.5s -> frame 10)
    frame, changed = pc.update(1.0)
    assert frame == 10
    assert pc.is_playing is True


def test_playback_controller_no_loop_stops_at_end():
    """Verify that when loop=False, playback stops at the final frame."""
    pc = PlaybackController(num_frames=40, fps=20.0, loop=False)
    pc.play()
    
    # Advance past 2.0s duration
    frame, _ = pc.update(5.0)
    assert frame == 39
    assert pc.is_playing is False


def test_playback_speed_scaling():
    """Verify playback speed multiplier affects clock advancement."""
    pc = PlaybackController(num_frames=100, fps=20.0, loop=True)
    pc.speed = 2.0  # 2x speed
    pc.play()
    
    # Advance 1.0 real second -> effectively 2.0 seconds -> 40 frames
    frame, _ = pc.update(1.0)
    assert frame == 40


def test_telemetry_logger_export():
    """Verify TelemetryLogger writes valid JSON and Markdown files."""
    import tempfile
    with tempfile.TemporaryDirectory(dir=str(EXPERIMENT_ROOT / "artifacts")) as tmp_dir:
        tmp_path = Path(tmp_dir)
        logger = TelemetryLogger(output_dir=tmp_path)
        rec = TelemetryRecord(
            prompt="Test prompt",
            inference_seconds=1.5,
            num_frames=60,
            actual_duration_seconds=3.0,
            status="SUCCESS",
        )
        logger.log(rec)
        
        json_file = logger.save_json("test_bench.json")
        assert json_file.exists()
        
        md_file = logger.save_markdown_summary("test_bench.md")
        assert md_file.exists()
        
        content = md_file.read_text(encoding="utf-8")
        assert "Test prompt" in content
        assert "Real-Time Factor" in content
