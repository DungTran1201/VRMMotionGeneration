import { reactive, computed } from "vue";
import type {
  AppSettings,
  DiagnosticsInfo,
  PlatformType,
  UserProfile,
  UserSession,
  ProviderSecretItem,
} from "@vrm/platform-contracts";
import { DEFAULT_SETTINGS } from "@vrm/shared";
import {
  detectPlatform,
  getPlatformAPI,
  isElectronEnvironment,
} from "./platform.js";

export type NavigationTab =
  | "overview"
  | "profile"
  | "security"
  | "secrets"
  | "settings"
  | "diagnostics"
  | "signin"
  | "signup"
  | "forgot-password"
  | "reset-password";

export interface AppState {
  currentTab: NavigationTab;
  settings: AppSettings;
  diagnostics: DiagnosticsInfo | null;
  isLoading: boolean;
  errorMessage: string | null;
  pingResult: string | null;
  // Auth state
  user: UserProfile | null;
  isAuthenticated: boolean;
  authLoading: boolean;
  authError: string | null;
  authNotice: string | null;
  sessions: UserSession[];
  secrets: ProviderSecretItem[];
  csrfToken: string | null;
  resetToken: string | null;
}

const state = reactive<AppState>({
  currentTab: "overview",
  settings: { ...DEFAULT_SETTINGS },
  diagnostics: null,
  isLoading: false,
  errorMessage: null,
  pingResult: null,
  user: null,
  isAuthenticated: false,
  authLoading: false,
  authError: null,
  authNotice: null,
  sessions: [],
  secrets: [],
  csrfToken: null,
  resetToken: null,
});

function getApiBaseUrl(): string {
  if (typeof window !== "undefined" && (window as any).VITE_API_BASE_URL) {
    return (window as any).VITE_API_BASE_URL;
  }
  return "http://127.0.0.1:3000";
}

async function apiRequest(
  path: string,
  options: RequestInit = {},
): Promise<any> {
  const baseUrl = getApiBaseUrl();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  if (state.csrfToken) {
    headers["X-CSRF-Token"] = state.csrfToken;
  }

  const res = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });

  const csrfHeader = res.headers.get("x-csrf-token");
  if (csrfHeader) {
    state.csrfToken = csrfHeader;
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.message || `Request failed with status ${res.status}`);
  }
  return data;
}

