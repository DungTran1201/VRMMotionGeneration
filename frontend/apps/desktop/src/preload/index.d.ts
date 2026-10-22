import type { DesktopAPI } from "@vrm/platform-contracts";

declare global {
  interface Window {
    desktopAPI: DesktopAPI;
  }
}

export {};
