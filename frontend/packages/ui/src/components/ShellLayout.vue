<script setup lang="ts">
import { useAppStore } from "@vrm/app-core";
import { APP_METADATA } from "@vrm/shared";
import NavigationBar from "./NavigationBar.vue";
import OverviewView from "../views/OverviewView.vue";
import SettingsView from "../views/SettingsView.vue";
import DiagnosticsView from "../views/DiagnosticsView.vue";

const store = useAppStore();
</script>

<template>
  <div class="shell-layout">
    <NavigationBar />

    <main class="shell-main" role="main">
      <OverviewView v-if="store.state.currentTab === 'overview'" />
      <SettingsView v-else-if="store.state.currentTab === 'settings'" />
      <DiagnosticsView v-else-if="store.state.currentTab === 'diagnostics'" />
    </main>

    <footer class="shell-footer" role="contentinfo">
      <div class="footer-left">
        <span>{{ APP_METADATA.name }} &copy; 2026 Dung Tran</span>
        <span class="divider">&bull;</span>
        <span>Licensed under {{ APP_METADATA.license }}</span>
      </div>
      <div class="footer-right">
        <a
          id="footer-github-link"
          :href="APP_METADATA.repositoryUrl"
          target="_blank"
          rel="noopener noreferrer"
        >
          GitHub Repository
        </a>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.shell-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.shell-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.shell-footer {
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-subtle);
  font-size: 0.8rem;
  color: var(--text-muted);
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.divider {
  color: var(--text-muted);
}
</style>