export function useAppStore() {
  const platform = computed<PlatformType>(() => detectPlatform());

  function setTab(tab: NavigationTab) {
    state.currentTab = tab;
    state.authError = null;
    state.authNotice = null;
  }

  function updateSettings(partial: Partial<AppSettings>) {
    Object.assign(state.settings, partial);
    if (typeof document !== "undefined") {
      document.documentElement.setAttribute("data-theme", state.settings.theme);
    }
  }

  async function loadDiagnostics() {
    state.isLoading = true;
    state.errorMessage = null;
    try {
      const api = getPlatformAPI();
      state.diagnostics = await api.getDiagnostics();
    } catch (err: unknown) {
      state.errorMessage =
        err instanceof Error ? err.message : "Failed to fetch diagnostics";
    } finally {
      state.isLoading = false;
    }
  }

  async function executePing(): Promise<string> {
    try {
      const api = getPlatformAPI();
      const res = await api.ping();
      state.pingResult = res;
      return res;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Ping failed";
      state.pingResult = `Error: ${msg}`;
      return state.pingResult;
    }
  }

  async function initAuth() {
    state.authLoading = true;
    try {
      if (
        isElectronEnvironment() &&
        window.desktopAPI?.auth?.getStoredSession
      ) {
        const stored = await window.desktopAPI.auth.getStoredSession();
        if (stored) {
          state.user = stored;
          state.isAuthenticated = true;
          return;
        }
      }

      // Web cookie check
      const profile = await apiRequest("/api/v1/users/me");
      if (profile && profile.id) {
        state.user = profile;
        state.isAuthenticated = true;
      }
    } catch {
      state.user = null;
      state.isAuthenticated = false;
    } finally {
      state.authLoading = false;
    }
  }

  async function login(emailRaw: string, passwordRaw: string) {
    state.authLoading = true;
    state.authError = null;
    state.authNotice = null;
    try {
      if (isElectronEnvironment() && window.desktopAPI?.auth?.login) {
        const res = await window.desktopAPI.auth.login({
          email: emailRaw,
          password: passwordRaw,
        });
        state.user = res.user;
        state.isAuthenticated = true;
        setTab("overview");
        return;
      }

      const res = await apiRequest("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: emailRaw, password: passwordRaw }),
      });
      state.user = res.user;
      state.isAuthenticated = true;
      if (res.csrfToken) state.csrfToken = res.csrfToken;
      setTab("overview");
    } catch (err: any) {
      state.authError = err?.message || "Invalid email or password";
      throw err;
    } finally {
      state.authLoading = false;
    }
  }

  async function register(
    emailRaw: string,
    passwordRaw: string,
    displayNameRaw?: string,
  ) {
    state.authLoading = true;
    state.authError = null;
    state.authNotice = null;
    try {
      const res = await apiRequest("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email: emailRaw,
          password: passwordRaw,
          displayName: displayNameRaw,
        }),
      });
      state.user = res.user;
      state.isAuthenticated = true;
      if (res.csrfToken) state.csrfToken = res.csrfToken;
      setTab("overview");
    } catch (err: any) {
      state.authError = err?.message || "Registration failed";
      throw err;
    } finally {
      state.authLoading = false;
    }
  }

  async function logout() {
    state.authLoading = true;
    try {
      if (isElectronEnvironment() && window.desktopAPI?.auth?.logout) {
        await window.desktopAPI.auth.logout();
      }
      await apiRequest("/api/v1/auth/logout", { method: "POST" }).catch(
        () => {},
      );
    } finally {
      state.user = null;
      state.isAuthenticated = false;
      state.sessions = [];
      state.secrets = [];
      state.authLoading = false;
      setTab("signin");
    }
  }

  async function logoutAll() {
    state.authLoading = true;
    try {
      if (isElectronEnvironment() && window.desktopAPI?.auth?.logout) {
        await window.desktopAPI.auth.logout();
      }
      await apiRequest("/api/v1/auth/logout-all", { method: "POST" }).catch(
        () => {},
      );
    } finally {
      state.user = null;
      state.isAuthenticated = false;
      state.sessions = [];
      state.secrets = [];
      state.authLoading = false;
      setTab("signin");
    }
  }

  async function fetchProfile() {
    try {
      const profile = await apiRequest("/api/v1/users/me");
      state.user = profile;
    } catch (err: any) {
      state.authError = err.message;
    }
  }

  async function updateProfile(partial: {
    displayName?: string;
    timezone?: string;
    locale?: string;
  }) {
    state.authLoading = true;
    state.authError = null;
    try {
      const updated = await apiRequest("/api/v1/users/me", {
        method: "PATCH",
        body: JSON.stringify(partial),
      });
      state.user = updated;
      state.authNotice = "Profile updated successfully";
    } catch (err: any) {
      state.authError = err.message;
      throw err;
    } finally {
      state.authLoading = false;
    }
  }

  async function changePassword(
    currentPassword: string,
    newPassword: string,
    revokeOthers: boolean = true,
  ) {
    state.authLoading = true;
    state.authError = null;
    try {
      await apiRequest("/api/v1/users/me/change-password", {
        method: "POST",
        body: JSON.stringify({
          currentPassword,
          newPassword,
          revokeOtherSessions: revokeOthers,
        }),
      });
      state.authNotice = "Password changed successfully";
    } catch (err: any) {
      state.authError = err.message;
      throw err;
    } finally {
      state.authLoading = false;
    }
  }

  async function fetchSessions() {
    try {
      const res = await apiRequest("/api/v1/users/me/sessions");
      state.sessions = res.sessions || [];
    } catch (err: any) {
      state.authError = err.message;
    }
  }

  async function revokeSession(sessionId: string) {
    try {
      await apiRequest(`/api/v1/users/me/sessions/${sessionId}`, {
        method: "DELETE",
      });
      await fetchSessions();
    } catch (err: any) {
      state.authError = err.message;
    }
  }

  async function forgotPassword(email: string): Promise<string> {
    state.authLoading = true;
    state.authError = null;
    try {
      const res = await apiRequest("/api/v1/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      state.authNotice = res.message;
      return res.message;
    } catch (err: any) {
      state.authError = err.message;
      throw err;
    } finally {
      state.authLoading = false;
    }
  }

  async function resetPassword(token: string, newPassword: string) {
    state.authLoading = true;
    state.authError = null;
    try {
      const res = await apiRequest("/api/v1/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({ token, newPassword }),
      });
      state.authNotice = res.message;
      setTab("signin");
    } catch (err: any) {
      state.authError = err.message;
      throw err;
    } finally {
      state.authLoading = false;
    }
  }

  async function fetchSecrets() {
    try {
      const res = await apiRequest("/api/v1/users/me/secrets");
      state.secrets = res.secrets || [];
    } catch (err: any) {
      state.authError = err.message;
    }
  }

  async function saveSecret(
    provider: "gemini" | "openai" | "anthropic",
    apiKey: string,
  ) {
    state.authLoading = true;
    state.authError = null;
    try {
      await apiRequest("/api/v1/users/me/secrets", {
        method: "POST",
        body: JSON.stringify({ provider, apiKey }),
      });
      await fetchSecrets();
      state.authNotice = "API key securely stored";
    } catch (err: any) {
      state.authError = err.message;
      throw err;
    } finally {
      state.authLoading = false;
    }
  }

  async function deleteSecret(provider: string) {
    try {
      await apiRequest(`/api/v1/users/me/secrets/${provider}`, {
        method: "DELETE",
      });
      await fetchSecrets();
    } catch (err: any) {
      state.authError = err.message;
    }
  }

  return {
    state,
    platform,
    setTab,
    updateSettings,
    loadDiagnostics,
    executePing,
    initAuth,
    login,
    register,
    logout,
    logoutAll,
    fetchProfile,
    updateProfile,
    changePassword,
    fetchSessions,
    revokeSession,
    forgotPassword,
    resetPassword,
    fetchSecrets,
    saveSecret,
    deleteSecret,
  };
}
