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

export interface UserProfile {
  id: string;
  email: string;
  status: "active" | "suspended" | "deactivated";
  emailVerified: boolean;
  emailStatusNotice: string;
  displayName: string;
  avatarUrl: string | null;
  locale: string;
  timezone: string;
  createdAt: string;
}

export interface UserSession {
  id: string;
  clientType: "web" | "desktop";
  deviceName: string;
  ipSubnet: string;
  isCurrent: boolean;
  lastSeenAt: string;
  createdAt: string;
}

export interface ProviderSecretItem {
  provider: "gemini" | "openai" | "anthropic";
  keyHint: string;
  createdAt: string;
  updatedAt: string;
}

export interface DesktopAuthAPI {
  login: (credentials: {
    email: string;
    password: string;
    deviceName?: string;
  }) => Promise<{ user: UserProfile }>;
  logout: () => Promise<void>;
  getStoredSession: () => Promise<UserProfile | null>;
}

export interface DesktopAPI {
  getAppVersion: () => Promise<string>;
  getDiagnostics: () => Promise<DiagnosticsInfo>;
  ping: () => Promise<string>;
  auth?: DesktopAuthAPI;
}

export const IPC_CHANNELS = {
  GET_VERSION: "app:get-version",
  GET_DIAGNOSTICS: "app:get-diagnostics",
  PING: "app:ping",
  AUTH_LOGIN: "app:auth-login",
  AUTH_LOGOUT: "app:auth-logout",
  AUTH_GET_STORED_SESSION: "app:auth-get-stored-session",
} as const;

export type IPCChannel = (typeof IPC_CHANNELS)[keyof typeof IPC_CHANNELS];

declare global {
  interface Window {
    desktopAPI?: DesktopAPI;
  }
}
