import { describe, it, expect } from "vitest";
import { IPC_CHANNELS } from "@vrm/platform-contracts";
import { APP_METADATA } from "@vrm/shared";

describe("Desktop IPC Contract & Channels", () => {
  it("exposes well-defined IPC channels without wildcards", () => {
    expect(IPC_CHANNELS.GET_VERSION).toBe("app:get-version");
    expect(IPC_CHANNELS.GET_DIAGNOSTICS).toBe("app:get-diagnostics");
    expect(IPC_CHANNELS.PING).toBe("app:ping");
    expect(IPC_CHANNELS.AUTH_LOGIN).toBe("app:auth-login");
    expect(IPC_CHANNELS.AUTH_LOGOUT).toBe("app:auth-logout");
    expect(IPC_CHANNELS.AUTH_GET_STORED_SESSION).toBe(
      "app:auth-get-stored-session",
    );
  });

  it("matches application version constant with semver pattern", () => {
    expect(APP_METADATA.version).toMatch(/^\d+\.\d+\.\d+/);
  });
});
