<script setup lang="ts">
import { ref } from "vue";
import { useAppStore } from "@vrm/app-core";

const store = useAppStore();

const email = ref("");
const password = ref("");
const isSubmitting = ref(false);
const formError = ref<string | null>(null);

async function handleSubmit() {
  if (!email.value || !password.value) {
    formError.value = "Please enter both email and password";
    return;
  }
  formError.value = null;
  isSubmitting.value = true;
  try {
    await store.login(email.value, password.value);
  } catch (err: any) {
    formError.value = err?.message || "Invalid email or password";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="auth-view">
    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-icon">🔐</div>
        <h1 class="auth-title">Welcome Back</h1>
        <p class="auth-subtitle">
          Sign in to your account across Web and Desktop
        </p>
      </div>

      <div
        v-if="formError || store.state.authError"
        class="alert alert-error"
        role="alert"
      >
        {{ formError || store.state.authError }}
      </div>

      <div
        v-if="store.state.authNotice"
        class="alert alert-success"
        role="status"
      >
        {{ store.state.authNotice }}
      </div>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="signin-email" class="form-label">Email Address</label>
          <input
            id="signin-email"
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
          <div class="label-row">
            <label for="signin-password" class="form-label">Password</label>
            <button
              type="button"
              class="link-btn"
              @click="store.setTab('forgot-password')"
            >
              Forgot password?
            </button>
          </div>
          <input
            id="signin-password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            required
            class="form-input"
            placeholder="••••••••••••••••"
            :disabled="isSubmitting"
          />
        </div>

        <button
          id="signin-submit-btn"
          type="submit"
          class="btn btn-primary"
          :disabled="isSubmitting"
        >
          <span v-if="isSubmitting" class="spinner"></span>
          <span>{{ isSubmitting ? "Signing in..." : "Sign In" }}</span>
        </button>
      </form>

      <div class="auth-footer">
        <span class="text-muted">Don't have an account?</span>
        <button
          id="goto-signup-btn"
          type="button"
          class="link-btn font-semibold"
          @click="store.setTab('signup')"
        >
          Create account
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

.alert-success {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid var(--accent-success);
  color: #86efac;
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

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
