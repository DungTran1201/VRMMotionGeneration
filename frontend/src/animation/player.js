/**
 * Decoupled Animation Player with Slerp Interpolation and Clock Management.
 */

import * as THREE from 'three';

export class AnimationPlayer {
  constructor(avatarManager) {
    this.avatar = avatarManager;
    this.motion = null;
    this.isPlaying = false;
    this.currentTime = 0.0;
    this.playbackSpeed = 1.0;
    this.loop = true;

    // Temporary Three.js math objects to avoid garbage collection
    this._q1 = new THREE.Quaternion();
    this._q2 = new THREE.Quaternion();
    this._qInterp = new THREE.Quaternion();
    this._p1 = new THREE.Vector3();
    this._p2 = new THREE.Vector3();
    this._pInterp = new THREE.Vector3();

    // Callbacks
    this.onProgress = null;
    this.onStateChange = null;
  }

  loadMotion(motionDoc) {
    this.motion = motionDoc;
    this.currentTime = 0.0;
    this.isPlaying = true;

    // Apply first frame immediately
    this.applyCurrentTimePose(0.016);

    if (this.onStateChange) {
      this.onStateChange({
        isPlaying: this.isPlaying,
        currentTime: this.currentTime,
        duration: this.getDuration(),
        motion: this.motion
      });
    }
  }

  getDuration() {
    return this.motion ? this.motion.metadata.duration : 0.0;
  }

  play() {
    if (!this.motion) return;
    this.isPlaying = true;
    if (this.onStateChange) this.onStateChange({ isPlaying: true });
  }

  pause() {
    this.isPlaying = false;
    if (this.onStateChange) this.onStateChange({ isPlaying: false });
  }

  togglePlayPause() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  restart() {
    this.currentTime = 0.0;
    this.applyCurrentTimePose(0.016);
    this.play();
  }

  seek(normalizedProgress) {
    if (!this.motion) return;
    const duration = this.getDuration();
    this.currentTime = THREE.MathUtils.clamp(normalizedProgress * duration, 0.0, duration);
    this.applyCurrentTimePose(0.016);
  }

  setSpeed(speed) {
    this.playbackSpeed = Math.max(0.1, Math.min(speed, 5.0));
  }

  setLoop(enable) {
    this.loop = enable;
  }

  update(delta) {
    if (!this.isPlaying || !this.motion) return;

    const duration = this.getDuration();
    if (duration <= 0) return;

    this.currentTime += delta * this.playbackSpeed;

    if (this.currentTime >= duration) {
      if (this.loop) {
        this.currentTime = this.currentTime % duration;
      } else {
        this.currentTime = duration;
        this.pause();
      }
    }

    this.applyCurrentTimePose(delta);

    if (this.onProgress) {
      this.onProgress({
        currentTime: this.currentTime,
        duration,
        progress: duration > 0 ? this.currentTime / duration : 0.0,
      });
    }
  }

  applyCurrentTimePose(delta) {
    if (!this.motion || !this.motion.frames || this.motion.frames.length === 0) return;

    const frames = this.motion.frames;
    const duration = this.getDuration();

    // 1. Find bounding keyframes for current timestamp
    let f1Index = 0;
    let f2Index = 0;

    for (let i = 0; i < frames.length - 1; i++) {
      if (this.currentTime >= frames[i].timestamp && this.currentTime <= frames[i + 1].timestamp) {
        f1Index = i;
        f2Index = i + 1;
        break;
      }
    }

    if (this.currentTime >= frames[frames.length - 1].timestamp) {
      f1Index = frames.length - 1;
      f2Index = frames.length - 1;
    }

    const f1 = frames[f1Index];
    const f2 = frames[f2Index];

    // Calculate interpolation factor alpha in [0, 1]
    let alpha = 0.0;
    const dt = f2.timestamp - f1.timestamp;
    if (dt > 1e-6) {
      alpha = THREE.MathUtils.clamp((this.currentTime - f1.timestamp) / dt, 0.0, 1.0);
    }

    // 2. Interpolate Root Position and Rotation
    this._p1.fromArray(f1.root.position);
    this._p2.fromArray(f2.root.position);
    this._pInterp.lerpVectors(this._p1, this._p2, alpha);

    this._q1.fromArray(f1.root.rotation);
    this._q2.fromArray(f2.root.rotation);
    this._qInterp.copy(this._q1).slerp(this._q2, alpha);

    // 3. Interpolate Bones
    const interpolatedBones = {};
    const boneNames = Object.keys(f1.bones);

    for (const bName of boneNames) {
      const b1 = f1.bones[bName];
      const b2 = f2.bones[bName] || b1;

      this._q1.fromArray(b1.rotation);
      this._q2.fromArray(b2.rotation);
      const bQuat = new THREE.Quaternion().copy(this._q1).slerp(this._q2, alpha);

      interpolatedBones[bName] = {
        rotation: [bQuat.x, bQuat.y, bQuat.z, bQuat.w]
      };
    }

    // 4. Apply to Avatar
    this.avatar.applyPose(
      [this._pInterp.x, this._pInterp.y, this._pInterp.z],
      [this._qInterp.x, this._qInterp.y, this._qInterp.z, this._qInterp.w],
      interpolatedBones,
      delta
    );

    // Update active contact and diagnostics reporting
    this.currentFrameData = {
      rootPos: [this._pInterp.x, this._pInterp.y, this._pInterp.z],
      rootRot: [this._qInterp.x, this._qInterp.y, this._qInterp.z, this._qInterp.w],
      contacts: f1.contacts || { leftFoot: false, rightFoot: false }
    };
  }
}
