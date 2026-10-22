import { describe, it, expect } from "vitest";
import { APP_METADATA, DEFAULT_SETTINGS } from "@vrm/shared";
import { detectPlatform, createWebFallbackAPI } from "@vrm/app-core";

describe("Workspace Contracts and Architecture Integrity", () => {
  it("defines valid application metadata and defaults", () => {
    expect(APP_METADATA.name).toBe("VRMMotionGeneration Platform");
    expect(APP_METADATA.license).toBe("MIT");
    expect(DEFAULT_SETTINGS.theme).toBe("dark");
  });

  it("detects Web platform when window.desktopAPI is not injected", () => {
    expect(detectPlatform()).toBe("web");
  });

  it("generates compliant fallback diagnostics in browser environment", async () => {
    const fallbackAPI = createWebFallbackAPI();
    const diagnostics = await fallbackAPI.getDiagnostics();

    expect(diagnostics.platform).toBe("web");
    expect(diagnostics.appVersion).toBe(APP_METADATA.version);
    expect(diagnostics.capabilities.desktopIntegration).toBe(false);
    expect(diagnostics.capabilities.fileSystemAccess).toBe(false);

    const ping = await fallbackAPI.ping();
    expect(ping).toBe("pong:web-fallback");
  });
});
