/**
 * Timeline and Playback Controller.
 * Ensures frame-synchronized playback across Skeleton and VRM avatar.
 */

export class TimelineController {
  constructor() {
    this.fps = 20.0;
    this.totalFrames = 60;
    this.duration = 3.0;
    this.currentTime = 0.0;
    this.currentFrame = 0;

    this.isPlaying = true;
    this.isLooping = true;
    this.playbackSpeed = 1.0;

    this.frameCallbacks = [];
  }

  setMotionSequence(totalFrames, fps, duration = null) {
    this.totalFrames = Math.max(1, totalFrames);
    this.fps = fps > 0 ? fps : 20.0;
    this.duration = duration && duration > 0 ? duration : this.totalFrames / this.fps;
    this.currentTime = 0.0;
    this.currentFrame = 0;
    this.notifyFrame();
  }

  onFrameUpdate(fn) {
    this.frameCallbacks.push(fn);
  }

  notifyFrame() {
    for (const fn of this.frameCallbacks) {
      fn(this.currentFrame, this.currentTime, this.totalFrames, this.duration);
    }
  }

  play() {
    this.isPlaying = true;
  }

  pause() {
    this.isPlaying = false;
  }

  togglePlay() {
    this.isPlaying = !this.isPlaying;
    return this.isPlaying;
  }

  restart() {
    this.currentTime = 0.0;
    this.currentFrame = 0;
    this.isPlaying = true;
    this.notifyFrame();
  }

  seekToTime(time) {
    this.currentTime = Math.max(0.0, Math.min(time, this.duration));
    this.currentFrame = Math.min(
      Math.floor(this.currentTime * this.fps),
      this.totalFrames - 1
    );
    this.notifyFrame();
  }

  seekToFrame(frame) {
    const clamped = Math.max(0, Math.min(frame, this.totalFrames - 1));
    this.currentFrame = clamped;
    this.currentTime = clamped / this.fps;
    this.notifyFrame();
  }

  setLoop(loop) {
    this.isLooping = Boolean(loop);
  }

  setSpeed(speed) {
    this.playbackSpeed = Math.max(0.1, Math.min(speed, 4.0));
  }

  update(deltaSeconds) {
    if (!this.isPlaying || this.totalFrames <= 1) return;

    this.currentTime += deltaSeconds * this.playbackSpeed;

    if (this.currentTime >= this.duration) {
      if (this.isLooping) {
        this.currentTime = this.currentTime % this.duration;
      } else {
        this.currentTime = this.duration;
        this.isPlaying = false;
      }
    }

    const newFrame = Math.min(
      Math.floor(this.currentTime * this.fps),
      this.totalFrames - 1
    );

    if (newFrame !== this.currentFrame) {
      this.currentFrame = newFrame;
      this.notifyFrame();
    }
  }
}
