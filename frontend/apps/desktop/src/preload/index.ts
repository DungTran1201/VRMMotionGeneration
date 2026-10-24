import { contextBridge, ipcRenderer } from "electron";
import {
  IPC_CHANNELS,
  type DesktopAPI,
  type DiagnosticsInfo,
} from "@vrm/platform-contracts";

const desktopAPI: DesktopAPI = {
  getAppVersion: (): Promise<string> => {
    return ipcRenderer.invoke(IPC_CHANNELS.GET_VERSION);
  },
  getDiagnostics: (): Promise<DiagnosticsInfo> => {
    return ipcRenderer.invoke(IPC_CHANNELS.GET_DIAGNOSTICS);
  },
  ping: (): Promise<string> => {
    return ipcRenderer.invoke(IPC_CHANNELS.PING);
  },
  auth: {
    login: (credentials) =>
      ipcRenderer.invoke(IPC_CHANNELS.AUTH_LOGIN, credentials),
    logout: () => ipcRenderer.invoke(IPC_CHANNELS.AUTH_LOGOUT),
    getStoredSession: () =>
      ipcRenderer.invoke(IPC_CHANNELS.AUTH_GET_STORED_SESSION),
  },
};

contextBridge.exposeInMainWorld("desktopAPI", desktopAPI);
