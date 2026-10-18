/**
 * API Transport Client for REST and WebSocket communication.
 */

export class ApiClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.wsUrl = baseUrl.replace(/^http/, 'ws') + '/ws/motion';
    this.ws = null;
  }

  async checkHealth() {
    try {
      const res = await fetch(`${this.baseUrl}/api/health`, { method: 'GET' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      return {
        status: 'offline',
        mode_a_fixture_ready: true,
        mode_b_real_inference_ready: false,
        checkpoint_details: 'Backend service unreachable. Running in local Mode A (Offline Demo).',
        environment: {}
      };
    }
  }

  async getFixture() {
    // First try backend API
    try {
      const res = await fetch(`${this.baseUrl}/api/motion/fixture`);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      // Backend offline, fallback to public folder
    }

    // Fallback to static public folder
    const fallbackRes = await fetch('/sample_motion.json');
    if (!fallbackRes.ok) {
      throw new Error('Failed to load sample motion fixture.');
    }
    return await fallbackRes.json();
  }

  async validateRemote(motionPayload) {
    const res = await fetch(`${this.baseUrl}/api/motion/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: json.stringify({ motion: motionPayload })
    });
    return await res.json();
  }

  async triggerInference(command = 'walk', duration = 2.0) {
    const res = await fetch(`${this.baseUrl}/api/inference/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, duration_seconds: duration })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail?.reason || data.detail || 'Inference failed');
    }
    return data;
  }

  connectStreaming({ onFrame, onHeader, onEnd, onError }) {
    if (this.ws) {
      this.ws.close();
    }

    try {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = () => {
        // Request fixture stream
        this.ws.send(JSON.stringify({ command: 'stream_fixture', loop: true, speed: 1.0 }));
      };

      this.ws.onmessage = (event) => {
        try {
          const packet = JSON.parse(event.data);
          if (packet.type === 'motion_frame' && onFrame) {
            onFrame(packet.frame);
          } else if (packet.type === 'motion_header' && onHeader) {
            onHeader(packet);
          } else if (packet.type === 'motion_ended' && onEnd) {
            onEnd();
          } else if (packet.type === 'error' && onError) {
            onError(new Error(packet.message));
          }
        } catch (e) {
          if (onError) onError(e);
        }
      };

      this.ws.onerror = (err) => {
        if (onError) onError(err);
      };

      this.ws.onclose = () => {
        this.ws = null;
      };
    } catch (e) {
      if (onError) onError(e);
    }
  }

  disconnectStreaming() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
