<script setup lang="ts">
import { useAppStore } from "@vrm/app-core";
import { APP_METADATA } from "@vrm/shared";

const store = useAppStore();
</script>

<template>
  <div class="view-container">
    <div class="hero">
      <div class="hero-badge">Architecture Reset Complete</div>
      <h1 class="hero-title">{{ APP_METADATA.name }}</h1>
      <p class="hero-subtitle">
        A unified, type-safe foundation engineered for high-performance Web and
        native Electron Desktop applications.
      </p>
    </div>

    <div class="grid-cards">
      <div class="card">
        <div class="card-header">
          <span class="card-icon">🏗️</span>
          <h3>Monorepo Topology</h3>
        </div>
        <p class="card-text">
          Modular pnpm workspace isolating presentation
          (<code>frontend/</code>), infra (<code>infra/</code>), and canonical
          contracts (<code>schemas/</code>).
        </p>
        <div class="card-meta">
          <span>Packages: 4</span>
          <span>Apps: 2 (Web & Desktop)</span>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <span class="card-icon">⚡</span>
          <h3>Unified Presentation</h3>
        </div>
        <p class="card-text">
          Vue 3 Composition API and sleek CSS design tokens shared between
          browser and Electron native renderer without code duplication.
        </p>
        <div class="card-meta">
          <span>Engine: Vite 6+</span>
          <span>Mode: TypeScript Strict</span>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <span class="card-icon">🛡️</span>
          <h3>Electron Security Baseline</h3>
        </div>
        <p class="card-text">
          Preload contextBridge, OS sandbox, disabled nodeIntegration, strict
          CSP, and allowlisted IPC channel isolation.
        </p>
        <div class="card-meta">
          <span>Isolation: Active</span>
          <span>Sandbox: Enabled</span>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <span class="card-icon">🔬</span>
          <h3>Evidence-First Status</h3>
        </div>
        <p class="card-text">
          All legacy motion generation experiments, models, and checkpoints have
          been purged. Zero simulated test gates.
        </p>
        <div class="card-meta">
          <span>Quality Gates: QG-01 to QG-08</span>
        </div>
      </div>
    </div>

    <div class="actions-strip">
      <button
        id="overview-diagnostics-btn"
        class="primary-btn"
        @click="store.setTab('diagnostics')"
      >
        Inspect Runtime Diagnostics →
      </button>
      <button
        id="overview-settings-btn"
        class="secondary-btn"
        @click="store.setTab('settings')"
      >
        Configure Settings
      </button>
    </div>
  </div>
</template>

<style scoped>
.view-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 24px;
}

.hero {
  text-align: center;
  margin-bottom: 48px;
}

.hero-badge {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(6, 182, 212, 0.12);
  border: 1px solid rgba(6, 182, 212, 0.3);
  color: var(--accent-cyan);
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 16px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #ffffff, #94a3b8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
  max-width: 640px;
  margin: 0 auto;
}

.grid-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 24px;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(8px);
  transition: all var(--transition-normal);
}

.card:hover {
  border-color: var(--border-focus);
  transform: translateY(-2px);
  background: var(--bg-card-hover);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.card-icon {
  font-size: 1.5rem;
}

.card-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.card-text {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 20px;
  flex: 1;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: var(--font-family-mono);
  border-top: 1px solid var(--border-subtle);
  padding-top: 12px;
}

.actions-strip {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.primary-btn {
  padding: 12px 24px;
  background: var(--accent-cyan);
  color: #000;
  font-weight: 600;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.primary-btn:hover {
  background: #22d3ee;
  box-shadow: 0 0 16px var(--accent-cyan-glow);
}

.secondary-btn {
  padding: 12px 24px;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  font-weight: 600;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  transition: all var(--transition-fast);
}

.secondary-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}
</style>
