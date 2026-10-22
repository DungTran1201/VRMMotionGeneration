export type PlatformType = "web" | "electron";

export type EnvironmentType = "development" | "production" | "test";

export interface PlatformCapabilities {
  desktopIntegration: boolean;
  fileSystemAccess: boolean;
  nativeMenus: boolean;
}

export interface OperatingSystemInfo {
  platform: string;
  arch: string;
  release: string;
}

export interface DiagnosticsInfo {
  platform: PlatformType;
  appVersion: string;
  environment: EnvironmentType;
  timestamp: string;
  capabilities: PlatformCapabilities;
  os?: OperatingSystemInfo;
}

export interface AppSettings {
  theme: "dark" | "light" | "system";
  telemetryEnabled: boolean;
  logLevel: "debug" | "info" | "warn" | "error";
}

export interface DesktopAPI {
  getAppVersion: () => Promise<string>;
  getDiagnostics: () => Promise<DiagnosticsInfo>;
  ping: () => Promise<string>;
}

export const IPC_CHANNELS = {
  GET_VERSION: "app:get-version",
  GET_DIAGNOSTICS: "app:get-diagnostics",
  PING: "app:ping",
} as const;

export type IPCChannel = (typeof IPC_CHANNELS)[keyof typeof IPC_CHANNELS];

declare global {
  interface Window {
    desktopAPI?: DesktopAPI;
  }
}
