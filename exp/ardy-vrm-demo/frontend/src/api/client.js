/**
 * API client for interacting with ARDY VRM Demo backend.
 */

export class ApiClient {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
  }

  async getHealth() {
    const res = await fetch(`${this.baseUrl}/api/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return await res.json();
  }

  async getModels() {
    const res = await fetch(`${this.baseUrl}/api/models`);
    if (!res.ok) throw new Error(`Fetch models failed: ${res.statusText}`);
    return await res.json();
  }

  async getDefaultSample() {
    const res = await fetch(`${this.baseUrl}/api/samples/default`);
    if (!res.ok) throw new Error(`Fetch default sample failed: ${res.statusText}`);
    return await res.json();
  }

  async createGeneration(prompt, durationSeconds, seed = null) {
    const payload = {
      prompt,
      duration_seconds: parseFloat(durationSeconds),
    };
    if (seed !== null && seed !== undefined && seed !== '') {
      payload.seed = parseInt(seed, 10);
    }

    const res = await fetch(`${this.baseUrl}/api/generations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Generation request failed (${res.status})`);
    }

    return await res.json(); // { job_id, status }
  }

  async getJobStatus(jobId) {
    const res = await fetch(`${this.baseUrl}/api/generations/${jobId}`);
    if (!res.ok) throw new Error(`Fetch job status failed: ${res.statusText}`);
    return await res.json();
  }

  async cancelJob(jobId) {
    const res = await fetch(`${this.baseUrl}/api/generations/${jobId}/cancel`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error(`Cancel job failed: ${res.statusText}`);
    return await res.json();
  }

  subscribeJobEvents(jobId, onMessage, onError, onComplete) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/generations/${jobId}/events`;
    const socket = new WebSocket(wsUrl);

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
        if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
          if (onComplete) onComplete(data);
          socket.close();
        }
      } catch (e) {
        console.error('Error parsing WS message:', e);
      }
    };

    socket.onerror = (err) => {
      if (onError) onError(err);
    };

    return socket;
  }
}
