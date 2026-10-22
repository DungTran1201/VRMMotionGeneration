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
};

contextBridge.exposeInMainWorld("desktopAPI", desktopAPI);
