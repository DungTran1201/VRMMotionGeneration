/**
 * Main Application Orchestrator for MotionBricks-to-VRM Viewer.
 */

import * as THREE from 'three';
import { AvatarManager } from './avatar/vrm_manager.js';
import { AnimationPlayer } from './animation/player.js';
import { ApiClient } from './transport/api_client.js';
import { UIController } from './ui/components.js';
import { validateCanonicalMotion } from './motion/schema_validator.js';

window.addEventListener('DOMContentLoaded', async () => {
  const canvas = document.getElementById('canvas3d');
  const ui = new UIController();
  const avatar = new AvatarManager(canvas);
  const player = new AnimationPlayer(avatar);
  const api = new ApiClient();

  const clock = new THREE.Clock();

  // Avatar Callback
  avatar.onBonesUpdated = (coverage) => {
    ui.updateBonesList(coverage);
    ui.setAvatarStatus(coverage.avatarName, coverage.isUsingVrm);
  };

  avatar.onError = (err) => {
    ui.showToast(`Avatar Error: ${err.message}`, 'error', 5000);
  };

  // Animation Player Callbacks
  player.onProgress = ({ currentTime, duration, progress }) => {
    ui.updatePlaybackControls(player.isPlaying, currentTime, duration);
    ui.updateFrameDiagnostics(player.currentFrameData);
  };

  player.onStateChange = ({ isPlaying, duration }) => {
    ui.updatePlaybackControls(isPlaying, player.currentTime, duration || player.getDuration());
  };

  // 1. Initial Load: Mode A Offline Fixture
  try {
    const fixtureData = await api.getFixture();
    const validation = validateCanonicalMotion(fixtureData);

    if (validation.valid) {
      player.loadMotion(fixtureData);
      ui.updateMotionMetadata(fixtureData.metadata);
      ui.setMode('fixture');
      ui.showToast('Mode A: Loaded validated locomotion fixture', 'success', 3500);
    } else {
      ui.showToast(`Fixture Validation Warning: ${validation.errors[0]}`, 'error');
    }
  } catch (err) {
    ui.showToast(`Failed to load fixture: ${err.message}`, 'error');
  }

  // 2. Playback Button Listeners
  const btnPlayPause = document.getElementById('btn-play-pause');
  btnPlayPause.addEventListener('click', () => {
    player.togglePlayPause();
  });

  const btnRestart = document.getElementById('btn-restart');
  btnRestart.addEventListener('click', () => {
    player.restart();
  });

  const timeScrubber = document.getElementById('time-scrubber');
  timeScrubber.addEventListener('input', (e) => {
    player.seek(parseFloat(e.target.value));
  });

  const speedSelect = document.getElementById('speed-select');
  speedSelect.addEventListener('change', (e) => {
    player.setSpeed(parseFloat(e.target.value));
  });

  const btnLoopToggle = document.getElementById('btn-loop-toggle');
  let loopEnabled = true;
  btnLoopToggle.addEventListener('click', () => {
    loopEnabled = !loopEnabled;
    player.setLoop(loopEnabled);
    btnLoopToggle.textContent = `Loop: ${loopEnabled ? 'ON' : 'OFF'}`;
    btnLoopToggle.style.color = loopEnabled ? 'var(--primary)' : 'var(--text-dim)';
  });

  const btnResetCam = document.getElementById('btn-reset-cam');
  btnResetCam.addEventListener('click', () => {
    avatar.resetCamera();
  });

  // 3. User Avatar Upload
  const btnLoadVrm = document.getElementById('btn-load-vrm');
  const vrmFileInput = document.getElementById('vrm-file-input');

  btnLoadVrm.addEventListener('click', () => {
    vrmFileInput.click();
  });

  vrmFileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    ui.showToast(`Loading avatar: ${file.name}...`, 'info', 3000);
    try {
      await avatar.loadVrmFile(file);
      ui.showToast(`Avatar '${file.name}' loaded successfully!`, 'success');
      // Re-apply current pose to newly loaded VRM
      player.applyCurrentTimePose(0.016);
    } catch (err) {
      ui.showToast(`Failed to parse VRM: ${err.message}`, 'error', 6000);
    }
  });

  // 4. User Motion File Upload
  const btnLoadMotion = document.getElementById('btn-load-motion');
  const motionFileInput = document.getElementById('motion-file-input');

  btnLoadMotion.addEventListener('click', () => {
    motionFileInput.click();
  });

  motionFileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      const text = await file.text();
      const motionDoc = JSON.parse(text);
      const validation = validateCanonicalMotion(motionDoc);

      if (!validation.valid) {
        ui.showToast(`Invalid motion file: ${validation.errors[0]}`, 'error', 5000);
        return;
      }

      player.loadMotion(motionDoc);
      ui.updateMotionMetadata(motionDoc.metadata);
      ui.setMode(motionDoc.metadata.source || 'custom');
      ui.showToast(`Loaded motion: ${file.name} (${motionDoc.metadata.num_frames} frames)`, 'success');
    } catch (err) {
      ui.showToast(`Error loading motion file: ${err.message}`, 'error', 5000);
    }
  });

  // 5. Connect Backend API & Check Real Inference Status
  const btnSwitchMode = document.getElementById('btn-switch-mode');
  btnSwitchMode.addEventListener('click', async () => {
    ui.showToast('Querying Backend API status...', 'info', 2000);
    const health = await api.checkHealth();

    if (health.status === 'healthy') {
      if (health.mode_b_real_inference_ready) {
        ui.setMode('real');
        ui.showToast('Mode B: Backend Connected & Checkpoints Verified!', 'success', 4000);
      } else {
        ui.setMode('fixture', 'BACKEND CONNECTED (FIXTURE ONLY)');
        ui.showToast(`Backend online, but weights are unpulled: ${health.checkpoint_details}`, 'info', 5000);
      }
    } else {
      ui.setMode('fixture');
      ui.showToast('Backend offline. Continuing in Mode A (Offline Demo).', 'info', 4000);
    }
  });

  // 6. Animation Render Loop
  function animate() {
    requestAnimationFrame(animate);
    const delta = clock.getDelta();
    player.update(delta);
    avatar.render();
  }

  animate();
});
