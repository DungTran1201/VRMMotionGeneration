<script setup lang="ts">
import { ref, watch } from "vue";
import { useAppStore } from "@vrm/app-core";

const store = useAppStore();

const displayName = ref(store.state.user?.displayName || "");
const timezone = ref(store.state.user?.timezone || "UTC");
const locale = ref(store.state.user?.locale || "en-US");
const isSaving = ref(false);

watch(
  () => store.state.user,
  (newUser) => {
    if (newUser) {
      displayName.value = newUser.displayName;
      timezone.value = newUser.timezone;
      locale.value = newUser.locale;
    }
  },
  { immediate: true },
);

async function handleSave() {
  isSaving.value = true;
  try {
    await store.updateProfile({
      displayName: displayName.value,
      timezone: timezone.value,
      locale: locale.value,
    });
  } finally {
    isSaving.value = false;
  }
}
</script>

<template>
  <div class="profile-view">
    <div class="profile-container">
      <div class="profile-header">
        <h1 class="page-title">Account Profile</h1>
        <p class="page-subtitle">
          Manage your personal details and contact preferences
        </p>
      </div>

      <div
        v-if="store.state.authNotice"
        class="alert alert-success"
        role="status"
      >
        {{ store.state.authNotice }}
      </div>

      <div v-if="store.state.authError" class="alert alert-error" role="alert">
        {{ store.state.authError }}
      </div>

      <!-- Prominent Unverified Email Notice -->
      <div
        class="email-status-card"
        role="region"
        aria-label="Email Verification Notice"
      >
        <div class="status-badge-row">
          <span class="status-pill status-unverified"
            >⚠️ Unverified Contact Address</span
          >
          <span class="registered-date"
            >Created
            {{
              new Date(store.state.user?.createdAt || "").toLocaleDateString()
            }}</span
          >
        </div>
        <div class="email-value">{{ store.state.user?.email }}</div>
        <p class="email-explanation">
          Email addresses on this platform are self-asserted and unverified by
          product design. This address is used strictly as a login identifier
          and recovery channel for password resets.
        </p>
      </div>

      <form class="profile-form" @submit.prevent="handleSave">
        <div class="form-group">
          <label for="profile-name" class="form-label">Display Name</label>
          <input
            id="profile-name"
            v-model="displayName"
            type="text"
            required
            class="form-input"
            placeholder="Your name"
            :disabled="isSaving"
          />
        </div>

        <div class="grid-2">
          <div class="form-group">
            <label for="profile-timezone" class="form-label">Timezone</label>
            <input
              id="profile-timezone"
              v-model="timezone"
              type="text"
              class="form-input"
              placeholder="e.g. America/New_York"
              :disabled="isSaving"
            />
          </div>

          <div class="form-group">
            <label for="profile-locale" class="form-label">Locale</label>
            <input
              id="profile-locale"
              v-model="locale"
              type="text"
              class="form-input"
              placeholder="e.g. en-US"
              :disabled="isSaving"
            />
          </div>
        </div>

        <div class="action-row">
          <button
            id="save-profile-btn"
            type="submit"
            class="btn btn-primary"
            :disabled="isSaving"
          >
            <span v-if="isSaving" class="spinner"></span>
            <span>{{ isSaving ? "Saving..." : "Save Changes" }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.profile-view {
  flex: 1;
  padding: 32px 24px;
  display: flex;
  justify-content: center;
}

.profile-container {
  width: 100%;
  max-width: 680px;
}

.profile-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.page-subtitle {
  font-size: 0.95rem;
  color: var(--text-secondary);
}

.alert {
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  margin-bottom: 20px;
}

.alert-error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid var(--accent-danger);
  color: #fca5a5;
}

.alert-success {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid var(--accent-success);
  color: #86efac;
}

.email-status-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 20px;
  margin-bottom: 28px;
}

.status-badge-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.status-pill {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 9999px;
}

.status-unverified {
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid var(--accent-warning);
  color: #fcd34d;
}

.registered-date {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.email-value {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.email-explanation {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.4;
  margin: 0;
}

.profile-form {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 600px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }
}

.form-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 0.95rem;
}

.form-input:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 2px var(--accent-cyan-glow);
}

.action-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: var(--accent-indigo);
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
