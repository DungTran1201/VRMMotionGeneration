<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useAppStore } from "@vrm/app-core";

const store = useAppStore();

const currentPassword = ref("");
const newPassword = ref("");
const revokeOthers = ref(true);
const isChangingPassword = ref(false);
const passwordNotice = ref<string | null>(null);
const passwordError = ref<string | null>(null);

const deletePassword = ref("");
const confirmPhrase = ref("");
const isDeleting = ref(false);
const deleteError = ref<string | null>(null);

const isNewPasswordValid = computed(() => newPassword.value.length >= 15);

onMounted(async () => {
  await store.fetchSessions();
});

async function handlePasswordChange() {
  if (!currentPassword.value || !newPassword.value) {
    passwordError.value = "Please complete all password fields";
    return;
  }
  if (newPassword.value.length < 15) {
    passwordError.value = "New password must be at least 15 characters long";
    return;
  }

  passwordError.value = null;
  passwordNotice.value = null;
  isChangingPassword.value = true;
  try {
    await store.changePassword(
      currentPassword.value,
      newPassword.value,
      revokeOthers.value,
    );
    passwordNotice.value = "Password updated successfully";
    currentPassword.value = "";
    newPassword.value = "";
    await store.fetchSessions();
  } catch (err: any) {
    passwordError.value = err?.message || "Failed to update password";
  } finally {
    isChangingPassword.value = false;
  }
}

async function handleRevokeSession(sessionId: string) {
  await store.revokeSession(sessionId);
}

async function handleLogoutAll() {
  if (confirm("Are you sure you want to log out of all active devices?")) {
    await store.logoutAll();
  }
}

async function handleDeleteAccount() {
  if (confirmPhrase.value !== "DELETE MY ACCOUNT") {
    deleteError.value = 'Please type "DELETE MY ACCOUNT" exactly to confirm';
    return;
  }
  if (!deletePassword.value) {
    deleteError.value = "Current password is required to delete account";
    return;
  }

  isDeleting.value = true;
  deleteError.value = null;
  try {
    const res = await fetch("http://127.0.0.1:3000/api/v1/users/me/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        currentPassword: deletePassword.value,
        confirmationPhrase: confirmPhrase.value,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || "Failed to delete account");
    }
    await store.logout();
  } catch (err: any) {
    deleteError.value = err?.message || "Account deletion failed";
  } finally {
    isDeleting.value = false;
  }
}
</script>

