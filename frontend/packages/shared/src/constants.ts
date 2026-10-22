export const APP_METADATA = {
  name: "VRMMotionGeneration Platform",
  shortName: "VRM Platform",
  version: "0.1.0",
  description: "Unified Web and Electron Desktop Application Foundation",
  repositoryUrl: "https://github.com/DungTran1201/VRMMotionGeneration",
  author: "Operation Dev",
  license: "MIT",
} as const;

export const DEFAULT_SETTINGS = {
  theme: "dark" as const,
  telemetryEnabled: false,
  logLevel: "info" as const,
};
