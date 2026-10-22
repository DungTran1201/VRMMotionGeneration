import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import App from "../src/App.vue";
import { useAppStore } from "@vrm/app-core";

describe("Web Application Foundation Mount", () => {
  it("renders successfully and displays platform as Web Client", () => {
    const wrapper = mount(App);
    expect(wrapper.text()).toContain("VRM Platform");
    expect(wrapper.text()).toContain("Web Client");
  });

  it("switches between navigation tabs smoothly", async () => {
    const wrapper = mount(App);
    const store = useAppStore();

    // Default tab is overview
    expect(store.state.currentTab).toBe("overview");
    expect(wrapper.text()).toContain("Architecture Reset Complete");

    // Switch to settings
    await wrapper.find("#nav-tab-settings").trigger("click");
    expect(store.state.currentTab).toBe("settings");
    expect(wrapper.text()).toContain("Application Settings");

    // Switch to diagnostics
    await wrapper.find("#nav-tab-diagnostics").trigger("click");
    expect(store.state.currentTab).toBe("diagnostics");
    expect(wrapper.text()).toContain("System Diagnostics & Runtime State");
  });

  it("runs web fallback diagnostics with correct platform capability flags", async () => {
    const store = useAppStore();
    await store.loadDiagnostics();

    expect(store.state.diagnostics).not.toBeNull();
    expect(store.state.diagnostics?.platform).toBe("web");
    expect(store.state.diagnostics?.capabilities.desktopIntegration).toBe(
      false,
    );
  });
});
