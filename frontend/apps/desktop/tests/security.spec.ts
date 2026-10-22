import { describe, it, expect } from "vitest";
import { CSP_HEADER, validateIpcSender } from "../src/main/security.js";

describe("Desktop Security Invariants", () => {
  it("enforces a strict Content Security Policy restricting script execution", () => {
    expect(CSP_HEADER).toContain("default-src 'self'");
    expect(CSP_HEADER).toContain("script-src 'self'");
    expect(CSP_HEADER).not.toContain("'unsafe-eval'");
  });

  it("rejects IPC events from null or destroyed browser windows", () => {
    const mockSender = { id: 123 } as any;
    expect(validateIpcSender(mockSender, null)).toBe(false);

    const mockDestroyedWindow = {
      isDestroyed: () => true,
      webContents: { id: 123 },
    } as any;
    expect(validateIpcSender(mockSender, mockDestroyedWindow)).toBe(false);
  });

  it("validates IPC events originating from the main window webContents", () => {
    const mockSender = { id: 456 } as any;
    const mockActiveWindow = {
      isDestroyed: () => false,
      webContents: { id: 456 },
    } as any;
    expect(validateIpcSender(mockSender, mockActiveWindow)).toBe(true);

    const mockForeignSender = { id: 789 } as any;
    expect(validateIpcSender(mockForeignSender, mockActiveWindow)).toBe(false);
  });
});
