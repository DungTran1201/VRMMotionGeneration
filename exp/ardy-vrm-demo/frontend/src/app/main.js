/**
 * Main application coordinator for ARDY -> VRM Motion Lab.
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { VRMLoaderPlugin } from '@pixiv/three-vrm';

import { ApiClient } from '../api/client.js';
import { ViewerStage } from '../scene/viewer_stage.js';
import { SkeletonRenderer } from '../skeleton/skeleton_renderer.js';
import { VrmManager } from '../vrm/vrm_manager.js';
import { TimelineController } from '../animation/timeline_controller.js';
import { TelemetryHud } from '../telemetry/telemetry_hud.js';

class App {
  constructor() {
    this.api = new ApiClient();
    this.telemetry = new TelemetryHud();
    this.timeline = new TimelineController();

    // DOM References
    this.skeletonCanvas = document.getElementById('skeletonCanvas');
    this.vrmCanvas = document.getElementById('vrmCanvas');
    this.promptInput = document.getElementById('promptInput');
    this.durationSlider = document.getElementById('durationSlider');
    this.durationVal = document.getElementById('durationVal');
    this.seedInput = document.getElementById('seedInput');
    this.loopToggle = document.getElementById('loopToggle');
    this.showSkeletonToggle = document.getElementById('showSkeletonToggle');
    this.btnGenerate = document.getElementById('btnGenerate');
    this.btnCancel = document.getElementById('btnCancel');
    this.btnPlayPause = document.getElementById('btnPlayPause');
    this.btnRestart = document.getElementById('btnRestart');
    this.timelineSlider = document.getElementById('timelineSlider');
    this.timelineLabel = document.getElementById('timelineLabel');
    this.vrmFileInput = document.getElementById('vrmFileInput');
    this.vrmEmptyState = document.getElementById('vrmEmptyState');
    this.vrmInfoBadge = document.getElementById('vrmInfoBadge');
    this.btnResetCamera = document.getElementById('btnResetCamera');
    this.toastBanner = document.getElementById('toastBanner');

    // Setup 3D Scene & Renderers
    this.stage = new ViewerStage(THREE, OrbitControls, this.skeletonCanvas, this.vrmCanvas);
    this.skeletonRenderer = new SkeletonRenderer(THREE, this.stage.skeleton.scene);
    this.vrmManager = new VrmManager(THREE, this.stage.vrm.scene, GLTFLoader, VRMLoaderPlugin);

    this.activeJobId = null;
    this.activeWebSocket = null;
    this.clock = new THREE.Clock();

    this.init();
  }

  async init() {
    this.bindEvents();
    this.setupPresets();

    // Timeline tick callback
    this.timeline.onFrameUpdate((frame, time, totalFrames, duration) => {
      this.updateTimelineUI(frame, time, totalFrames, duration);
    });

    // Check backend health & system specs
    try {
      const health = await this.api.getHealth();
      this.telemetry.setSystemInfo(health);
      this.telemetry.setMode(health.mode);
    } catch (e) {
      console.warn('Backend offline or health error:', e);
      this.telemetry.setMode('MODEL UNAVAILABLE');
      this.showToast('Backend server is not responding. Showing offline mode.');
    }

    // Load initial default sample
    try {
      this.telemetry.setStatus('Loading default sample...');
      const sample = await this.api.getDefaultSample();
      this.applyMotionPayload(sample);
      this.telemetry.setStatus('Playing');
    } catch (e) {
      console.warn('Could not load default sample:', e);
      this.telemetry.setStatus('Idle');
    }

    // Start render loop
    requestAnimationFrame((t) => this.loop(t));
  }

  applyMotionPayload(payload) {
    if (!payload) return;

    if (payload.prompt && this.promptInput && !this.promptInput.value) {
      this.promptInput.value = payload.prompt;
    }

    // Load skeleton data
    if (payload.skeleton) {
      this.skeletonRenderer.loadSkeletonData(payload.skeleton);
    }

    // Feed VRM motion data
    if (payload.vrm) {
      this.vrmManager.setMotionData(payload.vrm);
    }

    // Update timeline sequence
    this.timeline.setMotionSequence(
      payload.total_frames,
      payload.fps,
      payload.duration_seconds
    );

    // Update telemetry HUD
    this.telemetry.updateMetrics(payload.telemetry, payload.mode || 'LIVE ARDY');
  }

  bindEvents() {
    // Generate Button
    this.btnGenerate.addEventListener('click', () => this.handleGenerate());

    // Cancel Button
    this.btnCancel.addEventListener('click', () => this.handleCancel());

    // Duration slider
    this.durationSlider.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      const frames = Math.round(val * 20);
      this.durationVal.textContent = `${val.toFixed(1)}s (${frames}f)`;
    });

    // Loop toggle
    this.loopToggle.addEventListener('change', (e) => {
      this.timeline.setLoop(e.target.checked);
    });

    // Skeleton Visibility Toggle
    this.showSkeletonToggle.addEventListener('change', (e) => {
      this.skeletonRenderer.setVisible(e.target.checked);
    });

    // Play/Pause button
    this.btnPlayPause.addEventListener('click', () => {
      const playing = this.timeline.togglePlay();
      this.btnPlayPause.textContent = playing ? 'Pause' : 'Play';
    });

    // Restart button
    this.btnRestart.addEventListener('click', () => {
      this.timeline.restart();
    });

    // Timeline seek
    this.timelineSlider.addEventListener('input', (e) => {
      const frame = parseInt(e.target.value, 10);
      this.timeline.seekToFrame(frame);
    });

    // Camera reset
    if (this.btnResetCamera) {
      this.btnResetCamera.addEventListener('click', () => {
        this.stage.resetCamera();
      });
    }

    // VRM File Input
    this.vrmFileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) this.loadVrmFile(file);
    });

    // Drag and Drop on VRM viewport
    const vrmContainer = this.vrmCanvas.parentElement;
    vrmContainer.addEventListener('dragover', (e) => {
      e.preventDefault();
      vrmContainer.style.outline = '2px dashed #06b6d4';
    });
    vrmContainer.addEventListener('dragleave', () => {
      vrmContainer.style.outline = 'none';
    });
    vrmContainer.addEventListener('drop', (e) => {
      e.preventDefault();
      vrmContainer.style.outline = 'none';
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        this.loadVrmFile(e.dataTransfer.files[0]);
      }
    });

    // Keyboard shortcuts
    window.addEventListener('keydown', (e) => {
      if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') return;
      if (e.code === 'Space') {
        e.preventDefault();
        const playing = this.timeline.togglePlay();
        this.btnPlayPause.textContent = playing ? 'Pause' : 'Play';
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
      const chip = document.createElement('div');
      chip.className = 'preset-chip';
      chip.textContent = `Preset ${i + 1}: ${text.slice(0, 32)}...`;
      chip.title = text;
      chip.addEventListener('click', () => {
        this.promptInput.value = text;
      });
      container.appendChild(chip);
    });
  }

  async handleGenerate() {
    const prompt = this.promptInput.value.trim();
    if (!prompt) {
      this.showToast('Please enter a motion prompt.');
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

      // Subscribe to WebSocket events for real-time streaming progress
      this.activeWebSocket = this.api.subscribeJobEvents(
        job_id,
        (event) => {
          this.handleJobEvent(event);
        },
        (err) => {
          console.warn('WS error, falling back to polling:', err);
          this.pollJobStatus(job_id);
        },
        (finalEvent) => {
          this.setGeneratingUI(false);
          this.activeJobId = null;
        }
      );
    } catch (e) {
      this.showToast(e.message || 'Failed to submit generation.');
      this.setGeneratingUI(false);
      this.telemetry.setStatus('Error');
    }
  }

  handleJobEvent(event) {
    if (!event) return;

    if (event.status === 'processing') {
      const step = event.progress_step || 'diffusion denoiser';
      this.telemetry.setStatus(`Generating (${step})...`);
    } else if (event.status === 'completed') {
      this.telemetry.setStatus('Complete');
      if (event.result) {
        this.applyMotionPayload(event.result);
      }
    } else if (event.status === 'failed') {
      this.telemetry.setStatus('Failed');
      this.showToast(event.error_message || 'Generation failed.');
    } else if (event.status === 'cancelled') {
      this.telemetry.setStatus('Cancelled');
      this.showToast('Job was cancelled.');
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

  async loadVrmFile(file) {
    this.vrmEmptyState.classList.add('hidden');
    this.vrmInfoBadge.style.display = 'inline-block';
    this.vrmInfoBadge.textContent = `Parsing ${file.name}...`;

    this.vrmManager.loadFromFile(
      file,
      (percent) => {
        this.vrmInfoBadge.textContent = `Loading ${percent}%...`;
      },
      (meta) => {
        this.vrmInfoBadge.textContent = `Avatar: ${meta.name} (${meta.fileSizeMB} MB)`;
        this.showToast(`Loaded VRM: ${meta.name}`);
      },
      (err) => {
        this.vrmEmptyState.classList.remove('hidden');
        this.vrmInfoBadge.style.display = 'none';
        this.showToast(`VRM Error: ${err.message}`);
      }
    );
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

    // Advance timeline
    this.timeline.update(delta);

    // Update 3D rigs
    const currentFrame = this.timeline.currentFrame;
    this.skeletonRenderer.updateFrame(currentFrame);
    this.vrmManager.updateFrame(currentFrame, delta);

    // Render scenes
    this.stage.render();

    // Record FPS
    this.telemetry.recordRenderFrame();
  }
}

// Instantiate on DOM load
window.addEventListener('DOMContentLoaded', () => {
  window.app = new App();
});
