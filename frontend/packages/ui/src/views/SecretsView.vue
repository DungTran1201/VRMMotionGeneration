<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useAppStore } from "@vrm/app-core";

const store = useAppStore();

const provider = ref<"gemini" | "openai" | "anthropic">("gemini");
const apiKey = ref("");
const isSaving = ref(false);

onMounted(async () => {
  await store.fetchSecrets();
});

async function handleSave() {
  if (!apiKey.value || apiKey.value.length < 8) {
    return;
  }
  isSaving.value = true;
  try {
    await store.saveSecret(provider.value, apiKey.value);
    apiKey.value = "";
  } finally {
    isSaving.value = false;
  }
}

async function handleDelete(targetProvider: string) {
  if (confirm(`Delete the API key for ${targetProvider}?`)) {
    await store.deleteSecret(targetProvider);
  }
}
</script>

<template>
  <div class="secrets-view">
    <div class="secrets-container">
      <div class="secrets-header">
        <h1 class="page-title">AI Provider Key Vault</h1>
        <p class="page-subtitle">
          Store personal provider credentials for AI model integrations
        </p>
      </div>

      <!-- Envelope Encryption Notice -->
      <div class="vault-notice" role="note">
        <div class="vault-notice-title">
          🔒 Hardware / KMS Envelope Encryption
        </div>
        <div class="vault-notice-body">
          API keys are encrypted using AES-256-GCM with keys managed by backend
          KMS. Keys are never logged, never exposed to renderer local storage,
          and only masked hints are displayed.
        </div>
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

      <!-- Add Secret Form -->
      <section class="secrets-card" aria-labelledby="heading-add-secret">
        <h2 id="heading-add-secret" class="card-title">Add / Rotate API Key</h2>
        <form class="secret-form" @submit.prevent="handleSave">
          <div class="grid-2">
            <div class="form-group">
              <label for="provider-select" class="form-label"
                >AI Provider</label
              >
              <select
                id="provider-select"
                v-model="provider"
                class="form-select"
                :disabled="isSaving"
              >
                <option value="gemini">Google Gemini</option>
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic Claude</option>
              </select>
            </div>

            <div class="form-group">
              <label for="key-input" class="form-label">API Key</label>
              <input
                id="key-input"
                v-model="apiKey"
                type="password"
                required
                class="form-input"
                placeholder="Paste key (e.g. AIzaSy...)"
                :disabled="isSaving"
              />
            </div>
          </div>

          <div class="action-row">
            <button
              id="save-secret-btn"
              type="submit"
              class="btn btn-primary"
              :disabled="isSaving || apiKey.length < 8"
            >
              <span v-if="isSaving" class="spinner"></span>
              <span>{{ isSaving ? "Encrypting..." : "Save API Key" }}</span>
            </button>
          </div>
        </form>
      </section>

      <!-- Stored Secrets List -->
      <section class="secrets-card" aria-labelledby="heading-stored-secrets">
        <h2 id="heading-stored-secrets" class="card-title">
          Vaulted Credentials
        </h2>

        <div v-if="store.state.secrets.length === 0" class="empty-state">
          No external provider keys stored yet.
        </div>

        <ul v-else class="secrets-list" role="list">
          <li
            v-for="secret in store.state.secrets"
            :key="secret.provider"
            class="secret-item"
          >
            <div class="secret-info">
              <div class="provider-badge">
                {{ secret.provider.toUpperCase() }}
              </div>
              <div class="secret-meta">
                <span class="key-hint font-mono">{{ secret.keyHint }}</span>
                <span class="update-date"
                  >Updated:
                  {{ new Date(secret.updatedAt).toLocaleDateString() }}</span
                >
              </div>
            </div>

            <button
              :id="`delete-secret-${secret.provider}`"
              type="button"
              class="btn-delete"
              title="Delete this key"
              @click="handleDelete(secret.provider)"
            >
              Remove
            </button>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<style scoped>
.secrets-view {
  flex: 1;
  padding: 32px 24px;
  display: flex;
  justify-content: center;
}

.secrets-container {
  width: 100%;
  max-width: 680px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.secrets-header {
  margin-bottom: 4px;
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

.vault-notice {
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: var(--radius-md);
  padding: 16px 20px;
}

.vault-notice-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--accent-indigo);
  margin-bottom: 4px;
}

.vault-notice-body {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.secrets-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 24px;
}

.card-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.alert {
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  margin-bottom: 16px;
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

.secret-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 16px;
}

@media (max-width: 600px) {
  .grid-2 {
    grid-template-columns: 1fr;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-input,
.form-select {
  width: 100%;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 0.95rem;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--border-focus);
}

.action-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 4px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 18px;
  font-size: 0.9rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: var(--accent-indigo);
  color: #ffffff;
}

.empty-state {
  font-size: 0.85rem;
  color: var(--text-muted);
  padding: 12px 0;
}

.secrets-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.secret-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
}

.secret-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.provider-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 4px;
  background: rgba(99, 102, 241, 0.15);
  color: var(--accent-indigo);
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.secret-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.key-hint {
  font-size: 0.9rem;
  color: var(--text-primary);
}

.font-mono {
  font-family: var(--font-family-mono);
}

.update-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.btn-delete {
  background: none;
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  padding: 4px 10px;
  font-size: 0.75rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.btn-delete:hover {
  background: rgba(239, 68, 68, 0.15);
}

.spinner {
  width: 14px;
  height: 14px;
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
