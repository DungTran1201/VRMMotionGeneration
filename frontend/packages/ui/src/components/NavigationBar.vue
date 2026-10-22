<script setup lang="ts">
import { computed } from "vue";
import { useAppStore, type NavigationTab } from "@vrm/app-core";
import { APP_METADATA } from "@vrm/shared";
import StatusBadge from "./StatusBadge.vue";

const store = useAppStore();

const tabs: { id: NavigationTab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "settings", label: "Settings" },
  { id: "diagnostics", label: "Diagnostics" },
];

const platformLabel = computed(() =>
  store.platform.value === "electron" ? "Desktop App" : "Web Client",
);
</script>

<template>
  <header class="navbar" role="banner">
    <div class="brand">
      <div class="logo-mark">⚡</div>
      <div class="brand-text">
        <span class="app-name">{{ APP_METADATA.shortName }}</span>
        <span class="app-version">v{{ APP_METADATA.version }}</span>
      </div>
      <StatusBadge status="ready" :label="platformLabel" />
    </div>

    <nav class="nav-links" aria-label="Main Navigation">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :id="`nav-tab-${tab.id}`"
        :class="['nav-btn', { active: store.state.currentTab === tab.id }]"
        @click="store.setTab(tab.id)"
      >
        {{ tab.label }}
      </button>
    </nav>

    <div class="nav-actions">
      <button
        id="theme-toggle-btn"
        class="action-icon-btn"
        title="Toggle Theme"
        @click="
          store.updateSettings({
            theme: store.state.settings.theme === 'dark' ? 'light' : 'dark',
          })
        "
      >
        {{ store.state.settings.theme === "dark" ? "☀️" : "🌙" }}
      </button>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
  user-select: none;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-mark {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo));
  border-radius: var(--radius-sm);
  font-size: 1.1rem;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.app-name {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.app-version {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: var(--font-family-mono);
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-btn {
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.nav-btn:hover {
  color: var(--text-primary);
  background: var(--border-subtle);
}

.nav-btn.active {
  color: var(--accent-cyan);
  background: rgba(6, 182, 212, 0.12);
  border: 1px solid rgba(6, 182, 212, 0.3);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  background: var(--border-subtle);
  font-size: 1.1rem;
  transition: background var(--transition-fast);
}

.action-icon-btn:hover {
  background: var(--bg-tertiary);
}
</style>
