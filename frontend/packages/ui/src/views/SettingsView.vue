<script setup lang="ts">
import { useAppStore } from "@vrm/app-core";

const store = useAppStore();

const themes = [
  { id: "dark", label: "Dark Mode (Default)" },
  { id: "light", label: "Light Mode" },
  { id: "system", label: "Follow System" },
] as const;

const logLevels = ["debug", "info", "warn", "error"] as const;
</script>

<template>
  <div class="view-container">
    <div class="section-header">
      <h2>Application Settings</h2>
      <p>
        Configure theme appearance, logging verbosity, and runtime behavior.
      </p>
    </div>

    <div class="settings-group">
      <div class="setting-row">
        <div class="setting-info">
          <label class="setting-label">Interface Theme</label>
          <span class="setting-desc"
            >Select visual color theme for the shell layout</span
          >
        </div>
        <div class="setting-control">
          <div class="radio-pill-group">
            <button
              v-for="t in themes"
              :key="t.id"
              :id="`theme-btn-${t.id}`"
              :class="[
                'pill-btn',
                { active: store.state.settings.theme === t.id },
              ]"
              @click="store.updateSettings({ theme: t.id })"
            >
              {{ t.label }}
            </button>
          </div>
        </div>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <label class="setting-label">Log Level</label>
          <span class="setting-desc"
            >Verbosity threshold for console and diagnostic outputs</span
          >
        </div>
        <div class="setting-control">
          <select
            id="log-level-select"
            class="custom-select"
            :value="store.state.settings.logLevel"
            @change="
              (e) =>
                store.updateSettings({
                  logLevel: (e.target as HTMLSelectElement).value as any,
                })
            "
          >
            <option v-for="lvl in logLevels" :key="lvl" :value="lvl">
              {{ lvl.toUpperCase() }}
            </option>
          </select>
        </div>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <label class="setting-label">Anonymous Crash Telemetry</label>
          <span class="setting-desc"
            >Disabled by default per strict privacy baseline</span
          >
        </div>
        <div class="setting-control">
          <label class="switch">
            <input
              id="telemetry-toggle-checkbox"
              type="checkbox"
              :checked="store.state.settings.telemetryEnabled"
              @change="
                (e) =>
                  store.updateSettings({
                    telemetryEnabled: (e.target as HTMLInputElement).checked,
                  })
              "
            />
            <span class="slider"></span>
          </label>
        </div>
      </div>
    </div>

    <div class="info-card">
      <h4>Runtime Environment Details</h4>
      <p>
        Running on
        <strong>{{ store.platform.value.toUpperCase() }}</strong> runtime.
        <span v-if="store.platform.value === 'electron'">
          Operating inside native desktop shell with secure IPC bridge.
        </span>
        <span v-else>
          Operating inside browser sandbox with capability fallbacks.
        </span>
      </p>
    </div>
  </div>
</template>

<style scoped>
.view-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 24px;
}

.section-header {
  margin-bottom: 32px;
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

.settings-group {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 8px 24px;
  margin-bottom: 32px;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0;
  border-bottom: 1px solid var(--border-subtle);
}

.setting-row:last-child {
  border-bottom: none;
}

.setting-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.setting-label {
  font-weight: 600;
  color: var(--text-primary);
}

.setting-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.radio-pill-group {
  display: flex;
  gap: 6px;
  background: var(--bg-primary);
  padding: 4px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.pill-btn {
  padding: 6px 12px;
  font-size: 0.8rem;
  font-weight: 500;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.pill-btn.active {
  background: var(--accent-cyan);
  color: #000;
  font-weight: 600;
}

.custom-select {
  padding: 8px 16px;
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  font-family: var(--font-family-mono);
  font-size: 0.85rem;
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-tertiary);
  transition: 0.3s;
  border-radius: 24px;
  border: 1px solid var(--border-subtle);
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 3px;
  bottom: 3px;
  background-color: var(--text-primary);
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--accent-cyan);
}

input:checked + .slider:before {
  transform: translateX(20px);
  background-color: #000;
}

.info-card {
  padding: 20px;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.info-card h4 {
  color: var(--text-primary);
  margin-bottom: 6px;
}
</style>
