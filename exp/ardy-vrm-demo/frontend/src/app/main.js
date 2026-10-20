/**
 * Main application coordinator for ARDY -> VRM Motion Lab.
 * Manages full-page 3D stage, customizable floating tool windows,
 * synchronized timeline playback, and reliable VRM loading.
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';

import { ApiClient } from '../api/client.js';
import { ViewerStage } from '../scene/viewer_stage.js';
import { SkeletonRenderer } from '../skeleton/skeleton_renderer.js';
import { VrmManager } from '../vrm/vrm_manager.js';
import { TimelineController } from '../animation/timeline_controller.js';
import { TelemetryHud } from '../telemetry/telemetry_hud.js';
import { FloatingWindow } from '../components/floating_window.js';

class App {
  constructor() {
    this.api = new ApiClient();
    this.telemetry = new TelemetryHud();
    this.timeline = new TimelineController();

    // DOM Elements - Stage & Canvas
    this.stageCanvas = document.getElementById('stageCanvas');
    this.stageDropOverlay = document.getElementById('stageDropOverlay');

    // DOM Elements - Toolbar
    this.btnToggleControls = document.getElementById('btnToggleControls');
    this.btnToggleTelemetry = document.getElementById('btnToggleTelemetry');
    this.btnResetCamera = document.getElementById('btnResetCamera');
    this.btnFrameAvatar = document.getElementById('btnFrameAvatar');
    this.btnFrameSkeleton = document.getElementById('btnFrameSkeleton');
    this.btnFrameBoth = document.getElementById('btnFrameBoth');

    // DOM Elements - Motion Controls Window
    this.winControlsEl = document.getElementById('winMotionControls');
    this.promptInput = document.getElementById('promptInput');
    this.durationSlider = document.getElementById('durationSlider');
    this.durationVal = document.getElementById('durationVal');
    this.seedInput = document.getElementById('seedInput');
    this.loopToggle = document.getElementById('loopToggle');
    this.showSkeletonToggle = document.getElementById('showSkeletonToggle');
    this.showVrmToggle = document.getElementById('showVrmToggle');
    this.btnGenerate = document.getElementById('btnGenerate');
    this.btnCancel = document.getElementById('btnCancel');
    this.btnLoadVrm = document.getElementById('btnLoadVrm');
    this.btnRemoveVrm = document.getElementById('btnRemoveVrm');
    this.vrmFileInput = document.getElementById('vrmFileInput');
    this.vrmInfoBadge = document.getElementById('vrmInfoBadge');
    this.vrmStatusText = document.getElementById('vrmStatusText');

    // DOM Elements - Timeline Scrubber
    this.btnPlayPause = document.getElementById('btnPlayPause');
    this.btnRestart = document.getElementById('btnRestart');
    this.timelineSlider = document.getElementById('timelineSlider');
    this.timelineLabel = document.getElementById('timelineLabel');
    this.speedSelect = document.getElementById('speedSelect');

    // DOM Elements - Notification Toast
    this.toastBanner = document.getElementById('toastBanner');

    // Initialize 3D Stage & Rig Managers
    this.stage = new ViewerStage(THREE, OrbitControls, this.stageCanvas);
    this.skeletonRenderer = new SkeletonRenderer(THREE, this.stage.skeletonRoot);
    this.vrmManager = new VrmManager(THREE, this.stage.vrmRoot, GLTFLoader, VRMLoaderPlugin, VRMUtils);

    // Initialize Floating Windows
    const isMobile = window.innerWidth < 768;
    this.winControls = new FloatingWindow(this.winControlsEl, {
      minWidth: 320,
      minHeight: 220,
      initialX: isMobile ? 12 : 24,
      initialY: 60,
    });

    this.winTelemetryEl = document.getElementById('winTelemetry');
    this.winTelemetry = new FloatingWindow(this.winTelemetryEl, {
      minWidth: 280,
      minHeight: 180,
      initialX: isMobile ? 12 : Math.max(24, window.innerWidth - 380),
      initialY: isMobile ? 320 : 60,
    });

    this.activeJobId = null;
    this.activeWebSocket = null;
    this.currentMotionPayload = null;
    this.clock = new THREE.Clock();

    this.init();
  }

  async init() {
    this.bindEvents();
    this.setupPresets();

    // Timeline tick subscription
    this.timeline.onFrameUpdate((frame, time, totalFrames, duration) => {
      this.updateTimelineUI(frame, time, totalFrames, duration);
    });

    // Check backend health and GPU specifications
    try {
      const health = await this.api.getHealth();
      this.telemetry.setSystemInfo(health);
      this.telemetry.setMode(health.mode);
    } catch (e) {
      console.warn('Backend offline or health probe failed:', e);
      this.telemetry.setMode('MODEL OFFLINE');
      this.showToast('Backend server is not responding. Showing offline mode.');
    }

    // Load initial default motion sequence
    try {
      this.telemetry.setStatus('Loading sample motion...');
      const sample = await this.api.getDefaultSample();
      this.applyMotionPayload(sample);
      this.telemetry.setStatus('Playing');
    } catch (e) {
      console.warn('Could not load default motion sample:', e);
      this.telemetry.setStatus('Idle');
    }

    // Start single continuous animation loop
    requestAnimationFrame((t) => this.loop(t));
  }

  applyMotionPayload(payload) {
    if (!payload) return;
    this.currentMotionPayload = payload;

    if (payload.prompt && this.promptInput && !this.promptInput.value) {
      this.promptInput.value = payload.prompt;
    }

    // Load skeleton data into skeleton renderer
    if (payload.skeleton) {
      this.skeletonRenderer.loadSkeletonData(payload.skeleton);
    }

    // Apply VRM motion data to VRM avatar manager
    if (payload.vrm) {
      this.vrmManager.setMotionData(payload.vrm);
      // Immediately pose to current frame if avatar already loaded
      this.vrmManager.updateFrame(this.timeline.currentFrame);
    }

    // Synchronize timeline sequence
    this.timeline.setMotionSequence(
      payload.total_frames,
      payload.fps,
      payload.duration_seconds
    );

    // Update telemetry metrics with truthful data
    this.telemetry.updateMetrics(payload.telemetry, payload.mode || 'LIVE ARDY');
  }

  bindEvents() {
    // Toolbar window toggles
    if (this.btnToggleControls) {
      this.btnToggleControls.addEventListener('click', () => {
        const isVis = this.winControls.toggle();
        this.btnToggleControls.classList.toggle('active', isVis);
      });
    }

    if (this.btnToggleTelemetry) {
      this.btnToggleTelemetry.addEventListener('click', () => {
        const isVis = this.winTelemetry.toggle();
        this.btnToggleTelemetry.classList.toggle('active', isVis);
      });
    }

    // Camera Framing Buttons
    if (this.btnResetCamera) {
      this.btnResetCamera.addEventListener('click', () => this.stage.resetCamera());
    }
    if (this.btnFrameAvatar) {
      this.btnFrameAvatar.addEventListener('click', () => this.stage.frameAvatar());
    }
    if (this.btnFrameSkeleton) {
      this.btnFrameSkeleton.addEventListener('click', () => this.stage.frameSkeleton());
    }
    if (this.btnFrameBoth) {
      this.btnFrameBoth.addEventListener('click', () => this.stage.frameBoth());
    }

    // Generate Button
    this.btnGenerate.addEventListener('click', () => this.handleGenerate());

    // Cancel / Stop Button
    this.btnCancel.addEventListener('click', () => this.handleCancel());

    // Duration slider
    this.durationSlider.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      const frames = Math.round(val * 20); // 20 FPS canonical model rate
      this.durationVal.textContent = `${val.toFixed(1)}s (${frames}f)`;
    });

    // Loop toggle
    this.loopToggle.addEventListener('change', (e) => {
      this.timeline.setLoop(e.target.checked);
    });

    // Rig Visibility Toggles
    this.showSkeletonToggle.addEventListener('change', (e) => {
      this.skeletonRenderer.setVisible(e.target.checked);
    });

    if (this.showVrmToggle) {
      this.showVrmToggle.addEventListener('change', (e) => {
        this.stage.vrmRoot.visible = e.target.checked;
      });
    }

    // Play/Pause button
    this.btnPlayPause.addEventListener('click', () => {
      const playing = this.timeline.togglePlay();
      this.btnPlayPause.textContent = playing ? 'Pause' : 'Play';
    });

    // Restart button
    this.btnRestart.addEventListener('click', () => {
      this.timeline.restart();
    });

    // Timeline seek scrubber
    this.timelineSlider.addEventListener('input', (e) => {
      const frame = parseInt(e.target.value, 10);
      this.timeline.seekToFrame(frame);
    });

    // Playback Speed Selector
    if (this.speedSelect) {
      this.speedSelect.addEventListener('change', (e) => {
        const speed = parseFloat(e.target.value);
        this.timeline.setSpeed(speed);
      });
    }

    // VRM Avatar Loading: Single Authoritative File Input
    if (this.btnLoadVrm) {
      this.btnLoadVrm.addEventListener('click', () => {
        this.vrmFileInput.click();
      });
    }

    this.vrmFileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        this.loadVrmFile(file);
      }
      // Reset input value so reloading the same file triggers change
      e.target.value = '';
    });

    // Remove VRM button
    if (this.btnRemoveVrm) {
      this.btnRemoveVrm.addEventListener('click', () => {
        this.vrmManager.disposeCurrent();
        this.vrmInfoBadge.className = 'vrm-info-badge';
        this.vrmInfoBadge.textContent = 'No Avatar';
        this.vrmStatusText.textContent = 'No VRM avatar loaded';
        this.btnRemoveVrm.style.display = 'none';
        this.showToast('VRM avatar removed.');
      });
    }

    // Full-Stage Drag & Drop
    const dropTarget = window;
    let dragCounter = 0;

    dropTarget.addEventListener('dragenter', (e) => {
      e.preventDefault();
      dragCounter++;
      if (this.stageDropOverlay) {
        this.stageDropOverlay.classList.add('active');
      }
    });

    dropTarget.addEventListener('dragleave', (e) => {
      e.preventDefault();
      dragCounter--;
      if (dragCounter <= 0 && this.stageDropOverlay) {
        this.stageDropOverlay.classList.remove('active');
      }
    });

    dropTarget.addEventListener('dragover', (e) => {
      e.preventDefault();
    });

    dropTarget.addEventListener('drop', (e) => {
      e.preventDefault();
      dragCounter = 0;
      if (this.stageDropOverlay) {
        this.stageDropOverlay.classList.remove('active');
      }

      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
        this.loadVrmFile(e.dataTransfer.files[0]);
      }
    });

    // Global Keyboard shortcuts
    window.addEventListener('keydown', (e) => {
      if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') return;
      if (e.code === 'Space') {
        e.preventDefault();
        const playing = this.timeline.togglePlay();
        this.btnPlayPause.textContent = playing ? 'Pause' : 'Play';
      } else if (e.code === 'KeyR') {
        e.preventDefault();
        this.stage.resetCamera();
      } else if (e.code === 'KeyF') {
        e.preventDefault();
        this.stage.frameAvatar();
      }
    });
  }

  setupPresets() {
    const presets = [
      'A person waves both hands enthusiastically in the air.',
      'A person walks forward in a straight line with natural arm swings.',
      'A person walks in a wide clockwise circle.',
      'A person performs a deep knee squat and stands back up.',
    ];

    const container = document.getElementById('presetsRow');
    if (!container) return;

    container.innerHTML = '';
    presets.forEach((text, i) => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'preset-chip';
      chip.textContent = text.slice(0, 36) + '...';
      chip.title = text;
      chip.addEventListener('click', () => {
        this.promptInput.value = text;
      });
      container.appendChild(chip);
    });
  }

  async loadVrmFile(file) {
    if (!file) return;

    this.vrmInfoBadge.className = 'vrm-info-badge loading';
    this.vrmInfoBadge.textContent = 'Parsing...';
    this.vrmStatusText.textContent = `Loading ${file.name}...`;

    try {
      const result = await this.vrmManager.loadFromFile(
        file,
        (percent) => {
          if (percent !== null) {
            this.vrmInfoBadge.textContent = `${percent}%`;
          } else {
            this.vrmInfoBadge.textContent = 'Parsing...';
          }
        }
      );

      if (!result) return; // Load superseded by another file

      const { metadata, diagnostics } = result;
      this.vrmInfoBadge.className = 'vrm-info-badge loaded';
      this.vrmInfoBadge.textContent = `${metadata.version}`;
      this.vrmInfoBadge.title = `Author: ${metadata.author} | Size: ${metadata.fileSizeMB}MB | Height: ${metadata.heightMeters}m | Bones: ${diagnostics.boneCount}`;
      this.vrmStatusText.textContent = `${metadata.name} (${metadata.heightMeters}m)`;

      if (this.btnRemoveVrm) {
        this.btnRemoveVrm.style.display = 'inline-flex';
      }

      this.showToast(`Loaded ${metadata.name} (${metadata.version})`);

      // If motion payload is currently loaded, bind it to new avatar immediately
      if (this.currentMotionPayload?.vrm) {
        this.vrmManager.setMotionData(this.currentMotionPayload.vrm);
        this.vrmManager.updateFrame(this.timeline.currentFrame);
      }
    } catch (err) {
      console.error('VRM Load Failure:', err);
      this.vrmInfoBadge.className = 'vrm-info-badge error';
      this.vrmInfoBadge.textContent = 'Load Error';
      this.vrmStatusText.textContent = err.message || 'Failed to load VRM';
      this.showToast(`VRM Error: ${err.message}`);
    }
  }

  async handleGenerate() {
    const prompt = this.promptInput.value.trim();
    if (!prompt) {
      this.showToast('Please enter a motion conditioning prompt.');
      return;
    }

    const duration = parseFloat(this.durationSlider.value);
    const seed = this.seedInput.value.trim() ? parseInt(this.seedInput.value, 10) : null;

    this.setGeneratingUI(true);
    this.telemetry.setStatus('Submitting job...');

    try {
      const { job_id } = await this.api.createGeneration(prompt, duration, seed);
      this.activeJobId = job_id;
      this.telemetry.setStatus(`Job ${job_id} queued`);

      // Subscribe to WebSocket events for progress streaming
      this.activeWebSocket = this.api.subscribeJobEvents(
        job_id,
        (event) => this.handleJobEvent(event),
        (err) => {
          console.warn('WebSocket stream error, falling back to polling:', err);
          this.pollJobStatus(job_id);
        },
        () => {
          this.setGeneratingUI(false);
          this.activeJobId = null;
        }
      );
    } catch (e) {
      this.showToast(e.message || 'Failed to submit generation job.');
      this.setGeneratingUI(false);
      this.telemetry.setStatus('Error');
    }
  }

  handleJobEvent(event) {
    if (!event) return;

    if (event.status === 'processing') {
      const step = event.progress_step || 'denoiser';
      this.telemetry.setStatus(`Generating (${step})...`);
    } else if (event.status === 'completed') {
      this.telemetry.setStatus('Complete');
      if (event.result) {
        this.applyMotionPayload(event.result);
      }
    } else if (event.status === 'failed') {
      this.telemetry.setStatus('Failed');
      this.showToast(event.error_message || 'Motion generation failed.');
    } else if (event.status === 'cancelled') {
      this.telemetry.setStatus('Cancelled');
      this.showToast('Generation job was cancelled.');
    }
  }

  async pollJobStatus(jobId) {
    const pollInterval = setInterval(async () => {
      if (this.activeJobId !== jobId) {
        clearInterval(pollInterval);
        return;
      }

      try {
        const job = await this.api.getJobStatus(jobId);
        this.handleJobEvent(job);

        if (job.status === 'completed' || job.status === 'failed' || job.status === 'cancelled') {
          clearInterval(pollInterval);
          this.setGeneratingUI(false);
          this.activeJobId = null;
        }
      } catch (e) {
        clearInterval(pollInterval);
        this.setGeneratingUI(false);
        this.activeJobId = null;
      }
    }, 500);
  }

  async handleCancel() {
    if (!this.activeJobId) return;
    try {
      await this.api.cancelJob(this.activeJobId);
      this.telemetry.setStatus('Cancelling...');
    } catch (e) {
      console.warn('Cancel request error:', e);
    }
  }

  setGeneratingUI(isGenerating) {
    this.btnGenerate.disabled = isGenerating;
    this.btnCancel.disabled = !isGenerating;
    if (isGenerating) {
      this.btnGenerate.innerHTML = `<span class="spinner"></span><span>Generating...</span>`;
    } else {
      this.btnGenerate.innerHTML = `<span>Generate Motion</span>`;
    }
  }

  updateTimelineUI(frame, time, totalFrames, duration) {
    this.timelineSlider.max = Math.max(0, totalFrames - 1);
    this.timelineSlider.value = frame;
    this.timelineLabel.textContent = `Frame ${frame + 1} / ${totalFrames} (${time.toFixed(2)}s / ${duration.toFixed(2)}s)`;
  }

  showToast(message) {
    if (!this.toastBanner) return;
    this.toastBanner.textContent = message;
    this.toastBanner.style.display = 'flex';
    clearTimeout(this.toastTimeout);
    this.toastTimeout = setTimeout(() => {
      this.toastBanner.style.display = 'none';
    }, 4500);
  }

  loop() {
    requestAnimationFrame((t) => this.loop(t));

    const delta = this.clock.getDelta();

    // Advance shared timeline
    this.timeline.update(delta);

    // Update rigs synchronously
    const currentFrame = this.timeline.currentFrame;
    this.skeletonRenderer.updateFrame(currentFrame);
    this.vrmManager.updateFrame(currentFrame, delta);

    // Render single shared scene once per frame
    this.stage.render();

    // Live render FPS tracking
    this.telemetry.recordRenderFrame();
  }
}

// Instantiate application on DOM ready
window.addEventListener('DOMContentLoaded', () => {
  window.app = new App();
});