<template>
  <div class="security-view">
    <div class="security-container">
      <div class="security-header">
        <h1 class="page-title">Account Security</h1>
        <p class="page-subtitle">
          Manage credentials, active device sessions, and authentication
          controls
        </p>
      </div>

      <!-- Password Change Section -->
      <section class="security-card" aria-labelledby="heading-password">
        <h2 id="heading-password" class="card-title">Change Password</h2>
        <p class="card-description">
          Choose a strong, unique password of at least 15 characters (NIST SP
          800-63B-4 standard).
        </p>

        <div v-if="passwordNotice" class="alert alert-success" role="status">
          {{ passwordNotice }}
        </div>
        <div v-if="passwordError" class="alert alert-error" role="alert">
          {{ passwordError }}
        </div>

        <form class="security-form" @submit.prevent="handlePasswordChange">
          <div class="form-group">
            <label for="current-pwd" class="form-label">Current Password</label>
            <input
              id="current-pwd"
              v-model="currentPassword"
              type="password"
              autocomplete="current-password"
              required
              class="form-input"
              placeholder="••••••••••••••••"
              :disabled="isChangingPassword"
            />
          </div>

          <div class="form-group">
            <label for="new-pwd" class="form-label">New Password</label>
            <input
              id="new-pwd"
              v-model="newPassword"
              type="password"
              autocomplete="new-password"
              required
              class="form-input"
              placeholder="At least 15 characters"
              :disabled="isChangingPassword"
            />
            <div class="input-hint" :class="{ valid: isNewPasswordValid }">
              {{ newPassword.length }} / 15 characters minimum
            </div>
          </div>

          <div class="checkbox-group">
            <input
              id="revoke-others-chk"
              v-model="revokeOthers"
              type="checkbox"
              class="form-checkbox"
            />
            <label for="revoke-others-chk" class="checkbox-label">
              Log out of all other devices and applications
            </label>
          </div>

          <div class="action-row">
            <button
              id="change-pwd-btn"
              type="submit"
              class="btn btn-primary"
              :disabled="isChangingPassword || !isNewPasswordValid"
            >
              <span v-if="isChangingPassword" class="spinner"></span>
              <span>{{
                isChangingPassword ? "Updating..." : "Update Password"
              }}</span>
            </button>
          </div>
        </form>
      </section>

      <!-- Active Sessions & Devices -->
      <section class="security-card" aria-labelledby="heading-sessions">
        <div class="card-header-row">
          <div>
            <h2 id="heading-sessions" class="card-title">
              Active Devices & Sessions
            </h2>
            <p class="card-description">
              Review applications and browsers currently authenticated to your
              account.
            </p>
          </div>
          <button
            id="logout-all-btn"
            type="button"
            class="btn btn-outline-danger"
            @click="handleLogoutAll"
          >
            Log Out of All Devices
          </button>
        </div>

        <div v-if="store.state.sessions.length === 0" class="empty-state">
          No other active sessions detected.
        </div>

        <ul v-else class="session-list" role="list">
          <li
            v-for="session in store.state.sessions"
            :key="session.id"
            class="session-item"
            :class="{ current: session.isCurrent }"
          >
            <div class="session-info">
              <div class="session-icon">
                {{ session.clientType === "desktop" ? "💻" : "🌐" }}
              </div>
              <div class="session-details">
                <div class="device-name">
                  <span>{{ session.deviceName }}</span>
                  <span v-if="session.isCurrent" class="current-badge"
                    >This Device</span
                  >
                </div>
                <div class="device-meta">
                  <span>IP: {{ session.ipSubnet }}</span>
                  <span>&bull;</span>
                  <span
                    >Active:
                    {{ new Date(session.lastSeenAt).toLocaleString() }}</span
                  >
                </div>
              </div>
            </div>

            <button
              v-if="!session.isCurrent"
              :id="`revoke-session-${session.id}`"
              type="button"
              class="btn-revoke"
              title="Revoke this device session"
              @click="handleRevokeSession(session.id)"
            >
              Revoke
            </button>
          </li>
        </ul>
      </section>

      <!-- Danger Zone: Account Deletion -->
      <section
        class="security-card danger-card"
        aria-labelledby="heading-danger"
      >
        <h2 id="heading-danger" class="card-title text-danger">Danger Zone</h2>
        <p class="card-description">
          Permanently delete your account and all associated sessions and stored
          API keys.
        </p>

        <div v-if="deleteError" class="alert alert-error" role="alert">
          {{ deleteError }}
        </div>

        <form class="security-form" @submit.prevent="handleDeleteAccount">
          <div class="form-group">
            <label for="delete-pwd" class="form-label"
              >Confirm Current Password</label
            >
            <input
              id="delete-pwd"
              v-model="deletePassword"
              type="password"
              required
              class="form-input"
              placeholder="••••••••••••••••"
              :disabled="isDeleting"
            />
          </div>

          <div class="form-group">
            <label for="delete-confirm-text" class="form-label">
              Type <strong class="text-danger">DELETE MY ACCOUNT</strong> to
              confirm:
            </label>
            <input
              id="delete-confirm-text"
              v-model="confirmPhrase"
              type="text"
              required
              class="form-input"
              placeholder="DELETE MY ACCOUNT"
              :disabled="isDeleting"
            />
          </div>

          <div class="action-row">
            <button
              id="delete-account-btn"
              type="submit"
              class="btn btn-danger"
              :disabled="isDeleting || confirmPhrase !== 'DELETE MY ACCOUNT'"
            >
              <span v-if="isDeleting" class="spinner"></span>
              <span>{{
                isDeleting ? "Deleting..." : "Permanently Delete Account"
              }}</span>
            </button>
          </div>
        </form>
      </section>
    </div>
  </div>
</template>

<style scoped>
.security-view {
  flex: 1;
  padding: 32px 24px;
  display: flex;
  justify-content: center;
}

.security-container {
  width: 100%;
  max-width: 680px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.security-header {
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

.security-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 24px;
}

.danger-card {
  border-color: rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.03);
}

.card-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.card-description {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 18px;
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 18px;
  gap: 16px;
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

.security-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
}

.input-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.input-hint.valid {
  color: var(--accent-success);
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.checkbox-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.action-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 6px;
}

.session-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
}

.session-item.current {
  border-color: rgba(6, 182, 212, 0.4);
}

.session-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.session-icon {
  font-size: 1.3rem;
}

.device-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.current-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 9999px;
  background: rgba(6, 182, 212, 0.15);
  color: var(--accent-cyan);
  border: 1px solid rgba(6, 182, 212, 0.3);
}

.device-meta {
  font-size: 0.75rem;
  color: var(--text-muted);
  display: flex;
  gap: 6px;
  margin-top: 2px;
}

.btn-revoke {
  background: none;
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
  padding: 4px 10px;
  font-size: 0.75rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.btn-revoke:hover {
  background: rgba(239, 68, 68, 0.15);
}

.empty-state {
  font-size: 0.85rem;
  color: var(--text-muted);
  padding: 16px 0;
}

.text-danger {
  color: var(--accent-danger);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: var(--radius-sm);
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: var(--accent-indigo);
  color: #ffffff;
}

.btn-outline-danger {
  background: none;
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}

.btn-outline-danger:hover {
  background: rgba(239, 68, 68, 0.15);
}

.btn-danger {
  background: var(--accent-danger);
  color: #ffffff;
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
