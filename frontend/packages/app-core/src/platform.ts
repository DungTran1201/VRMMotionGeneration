import type {
  DesktopAPI,
  DiagnosticsInfo,
  PlatformType,
} from "@vrm/platform-contracts";
import { APP_METADATA } from "@vrm/shared";

export function isElectronEnvironment(): boolean {
  return (
    typeof window !== "undefined" &&
    window.desktopAPI !== undefined &&
    typeof window.desktopAPI.getDiagnostics === "function"
  );
}

export function detectPlatform(): PlatformType {
  return isElectronEnvironment() ? "electron" : "web";
}

export function createWebFallbackAPI(): DesktopAPI {
  return {
    getAppVersion: async () => APP_METADATA.version,
    getDiagnostics: async (): Promise<DiagnosticsInfo> => {
      const isBrowser = typeof window !== "undefined";
      return {
        platform: "web",
        appVersion: APP_METADATA.version,
        environment:
          process.env.NODE_ENV === "production" ? "production" : "development",
        timestamp: new Date().toISOString(),
        capabilities: {
          desktopIntegration: false,
          fileSystemAccess: false,
          nativeMenus: false,
        },
        os: isBrowser
          ? {
              platform: navigator.platform || "web-browser",
              arch: "unknown",
              release: navigator.userAgent,
            }
          : undefined,
      };
    },
    ping: async () => "pong:web-fallback",
  };
}

export function getPlatformAPI(): DesktopAPI {
  if (isElectronEnvironment() && window.desktopAPI) {
    return window.desktopAPI;
  }
  return createWebFallbackAPI();
}
