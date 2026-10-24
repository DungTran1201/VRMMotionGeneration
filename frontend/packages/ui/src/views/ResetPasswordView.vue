<script setup lang="ts">
import { ref, computed } from "vue";
import { useAppStore } from "@vrm/app-core";

const store = useAppStore();

const token = ref(store.state.resetToken || "");
const newPassword = ref("");
const isSubmitting = ref(false);
const formError = ref<string | null>(null);

const isPasswordLongEnough = computed(() => newPassword.value.length >= 15);

async function handleSubmit() {
  if (!token.value || !newPassword.value) {
    formError.value = "Please provide both the reset token and new password";
    return;
  }
  if (newPassword.value.length < 15) {
    formError.value = "New password must be at least 15 characters long";
    return;
  }

  formError.value = null;
  isSubmitting.value = true;
  try {
    await store.resetPassword(token.value, newPassword.value);
  } catch (err: any) {
    formError.value =
      err?.message || "Password reset failed. The link may have expired.";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="auth-view">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-icon">🛡️</div>
        <h1 class="auth-title">Set New Password</h1>
        <p class="auth-subtitle">
          All existing active sessions will be terminated upon reset
        </p>
      </div>

      <div v-if="formError" class="alert alert-error" role="alert">
        {{ formError }}
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="reset-token-input" class="form-label">Reset Token</label>
          <input
            id="reset-token-input"
            v-model="token"
            type="text"
            required
            class="form-input font-mono"
            placeholder="Paste reset token from email"
            :disabled="isSubmitting"
          />
        </div>

        <div class="form-group">
          <label for="reset-new-password" class="form-label"
            >New Password</label
          >
          <input
            id="reset-new-password"
            v-model="newPassword"
            type="password"
            autocomplete="new-password"
            required
            class="form-input"
            placeholder="At least 15 characters"
            :disabled="isSubmitting"
          />
          <div class="input-hint" :class="{ valid: isPasswordLongEnough }">
            {{ newPassword.length }} / 15 characters minimum
          </div>
        </div>

        <button
          id="reset-submit-btn"
          type="submit"
          class="btn btn-primary"
          :disabled="isSubmitting || !isPasswordLongEnough"
        >
          <span v-if="isSubmitting" class="spinner"></span>
          <span>{{
            isSubmitting ? "Updating..." : "Update Password & Sign In"
          }}</span>
        </button>
      </form>

      <div class="auth-footer">
        <button
          type="button"
          class="link-btn font-semibold"
          @click="store.setTab('signin')"
        >
          &larr; Back to sign in
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-view {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 16px;
}

.auth-card {
  width: 100%;
  max-width: 440px;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 32px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.auth-header {
  text-align: center;
  margin-bottom: 24px;
}

.auth-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

.auth-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.auth-subtitle {
  font-size: 0.9rem;
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

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
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

.font-mono {
  font-family: var(--font-family-mono);
  font-size: 0.85rem;
}

.input-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.input-hint.valid {
  color: var(--accent-success);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: var(--accent-indigo);
  color: #ffffff;
  margin-top: 6px;
}

.link-btn {
  background: none;
  border: none;
  color: var(--accent-cyan);
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0;
}

.link-btn:hover {
  text-decoration: underline;
}

.auth-footer {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  justify-content: center;
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
