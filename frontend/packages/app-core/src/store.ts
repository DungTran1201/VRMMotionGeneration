import { reactive, computed } from "vue";
import type {
  AppSettings,
  DiagnosticsInfo,
  PlatformType,
} from "@vrm/platform-contracts";
import { DEFAULT_SETTINGS } from "@vrm/shared";
import { detectPlatform, getPlatformAPI } from "./platform.js";

export type NavigationTab = "overview" | "settings" | "diagnostics";

export interface AppState {
  currentTab: NavigationTab;
  settings: AppSettings;
  diagnostics: DiagnosticsInfo | null;
  isLoading: boolean;
  errorMessage: string | null;
  pingResult: string | null;
}

const state = reactive<AppState>({
  currentTab: "overview",
  settings: { ...DEFAULT_SETTINGS },
  diagnostics: null,
  isLoading: false,
  errorMessage: null,
  pingResult: null,
});

export function useAppStore() {
  const platform = computed<PlatformType>(() => detectPlatform());

  function setTab(tab: NavigationTab) {
    state.currentTab = tab;
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

  return {
    state,
    platform,
    setTab,
    updateSettings,
    loadDiagnostics,
    executePing,
  };
}
