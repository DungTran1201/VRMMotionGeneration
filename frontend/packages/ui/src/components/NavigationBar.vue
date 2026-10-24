<script setup lang="ts">
import { computed } from "vue";
import { useAppStore, type NavigationTab } from "@vrm/app-core";
import { APP_METADATA } from "@vrm/shared";
import StatusBadge from "./StatusBadge.vue";

const store = useAppStore();

const activeTabs = computed<{ id: NavigationTab; label: string }[]>(() => {
  if (store.state.isAuthenticated) {
    return [
      { id: "overview", label: "Overview" },
      { id: "profile", label: "Profile" },
      { id: "security", label: "Security" },
      { id: "secrets", label: "AI Keys" },
      { id: "settings", label: "Settings" },
      { id: "diagnostics", label: "Diagnostics" },
    ];
  }
  return [
    { id: "overview", label: "Overview" },
    { id: "settings", label: "Settings" },
    { id: "diagnostics", label: "Diagnostics" },
  ];
});

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
        v-for="tab in activeTabs"
        :key="tab.id"
        :id="`nav-tab-${tab.id}`"
        :class="['nav-btn', { active: store.state.currentTab === tab.id }]"
        @click="store.setTab(tab.id)"
      >
        {{ tab.label }}
      </button>
    </nav>

    <div class="nav-actions">
      <!-- Auth Actions -->
      <template v-if="store.state.isAuthenticated">
        <button
          id="nav-user-pill"
          class="user-pill-btn"
          title="Account Profile"
          @click="store.setTab('profile')"
        >
          <span class="user-pill-icon">👤</span>
          <span class="user-pill-name">{{
            store.state.user?.displayName ||
            store.state.user?.email?.split("@")[0]
          }}</span>
        </button>
        <button
          id="nav-signout-btn"
          class="nav-auth-btn"
          title="Sign Out"
          @click="store.logout()"
        >
          Sign Out
        </button>
      </template>
      <template v-else>
        <button
          id="nav-signin-btn"
          class="nav-auth-btn"
          @click="store.setTab('signin')"
        >
          Sign In
        </button>
        <button
          id="nav-signup-btn"
          class="nav-auth-primary-btn"
          @click="store.setTab('signup')"
        >
          Register
        </button>
      </template>

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

.user-pill-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: 9999px;
  color: var(--text-primary);
  font-size: 0.825rem;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.user-pill-btn:hover {
  border-color: var(--accent-cyan);
}

.user-pill-icon {
  font-size: 0.85rem;
}

.user-pill-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-auth-btn {
  padding: 6px 12px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  transition: all var(--transition-fast);
}

.nav-auth-btn:hover {
  color: var(--text-primary);
  background: var(--border-subtle);
}

.nav-auth-primary-btn {
  padding: 6px 14px;
  background: var(--accent-cyan);
  color: #000;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.nav-auth-primary-btn:hover {
  background: #22d3ee;
  box-shadow: 0 0 10px var(--accent-cyan-glow);
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
