import { app, BrowserWindow, ipcMain } from "electron";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import os from "node:os";
import { IPC_CHANNELS, type DiagnosticsInfo } from "@vrm/platform-contracts";
import { APP_METADATA } from "@vrm/shared";
import {
  configureSessionSecurity,
  enforceWindowSecurity,
  validateIpcSender,
} from "./security.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let mainWindow: BrowserWindow | null = null;

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    title: APP_METADATA.name,
    backgroundColor: "#0a0e17",
    webPreferences: {
      preload: join(__dirname, "../preload/index.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true,
      allowRunningInsecureContent: false,
      navigateOnDragDrop: false,
    },
  });

  enforceWindowSecurity(mainWindow);

  // In development, if VITE_DEV_SERVER_URL is present, load it; otherwise load local build
  const devUrl = process.env["VITE_DEV_SERVER_URL"];
  if (devUrl) {
    mainWindow.loadURL(devUrl);
  } else {
    mainWindow.loadFile(join(__dirname, "../../dist/index.html"));
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

function registerIpcHandlers(): void {
  ipcMain.handle(IPC_CHANNELS.GET_VERSION, (event) => {
    if (!validateIpcSender(event.sender, mainWindow)) {
      throw new Error("Unauthorized IPC sender");
    }
    return APP_METADATA.version;
  });

  ipcMain.handle(IPC_CHANNELS.GET_DIAGNOSTICS, (event): DiagnosticsInfo => {
    if (!validateIpcSender(event.sender, mainWindow)) {
      throw new Error("Unauthorized IPC sender");
    }
    return {
      platform: "electron",
      appVersion: APP_METADATA.version,
      environment: app.isPackaged ? "production" : "development",
      timestamp: new Date().toISOString(),
      capabilities: {
        desktopIntegration: true,
        fileSystemAccess: true,
        nativeMenus: true,
      },
      os: {
        platform: os.platform(),
        arch: os.arch(),
        release: os.release(),
      },
    };
  });

  ipcMain.handle(IPC_CHANNELS.PING, (event) => {
    if (!validateIpcSender(event.sender, mainWindow)) {
      throw new Error("Unauthorized IPC sender");
    }
    return "pong:electron-main";
  });
}

const gotSingleInstanceLock = app.requestSingleInstanceLock();

if (!gotSingleInstanceLock) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });

  app.whenReady().then(() => {
    configureSessionSecurity();
    registerIpcHandlers();
    createWindow();

    app.on("activate", () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
      }
    });
  });

  app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
      app.quit();
    }
  });
}
