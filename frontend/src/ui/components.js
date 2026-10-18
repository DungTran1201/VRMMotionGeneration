/**
 * UI components, HUD updates, bone checklist, and notification toasts.
 */

export class UIController {
  constructor() {
    this.toastEl = document.getElementById('notification-toast');
    this.toastMsgEl = document.getElementById('toast-message');
    this.toastTimer = null;

    this.boneListEl = document.getElementById('bone-list');
    this.boneCountBadge = document.getElementById('bone-count-badge');

    this.modeBadge = document.getElementById('mode-badge');
    this.modeBadgeText = document.getElementById('mode-badge-text');

    this.avatarBadge = document.getElementById('avatar-badge');
    this.avatarBadgeText = document.getElementById('avatar-badge-text');

    this.statSource = document.getElementById('stat-source');
    this.statFps = document.getElementById('stat-fps');
    this.statDuration = document.getElementById('stat-duration');
    this.statFrames = document.getElementById('stat-frames');

    this.statRootPos = document.getElementById('stat-root-pos');
    this.statRootRot = document.getElementById('stat-root-rot');

    this.statContactLeft = document.getElementById('stat-contact-left');
    this.statContactRight = document.getElementById('stat-contact-right');

    this.currentTimeText = document.getElementById('current-time-text');
    this.totalTimeText = document.getElementById('total-time-text');
    this.timeScrubber = document.getElementById('time-scrubber');

    this.iconPlay = document.getElementById('icon-play');
    this.iconPause = document.getElementById('icon-pause');
  }

  showToast(message, type = 'info', duration = 4000) {
    if (this.toastTimer) clearTimeout(this.toastTimer);

    this.toastEl.className = `glass-panel show ${type}`;
    this.toastMsgEl.textContent = message;

    this.toastTimer = setTimeout(() => {
      this.toastEl.classList.remove('show');
    }, duration);
  }

  setMode(mode, details = '') {
    if (mode === 'fixture') {
      this.modeBadge.className = 'badge fixture-mode';
      this.modeBadgeText.textContent = 'MODE A: FIXTURE (OFFLINE)';
    } else if (mode === 'real') {
      this.modeBadge.className = 'badge real-mode';
      this.modeBadgeText.textContent = 'MODE B: REAL INFERENCE';
    } else {
      this.modeBadge.className = 'badge';
      this.modeBadgeText.textContent = details || 'OFFLINE';
    }
  }

  setAvatarStatus(avatarName, isVrm = false) {
    this.avatarBadgeText.textContent = isVrm ? `VRM: ${avatarName}` : 'PROCEDURAL HUMANOID RIG';
  }

  updatePlaybackControls(isPlaying, currentTime, duration) {
    if (isPlaying) {
      this.iconPlay.style.display = 'none';
      this.iconPause.style.display = 'block';
    } else {
      this.iconPlay.style.display = 'block';
      this.iconPause.style.display = 'none';
    }

    this.currentTimeText.textContent = `${currentTime.toFixed(2)}s`;
    this.totalTimeText.textContent = `${duration.toFixed(2)}s`;

    if (duration > 0) {
      this.timeScrubber.value = currentTime / duration;
    }
  }

  updateMotionMetadata(meta) {
    if (this.statSource) this.statSource.textContent = meta.source || 'fixture';
    if (this.statFps) this.statFps.textContent = `${meta.fps.toFixed(1)} fps`;
    if (this.statDuration) this.statDuration.textContent = `${meta.duration.toFixed(2)}s`;
    if (this.statFrames) this.statFrames.textContent = `${meta.num_frames} frames`;
  }

  updateFrameDiagnostics(frameData) {
    if (!frameData) return;

    if (frameData.rootPos) {
      const p = frameData.rootPos;
      this.statRootPos.textContent = `${p[0].toFixed(2)}, ${p[1].toFixed(2)}, ${p[2].toFixed(2)}`;
    }

    if (frameData.rootRot) {
      const q = frameData.rootRot;
      this.statRootRot.textContent = `${q[0].toFixed(2)}, ${q[1].toFixed(2)}, ${q[2].toFixed(2)}, ${q[3].toFixed(2)}`;
    }

    if (frameData.contacts) {
      const l = frameData.contacts.leftFoot;
      const r = frameData.contacts.rightFoot;

      this.statContactLeft.textContent = l ? 'STANCE' : 'SWING';
      this.statContactLeft.style.color = l ? 'var(--emerald)' : 'var(--text-dim)';

      this.statContactRight.textContent = r ? 'STANCE' : 'SWING';
      this.statContactRight.style.color = r ? 'var(--emerald)' : 'var(--text-dim)';
    }
  }

  updateBonesList(coverage) {
    this.boneCountBadge.textContent = `${coverage.presentCount}/${coverage.total}`;
    this.boneListEl.innerHTML = '';

    for (const [boneName, isPresent] of Object.entries(coverage.bones)) {
      const item = document.createElement('div');
      item.className = `bone-item ${isPresent ? 'present' : 'missing'}`;

      const nameSpan = document.createElement('span');
      nameSpan.textContent = boneName;

      const statusSpan = document.createElement('span');
      statusSpan.textContent = isPresent ? '✓ OK' : '✕ MISSING';

      item.appendChild(nameSpan);
      item.appendChild(statusSpan);
      this.boneListEl.appendChild(item);
    }
  }
}
