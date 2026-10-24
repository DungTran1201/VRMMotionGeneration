<script setup lang="ts">
import { ref, computed } from "vue";
import { useAppStore } from "@vrm/app-core";

const store = useAppStore();

const email = ref("");
const displayName = ref("");
const password = ref("");
const isSubmitting = ref(false);
const formError = ref<string | null>(null);

const isPasswordLongEnough = computed(() => password.value.length >= 15);

async function handleSubmit() {
  if (!email.value || !password.value) {
    formError.value = "Please complete all required fields";
    return;
  }
  if (password.value.length < 15) {
    formError.value = "Password must be at least 15 characters long";
    return;
  }

  formError.value = null;
  isSubmitting.value = true;
  try {
    await store.register(
      email.value,
      password.value,
      displayName.value || undefined,
    );
  } catch (err: any) {
    formError.value = err?.message || "Registration failed";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="auth-view">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-icon">🚀</div>
        <h1 class="auth-title">Create Account</h1>
        <p class="auth-subtitle">
          Instant activation with shared Web & Desktop access
        </p>
      </div>

      <!-- Policy Advisory: No Email Verification -->
      <div class="advisory-banner" role="note">
        <div class="advisory-title">ℹ️ No Email Verification Required</div>
        <div class="advisory-text">
          Accounts activate immediately upon creation. No confirmation links or
          OTPs will be sent. Please ensure your email address is spelled
          correctly for account recovery.
        </div>
      </div>

      <div
        v-if="formError || store.state.authError"
        class="alert alert-error"
        role="alert"
      >
        {{ formError || store.state.authError }}
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="signup-email" class="form-label"
            >Email Address (Login Identifier)</label
          >
          <input
            id="signup-email"
            v-model="email"
            type="email"
            autocomplete="email"
            required
            class="form-input"
            placeholder="alex@example.com"
            :disabled="isSubmitting"
          />
        </div>

        <div class="form-group">
          <label for="signup-name" class="form-label"
            >Display Name (Optional)</label
          >
          <input
            id="signup-name"
            v-model="displayName"
            type="text"
            autocomplete="name"
            class="form-input"
            placeholder="Alex Chen"
            :disabled="isSubmitting"
          />
        </div>

        <div class="form-group">
          <label for="signup-password" class="form-label">Password</label>
          <input
            id="signup-password"
            v-model="password"
            type="password"
            autocomplete="new-password"
            required
            class="form-input"
            placeholder="At least 15 characters"
            :disabled="isSubmitting"
          />
          <div class="input-hint" :class="{ valid: isPasswordLongEnough }">
            {{ password.length }} / 15 characters minimum (NIST SP 800-63B-4
            standard)
          </div>
        </div>

        <button
          id="signup-submit-btn"
          type="submit"
          class="btn btn-primary"
          :disabled="isSubmitting || !isPasswordLongEnough"
        >
          <span v-if="isSubmitting" class="spinner"></span>
          <span>{{
            isSubmitting ? "Creating account..." : "Create Account & Sign In"
          }}</span>
        </button>
      </form>

      <div class="auth-footer">
        <span class="text-muted">Already have an account?</span>
        <button
          id="goto-signin-btn"
          type="button"
          class="link-btn font-semibold"
          @click="store.setTab('signin')"
        >
          Sign in
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
  max-width: 480px;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 32px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.auth-header {
  text-align: center;
  margin-bottom: 20px;
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

.advisory-banner {
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.3);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  margin-bottom: 20px;
}

.advisory-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--accent-cyan);
  margin-bottom: 4px;
}

.advisory-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.4;
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
  transition: border-color var(--transition-fast);
}

.form-input:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 2px var(--accent-cyan-glow);
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  transition: all var(--transition-fast);
  border: none;
}

.btn-primary {
  background: var(--accent-indigo);
  color: #ffffff;
  margin-top: 6px;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  gap: 8px;
  font-size: 0.85rem;
}

.text-muted {
  color: var(--text-muted);
}

.font-semibold {
  font-weight: 600;
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
