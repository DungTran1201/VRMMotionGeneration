/**
 * Telemetry HUD Manager.
 * Formats and updates generation metrics, hardware state, and live rendering FPS.
 * Strict adherence to evidence-based metrics without prefilled or fabricated numbers.
 */

export class TelemetryHud {
  constructor() {
    this.fpsCounter = {
      frames: 0,
      lastTime: performance.now(),
      currentFps: 0,
    };

    // DOM Elements
    this.elModeBadge = document.getElementById('modeBadge');
    this.elSystemPill = document.getElementById('systemPill');
    this.elStatus = document.getElementById('metricStatus');
    this.elModel = document.getElementById('metricModel');
    this.elDuration = document.getElementById('metricDuration');
    this.elGenTime = document.getElementById('metricGenTime');
    this.elEffectiveFps = document.getElementById('metricEffectiveFps');
    this.elRtf = document.getElementById('metricRtf');
    this.elLatency = document.getElementById('metricLatency');
    this.elVram = document.getElementById('metricVram');
    this.elRenderFps = document.getElementById('metricRenderFps');

    this.resetToIdle();
  }

  resetToIdle() {
    if (this.elStatus) this.elStatus.textContent = 'Idle';
    if (this.elDuration) this.elDuration.textContent = '—';
    if (this.elGenTime) this.elGenTime.textContent = '—';
    if (this.elEffectiveFps) this.elEffectiveFps.textContent = '—';
    if (this.elRtf) this.elRtf.textContent = '—';
    if (this.elLatency) this.elLatency.textContent = '—';
    if (this.elVram) this.elVram.textContent = 'N/A';
  }

  setMode(mode) {
    if (!this.elModeBadge) return;
    const cleanMode = (mode || 'FIXTURE PREVIEW').toUpperCase();
    this.elModeBadge.innerHTML = `<span class="pulse-dot"></span><span>${cleanMode}</span>`;

    this.elModeBadge.className = 'mode-badge';
    if (cleanMode.includes('FIXTURE')) {
      this.elModeBadge.classList.add('fixture');
    } else if (cleanMode.includes('BATCH')) {
      this.elModeBadge.classList.add('batch');
    } else if (cleanMode.includes('LIVE')) {
      this.elModeBadge.classList.add('live');
    } else if (cleanMode.includes('UNAVAILABLE') || cleanMode.includes('ERROR') || cleanMode.includes('OFFLINE')) {
      this.elModeBadge.classList.add('error');
    }
  }

  setSystemInfo(health) {
    if (!this.elSystemPill) return;
    if (health.cuda_available && health.gpu_name) {
      const vram = health.vram_free_mb ? ` | ${health.vram_free_mb} MB Free` : '';
      this.elSystemPill.textContent = `${health.gpu_name}${vram}`;
    } else {
      this.elSystemPill.textContent = 'CPU Mode (Deterministic Fixture)';
    }
  }

  updateMetrics(telemetry, fallbackMode = null) {
    if (!telemetry) return;

    if (this.elStatus) this.elStatus.textContent = 'Playing';
    if (this.elModel) this.elModel.textContent = telemetry.model_name || 'ARDY-Core8';

    if (this.elDuration) {
      const req = telemetry.requested_duration ? `${telemetry.requested_duration.toFixed(2)}s` : '—';
      const act = telemetry.actual_duration ? `${telemetry.actual_duration.toFixed(2)}s` : '—';
      const frames = telemetry.total_frames ? ` (${telemetry.total_frames}f)` : '';
      this.elDuration.textContent = `${req} / ${act}${frames}`;
    }

    if (this.elGenTime) {
      const ms = telemetry.generation_time_seconds
        ? `${(telemetry.generation_time_seconds * 1000).toFixed(0)} ms`
        : '—';
      this.elGenTime.textContent = ms;
    }

    if (this.elEffectiveFps) {
      const fps = telemetry.effective_generated_fps
        ? `${telemetry.effective_generated_fps.toFixed(1)} FPS`
        : '—';
      this.elEffectiveFps.textContent = fps;
    }

    if (this.elRtf) {
      if (telemetry.real_time_factor !== undefined && telemetry.real_time_factor !== null) {
        const rtf = telemetry.real_time_factor.toFixed(2);
        const desc = telemetry.real_time_factor < 1.0 ? ' (<1.0x Realtime)' : ' (>=1.0x Realtime)';
        this.elRtf.textContent = `${rtf}${desc}`;
      } else {
        this.elRtf.textContent = '—';
      }
    }

    if (this.elLatency) {
      const lat = telemetry.end_to_end_latency_ms
        ? `${telemetry.end_to_end_latency_ms.toFixed(0)} ms`
        : '—';
      this.elLatency.textContent = lat;
    }

    if (this.elVram) {
      const vram = telemetry.peak_vram_mb
        ? `${telemetry.peak_vram_mb.toFixed(1)} MB`
        : 'N/A';
      this.elVram.textContent = vram;
    }

    if (fallbackMode) {
      this.setMode(fallbackMode);
    }
  }

  setStatus(text) {
    if (this.elStatus) this.elStatus.textContent = text;
  }

  recordRenderFrame() {
    this.fpsCounter.frames++;
    const now = performance.now();
    const elapsed = now - this.fpsCounter.lastTime;

    if (elapsed >= 500) {
      this.fpsCounter.currentFps = Math.round((this.fpsCounter.frames * 1000) / elapsed);
      this.fpsCounter.frames = 0;
      this.fpsCounter.lastTime = now;

      if (this.elRenderFps) {
        this.elRenderFps.textContent = `${this.fpsCounter.currentFps} FPS`;
      }
    }
  }
}
