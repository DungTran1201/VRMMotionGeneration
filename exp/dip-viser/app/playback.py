"""
Playback Controller for DiP-Viser Experiment.
Maintains continuous clock, frame indexing, looping, seeking, and speed scaling.
"""
from typing import Tuple


class PlaybackController:
    """
    Clock-driven animation playback controller.
    Supports arbitrary delta-time updates, looping, speed multipliers, and clamping.
    """
    def __init__(self, num_frames: int = 0, fps: float = 20.0, loop: bool = True):
        self.num_frames = max(0, num_frames)
        self.fps = float(fps) if fps > 0 else 20.0
        self.loop = loop
        self.speed = 1.0
        self.is_playing = False
        
        self._current_time: float = 0.0
        self._current_frame: int = 0

    @property
    def current_frame(self) -> int:
        return self._current_frame

    @property
    def current_time(self) -> float:
        return self._current_time

    @property
    def duration(self) -> float:
        if self.num_frames <= 0:
            return 0.0
        return float(self.num_frames) / self.fps

    def set_motion(self, num_frames: int, fps: float = 20.0) -> None:
        """Reset or bind to a new motion clip."""
        self.num_frames = max(0, num_frames)
        self.fps = float(fps) if fps > 0 else 20.0
        self.reset()

    def play(self) -> None:
        if self.num_frames > 0:
            # If at the end and not looping, rewind to start
            if self._current_frame >= self.num_frames - 1 and not self.loop:
                self.reset()
            self.is_playing = True

    def pause(self) -> None:
        self.is_playing = False

    def toggle_play(self) -> bool:
        if self.is_playing:
            self.pause()
        else:
            self.play()
        return self.is_playing

    def reset(self) -> None:
        self._current_time = 0.0
        self._current_frame = 0

    def seek_frame(self, frame_idx: int) -> int:
        if self.num_frames <= 0:
            self._current_frame = 0
            self._current_time = 0.0
            return 0
        clamped = max(0, min(self.num_frames - 1, frame_idx))
        self._current_frame = clamped
        self._current_time = float(clamped) / self.fps
        return self._current_frame

    def seek_time(self, timestamp: float) -> int:
        if self.duration <= 0.0:
            return 0
        clamped_t = max(0.0, min(self.duration, timestamp))
        frame_idx = int(clamped_t * self.fps)
        return self.seek_frame(frame_idx)

    def step(self, delta_frames: int) -> int:
        return self.seek_frame(self._current_frame + delta_frames)

    def update(self, dt: float) -> Tuple[int, bool]:
        """
        Advance playback clock by dt seconds.
        Returns: (current_frame, frame_changed_flag)
        """
        if not self.is_playing or self.num_frames <= 1:
            return self._current_frame, False

        prev_frame = self._current_frame
        effective_dt = dt * self.speed
        self._current_time += effective_dt

        max_duration = self.duration

        if self._current_time >= max_duration:
            if self.loop:
                # Wrap around without re-triggering inference
                self._current_time = self._current_time % max_duration
            else:
                self._current_time = max_duration
                self.is_playing = False

        new_frame = min(self.num_frames - 1, int(self._current_time * self.fps))
        self._current_frame = new_frame
        frame_changed = (new_frame != prev_frame)
        return self._current_frame, frame_changed
