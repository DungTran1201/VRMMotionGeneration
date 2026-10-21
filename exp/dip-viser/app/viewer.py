"""
Viser Interactive 3D Skeleton Motion Viewer for DiP Experiment.
Renders real DiP-generated motions and test fixtures with playback controls,
interactive generation triggers, and live performance telemetry.
"""
import os
from pathlib import Path
import threading
import time
from typing import Any, Dict, List, Optional
import numpy as np
import viser

from .config import (
    CHECKPOINT_MODEL_PATH,
    DEFAULT_DURATION_SECONDS,
    DEFAULT_GUIDANCE_PARAM,
    DEFAULT_HOST,
    DEFAULT_PORT,
    NUM_JOINTS,
    PROMPTS_FILE,
    SAMPLES_DIR,
)
from .dip_adapter import DiPAdapter, GenerationJob, JobStatus
from .motion_decoder import create_fixture_motion, decode_results_npy
from .motion_schema import MotionClip
from .playback import PlaybackController


class ViserMotionViewer:
    """
    Interactive Viser 3D Viewer for DiP text-to-motion visualization.
    """
    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        adapter: Optional[DiPAdapter] = None,
    ):
        self.host = host
        self.port = port
        self.adapter = adapter or DiPAdapter()
        
        # Current active clip and playback controller
        self.clip: Optional[MotionClip] = None
        self.playback = PlaybackController(num_frames=0, fps=20.0, loop=True)
        self._lock = threading.Lock()
        self._running = False
        self._playback_thread: Optional[threading.Thread] = None

        # Scene and GUI handles
        self.server = viser.ViserServer(host=self.host, port=self.port)
        self.joint_handle: Optional[viser.PointCloudHandle] = None
        self.bone_handle: Optional[viser.LineSegmentsHandle] = None
        self.gui_elements: Dict[str, Any] = {}

        self._setup_scene()
        self._setup_gui()
        self._load_initial_motion()
        self._start_playback_loop()

    def _setup_scene(self) -> None:
        """Initialize coordinate system, ground grid, lighting and axes."""
        self.server.scene.set_up_direction("+y")
        
        # Ground grid on XZ plane with Y=0
        self.server.scene.add_grid(
            "/scene/ground",
            width=14.0,
            height=14.0,
            plane="xz",
            cell_size=0.5,
            section_size=1.0,
            cell_color=(190, 195, 200),
            section_color=(120, 125, 135),
        )
        
        # Coordinate frame axes at world origin
        self.server.scene.add_frame(
            "/scene/origin",
            show_axes=True,
            axes_length=0.4,
            axes_radius=0.008,
            position=(0.0, 0.0, 0.0),
        )

        # Placeholder joint and bone handles
        dummy_joints = np.zeros((NUM_JOINTS, 3), dtype=np.float32)
        dummy_bones = np.zeros((len(self.playback.num_frames and self.clip.bones or [0]*21), 2, 3), dtype=np.float32)

        self.joint_handle = self.server.scene.add_point_cloud(
            "/skeleton/joints",
            points=dummy_joints,
            colors=(235, 95, 30),
            point_size=0.045,
            point_shape="circle",
        )

        self.bone_handle = self.server.scene.add_line_segments(
            "/skeleton/bones",
            points=dummy_bones,
            colors=(55, 135, 235),
            thickness=0.012,
        )

    def _setup_gui(self) -> None:
        """Configure interactive GUI panels."""
        self.server.gui.configure_theme(brand_color=(235, 95, 30))

        # Title & Provenance Badge
        self.gui_elements["provenance_md"] = self.server.gui.add_markdown(
            "### ⏳ Initializing Viewer..."
        )
        self.server.gui.add_divider()

        # Prompt & Generation Folder
        with self.server.gui.add_folder("Motion Generation (DiP)"):
            preset_options = [
                "A person walks forward and waves.",
                "A person runs forward and jumps.",
                "A person kicks with their right leg.",
                "A person sits down on the ground.",
                "A person turns around and dances.",
            ]
            self.gui_elements["prompt_preset"] = self.server.gui.add_dropdown(
                "Preset Prompts",
                options=preset_options,
                initial_value=preset_options[0],
            )

            self.gui_elements["prompt_input"] = self.server.gui.add_text(
                "Prompt Input",
                initial_value=preset_options[0],
            )

            @self.gui_elements["prompt_preset"].on_update
            def _(_):
                self.gui_elements["prompt_input"].value = self.gui_elements["prompt_preset"].value

            self.gui_elements["duration_slider"] = self.server.gui.add_slider(
                "Duration (seconds)",
                min=2.0,
                max=9.8,
                step=0.5,
                initial_value=DEFAULT_DURATION_SECONDS,
            )

            self.gui_elements["guidance_slider"] = self.server.gui.add_slider(
                "Guidance Scale",
                min=1.0,
                max=15.0,
                step=0.5,
                initial_value=DEFAULT_GUIDANCE_PARAM,
            )

            self.gui_elements["device_select"] = self.server.gui.add_dropdown(
                "Compute Device",
                options=["GPU (cuda:0)", "CPU"],
                initial_value="GPU (cuda:0)",
            )

            self.gui_elements["btn_generate"] = self.server.gui.add_button(
                "🚀 Generate Motion",
                color="primary",
            )
            self.gui_elements["btn_load_fixture"] = self.server.gui.add_button(
                "📦 Load Synthetic Fixture",
            )

            self.gui_elements["status_text"] = self.server.gui.add_text(
                "Job Status",
                initial_value="Ready",
                disabled=True,
            )

            @self.gui_elements["btn_generate"].on_click
            def _(_):
                self._on_generate_clicked()

            @self.gui_elements["btn_load_fixture"].on_click
            def _(_):
                self._load_synthetic_fixture()

        # Playback Controls Folder
        with self.server.gui.add_folder("Playback Controls"):
            self.gui_elements["btn_play_pause"] = self.server.gui.add_button("▶ Play / ⏸ Pause")
            
            self.gui_elements["timeline_slider"] = self.server.gui.add_slider(
                "Timeline (Frame)",
                min=0,
                max=1,
                step=1,
                initial_value=0,
            )

            self.gui_elements["loop_checkbox"] = self.server.gui.add_checkbox(
                "Loop Playback",
                initial_value=True,
            )

            self.gui_elements["speed_select"] = self.server.gui.add_dropdown(
                "Playback Speed",
                options=["0.25x", "0.5x", "1.0x", "1.5x", "2.0x"],
                initial_value="1.0x",
            )

            self.gui_elements["btn_reset"] = self.server.gui.add_button("⏮ Reset to Start")

            @self.gui_elements["btn_play_pause"].on_click
            def _(_):
                self.playback.toggle_play()

            @self.gui_elements["timeline_slider"].on_update
            def _(_):
                # When user manually drags the slider
                if not self.playback.is_playing:
                    self.playback.seek_frame(int(self.gui_elements["timeline_slider"].value))
                    self._render_current_frame()

            @self.gui_elements["loop_checkbox"].on_update
            def _(_):
                self.playback.loop = self.gui_elements["loop_checkbox"].value

            @self.gui_elements["speed_select"].on_update
            def _(_):
                speed_str = self.gui_elements["speed_select"].value.replace("x", "")
                try:
                    self.playback.speed = float(speed_str)
                except ValueError:
                    self.playback.speed = 1.0

            @self.gui_elements["btn_reset"].on_click
            def _(_):
                self.playback.reset()
                self._render_current_frame()

        # Display Options
        with self.server.gui.add_folder("Display Options"):
            self.gui_elements["cb_skeleton_vis"] = self.server.gui.add_checkbox(
                "Skeleton Visible",
                initial_value=True,
            )
            self.gui_elements["slider_joint_size"] = self.server.gui.add_slider(
                "Joint Size",
                min=0.01,
                max=0.10,
                step=0.005,
                initial_value=0.045,
            )

            @self.gui_elements["cb_skeleton_vis"].on_update
            def _(_):
                vis = self.gui_elements["cb_skeleton_vis"].value
                if self.joint_handle:
                    self.joint_handle.visible = vis
                if self.bone_handle:
                    self.bone_handle.visible = vis

            @self.gui_elements["slider_joint_size"].on_update
            def _(_):
                # Point size in Viser can be re-applied or updated
                val = self.gui_elements["slider_joint_size"].value
                if self.joint_handle and self.clip:
                    joints = self.clip.get_frame(self.playback.current_frame)
                    self.joint_handle = self.server.scene.add_point_cloud(
                        "/skeleton/joints",
                        points=joints,
                        colors=(235, 95, 30),
                        point_size=val,
                        point_shape="circle",
                    )

        # Telemetry & Diagnostics Folder (Collapsed by default)
        with self.server.gui.add_folder("Telemetry & Diagnostics", expand_by_default=False):
            self.gui_elements["diag_model"] = self.server.gui.add_text("Model", initial_value="DiP", disabled=True)
            self.gui_elements["diag_checkpoint"] = self.server.gui.add_text("Checkpoint", initial_value=CHECKPOINT_MODEL_PATH.name, disabled=True)
            self.gui_elements["diag_duration"] = self.server.gui.add_text("Duration / Frames", initial_value="0.0s (0 frames)", disabled=True)
            self.gui_elements["diag_latency"] = self.server.gui.add_text("Inference Latency", initial_value="N/A", disabled=True)
            self.gui_elements["diag_rtf"] = self.server.gui.add_text("Real-Time Factor (RTF)", initial_value="N/A", disabled=True)
            self.gui_elements["diag_gen_fps"] = self.server.gui.add_text("Generated Motion FPS", initial_value="N/A", disabled=True)
            self.gui_elements["diag_path"] = self.server.gui.add_text("Output Directory", initial_value="N/A", disabled=True)

    def _load_initial_motion(self) -> None:
        """Check for existing real DiP sample first; fallback to fixture."""
        sample_path = SAMPLES_DIR / "sample_01" / "results.npy"
        if sample_path.exists():
            try:
                clip = decode_results_npy(sample_path, provenance="real_inference")
                self.set_motion_clip(clip)
                return
            except Exception as e:
                print(f"Warning: Failed to load existing sample_01: {e}")

        # Fallback to synthetic fixture
        self._load_synthetic_fixture()

    def _load_synthetic_fixture(self) -> None:
        """Load deterministic procedural walking fixture."""
        fixture = create_fixture_motion(
            prompt="FIXTURE: Procedural walking human",
            num_frames=80,
            fps=20.0,
        )
        self.set_motion_clip(fixture)

    def set_motion_clip(self, clip: MotionClip) -> None:
        """Set new motion sequence and update viewer widgets."""
        with self._lock:
            self.clip = clip
            self.playback.set_motion(num_frames=clip.num_frames, fps=clip.fps)
            
            # Update provenance badge
            if clip.provenance == "real_inference":
                badge = (
                    "### 🟢 REAL MODEL INFERENCE\n"
                    f"**Prompt**: *\"{clip.prompt}\"*\n\n"
                    f"**Model**: `{clip.source_model}` | **Frames**: `{clip.num_frames}` | **FPS**: `{clip.fps:.0f}`"
                )
            else:
                badge = (
                    "### ⚠️ FIXTURE — NOT MODEL OUTPUT\n"
                    f"**Note**: *Synthetic procedural motion for offline verification.*\n\n"
                    f"**Frames**: `{clip.num_frames}` | **FPS**: `{clip.fps:.0f}`"
                )
            self.gui_elements["provenance_md"].content = badge

            # Update timeline slider bounds
            max_f = max(1, clip.num_frames - 1)
            self.gui_elements["timeline_slider"].max = max_f
            self.gui_elements["timeline_slider"].value = 0

            # Update diagnostics
            self.gui_elements["diag_duration"].value = f"{clip.duration_seconds:.2f}s ({clip.num_frames} frames @ {clip.fps} FPS)"
            if "output_dir" in clip.metadata:
                self.gui_elements["diag_path"].value = str(clip.metadata["output_dir"])

            self._render_current_frame()
            self.playback.play()

    def _on_generate_clicked(self) -> None:
        """Handle Generate button click with background job execution."""
        prompt = self.gui_elements["prompt_input"].value.strip()
        if not prompt:
            self.gui_elements["status_text"].value = "Error: Prompt is empty"
            return

        duration = float(self.gui_elements["duration_slider"].value)
        guidance = float(self.gui_elements["guidance_slider"].value)
        device_choice = self.gui_elements["device_select"].value
        device_id = 0 if "GPU" in device_choice else -1

        self.gui_elements["status_text"].value = "Starting generation..."
        self.gui_elements["btn_generate"].disabled = True

        def _on_complete(job: GenerationJob) -> None:
            self.gui_elements["btn_generate"].disabled = False
            if job.status == JobStatus.COMPLETED and job.motion_clip:
                self.gui_elements["status_text"].value = f"Completed in {job.telemetry.inference_seconds:.2f}s"
                if job.telemetry:
                    self.gui_elements["diag_latency"].value = f"{job.telemetry.inference_seconds:.3f} s"
                    self.gui_elements["diag_rtf"].value = f"{job.telemetry.real_time_factor:.3f}x"
                    self.gui_elements["diag_gen_fps"].value = f"{job.telemetry.generated_fps:.1f} FPS"
                if job.output_dir:
                    job.motion_clip.metadata["output_dir"] = str(job.output_dir)
                    self.gui_elements["diag_path"].value = str(job.output_dir)
                self.set_motion_clip(job.motion_clip)
            else:
                err_msg = job.error_message or "Unknown failure"
                self.gui_elements["status_text"].value = f"Failed: {err_msg[:60]}"

        job = self.adapter.submit_job(
            prompt=prompt,
            motion_length=duration,
            guidance_param=guidance,
            device=device_id,
            on_complete=_on_complete,
        )

        # Monitor progress text in separate small updater
        def _monitor():
            while job.status in (JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.DECODING):
                self.gui_elements["status_text"].value = f"Status: {job.status.value}..."
                time.sleep(0.5)

        threading.Thread(target=_monitor, daemon=True).start()

    def _render_current_frame(self) -> None:
        """Update Viser scene objects for the current playback frame."""
        if not self.clip or self.clip.num_frames == 0:
            return

        frame_idx = self.playback.current_frame
        joints = self.clip.get_frame(frame_idx)
        bone_segments = self.clip.get_bone_segments(frame_idx)

        # Update handles directly without recreating scene objects
        if self.joint_handle:
            self.joint_handle.points = joints
        if self.bone_handle:
            self.bone_handle.points = bone_segments

    def _start_playback_loop(self) -> None:
        """Start the animation clock thread."""
        self._running = True
        
        def _loop():
            last_tick = time.time()
            target_dt = 1.0 / 30.0  # ~30 Hz update rate
            
            while self._running:
                now = time.time()
                dt = now - last_tick
                last_tick = now

                with self._lock:
                    if self.clip and self.playback.is_playing:
                        curr_frame, changed = self.playback.update(dt)
                        if changed:
                            self._render_current_frame()
                            # Reflect frame change on slider without feedback loop
                            try:
                                self.gui_elements["timeline_slider"].value = curr_frame
                            except Exception:
                                pass

                elapsed = time.time() - now
                sleep_time = max(0.005, target_dt - elapsed)
                time.sleep(sleep_time)

        self._playback_thread = threading.Thread(target=_loop, daemon=True, name="viser-playback-clock")
        self._playback_thread.start()

    def stop(self) -> None:
        """Stop viewer and server."""
        self._running = False
        if self.server:
            self.server.stop()
