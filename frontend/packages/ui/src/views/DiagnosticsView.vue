<script setup lang="ts">
import { onMounted } from "vue";
import { useAppStore } from "@vrm/app-core";
import StateView from "../components/StateView.vue";
import StatusBadge from "../components/StatusBadge.vue";

const store = useAppStore();

onMounted(() => {
  if (!store.state.diagnostics) {
    store.loadDiagnostics();
  }
});
</script>

<template>
  <div class="view-container">
    <div class="section-header">
      <div class="header-main">
        <div>
          <h2>System Diagnostics & Runtime State</h2>
          <p>Verified hardware, platform capabilities, and IPC connectivity.</p>
        </div>
        <button
          id="refresh-diagnostics-btn"
          class="refresh-btn"
          :disabled="store.state.isLoading"
          @click="store.loadDiagnostics()"
        >
          🔄 Refresh
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <StateView
      v-if="store.state.isLoading"
      type="loading"
      title="Probing Runtime Subsystems"
      description="Querying system capabilities and inter-process communication channels..."
    />

    <!-- Error State -->
    <StateView
      v-else-if="store.state.errorMessage"
      type="error"
      title="Diagnostics Probe Failed"
      :description="store.state.errorMessage"
      action-label="Retry Diagnostics Probe"
      @action="store.loadDiagnostics()"
    />

    <!-- Diagnostics Display -->
    <div v-else-if="store.state.diagnostics" class="diagnostics-content">
      <div class="grid-stats">
        <div class="stat-card">
          <span class="stat-label">Active Platform</span>
          <div class="stat-value-row">
            <span class="stat-value">{{
              store.state.diagnostics.platform.toUpperCase()
            }}</span>
            <StatusBadge
              :status="
                store.state.diagnostics.platform === 'electron'
                  ? 'active'
                  : 'ready'
              "
              :label="
                store.state.diagnostics.platform === 'electron'
                  ? 'Native Shell'
                  : 'Browser Client'
              "
            />
          </div>
        </div>

        <div class="stat-card">
          <span class="stat-label">App Version</span>
          <span class="stat-value mono"
            >v{{ store.state.diagnostics.appVersion }}</span
          >
        </div>

        <div class="stat-card">
          <span class="stat-label">Build Environment</span>
          <span class="stat-value mono">{{
            store.state.diagnostics.environment
          }}</span>
        </div>

        <div class="stat-card">
          <span class="stat-label">Telemetry Timestamp</span>
          <span class="stat-value mono text-sm">{{
            store.state.diagnostics.timestamp
          }}</span>
        </div>
      </div>

      <div class="details-section">
        <h3>Platform Capability Flags</h3>
        <div class="capability-grid">
          <div class="cap-card">
            <span>Desktop Integration</span>
            <StatusBadge
              :status="
                store.state.diagnostics.capabilities.desktopIntegration
                  ? 'active'
                  : 'offline'
              "
              :label="
                store.state.diagnostics.capabilities.desktopIntegration
                  ? 'Supported'
                  : 'Not Available'
              "
            />
          </div>
          <div class="cap-card">
            <span>Local File System Access</span>
            <StatusBadge
              :status="
                store.state.diagnostics.capabilities.fileSystemAccess
                  ? 'active'
                  : 'offline'
              "
              :label="
                store.state.diagnostics.capabilities.fileSystemAccess
                  ? 'Available'
                  : 'Sandboxed'
              "
            />
          </div>
          <div class="cap-card">
            <span>Native Window Menus</span>
            <StatusBadge
              :status="
                store.state.diagnostics.capabilities.nativeMenus
                  ? 'active'
                  : 'offline'
              "
              :label="
                store.state.diagnostics.capabilities.nativeMenus
                  ? 'Enabled'
                  : 'Browser Managed'
              "
            />
          </div>
        </div>
      </div>

      <div v-if="store.state.diagnostics.os" class="details-section">
        <h3>Host Operating System</h3>
        <div class="os-info-box">
          <div class="info-item">
            <span class="info-k">OS Platform:</span>
            <span class="info-v mono">{{
              store.state.diagnostics.os.platform
            }}</span>
          </div>
          <div class="info-item">
            <span class="info-k">Architecture:</span>
            <span class="info-v mono">{{
              store.state.diagnostics.os.arch
            }}</span>
          </div>
          <div class="info-item">
            <span class="info-k">Release / Kernel:</span>
            <span class="info-v mono">{{
              store.state.diagnostics.os.release
            }}</span>
          </div>
        </div>
      </div>

      <div class="details-section">
        <h3>Inter-Process Communication (IPC) Health</h3>
        <div class="ipc-card">
          <p>
            Verify round-trip latency and message deserialization across process
            boundaries using allowlisted IPC ping.
          </p>
          <div class="ipc-actions">
            <button
              id="ipc-ping-btn"
              class="action-btn"
              @click="store.executePing()"
            >
              Test IPC Ping
            </button>
            <span
              v-if="store.state.pingResult"
              id="ipc-ping-result"
              class="ping-output mono"
            >
              Result: {{ store.state.pingResult }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.view-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 24px;
}

.section-header {
  margin-bottom: 32px;
}

.header-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-header h2 {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.section-header p {
  color: var(--text-secondary);
}

.refresh-btn {
  padding: 8px 16px;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.grid-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-value-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.mono {
  font-family: var(--font-family-mono);
}

.text-sm {
  font-size: 0.85rem;
}

.details-section {
  margin-bottom: 28px;
}

.details-section h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.capability-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.cap-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 14px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.os-info-box {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.info-k {
  color: var(--text-muted);
}

.info-v {
  color: var(--text-primary);
}

.ipc-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ipc-card p {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.ipc-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-btn {
  padding: 8px 18px;
  background: var(--accent-cyan);
  color: #000;
  font-weight: 600;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background: #22d3ee;
  box-shadow: 0 0 10px var(--accent-cyan-glow);
}

.ping-output {
  color: var(--accent-success);
  font-size: 0.9rem;
}
</style>
