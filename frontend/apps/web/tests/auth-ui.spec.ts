import { describe, it, expect, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import App from "../src/App.vue";
import { useAppStore } from "@vrm/app-core";

describe("Web Application Authentication UI & Navigation Flow", () => {
  beforeEach(() => {
    const store = useAppStore();
    store.setTab("overview");
    store.state.isAuthenticated = false;
    store.state.user = null;
    store.state.sessions = [];
    store.state.secrets = [];
    store.state.authError = null;
    store.state.authNotice = null;
  });

  it("renders unauthenticated state on overview with sign in and register buttons", () => {
    const wrapper = mount(App);
    const store = useAppStore();

    expect(store.state.isAuthenticated).toBe(false);
    expect(wrapper.find("#overview-signin-btn").exists()).toBe(true);
    expect(wrapper.find("#overview-signup-btn").exists()).toBe(true);
    expect(wrapper.find("#nav-signin-btn").exists()).toBe(true);
    expect(wrapper.find("#nav-signup-btn").exists()).toBe(true);
  });

  it("navigates to Sign In view and verifies form elements", async () => {
    const wrapper = mount(App);
    const store = useAppStore();

    await wrapper.find("#nav-signin-btn").trigger("click");
    expect(store.state.currentTab).toBe("signin");
    expect(wrapper.text()).toContain("Welcome Back");
    expect(wrapper.find("#signin-email").exists()).toBe(true);
    expect(wrapper.find("#signin-password").exists()).toBe(true);
    expect(wrapper.find("#signin-submit-btn").exists()).toBe(true);
  });

  it("navigates to Sign Up view and displays NIST 15-char requirement and unverified notice", async () => {
    const wrapper = mount(App);
    const store = useAppStore();

    await wrapper.find("#nav-signup-btn").trigger("click");
    expect(store.state.currentTab).toBe("signup");
    expect(wrapper.text()).toContain("Create Account");
    expect(wrapper.text()).toContain("No Email Verification Required");
    expect(wrapper.text()).toContain(
      "15 characters minimum (NIST SP 800-63B-4 standard)",
    );
    expect(wrapper.find("#signup-email").exists()).toBe(true);
    expect(wrapper.find("#signup-password").exists()).toBe(true);
    expect(wrapper.find("#signup-submit-btn").exists()).toBe(true);
  });

  it("dynamically shows auth tabs and profile when user is authenticated", async () => {
    const wrapper = mount(App);
    const store = useAppStore();

    // Simulate login
    store.state.isAuthenticated = true;
    store.state.user = {
      id: "usr_test_1234567890",
      email: "engineer@example.com",
      status: "active",
      emailVerified: false,
      emailStatusNotice: "UNVERIFIED",
      displayName: "Staff Engineer",
      avatarUrl: null,
      locale: "en-US",
      timezone: "UTC",
      createdAt: new Date().toISOString(),
    };
    store.setTab("overview");

    await wrapper.vm.$nextTick();

    // Nav bar should display auth tabs
    expect(wrapper.find("#nav-tab-profile").exists()).toBe(true);
    expect(wrapper.find("#nav-tab-security").exists()).toBe(true);
    expect(wrapper.find("#nav-tab-secrets").exists()).toBe(true);
    expect(wrapper.find("#nav-user-pill").text()).toContain("Staff Engineer");
    expect(wrapper.find("#nav-signout-btn").exists()).toBe(true);

    // Overview should display welcome banner with unverified email badge
    expect(wrapper.text()).toContain("Staff Engineer");
    expect(wrapper.text()).toContain("Unverified Contact Address");

    // Navigate to Profile view
    await wrapper.find("#nav-tab-profile").trigger("click");
    expect(store.state.currentTab).toBe("profile");
    expect(wrapper.text()).toContain("Account Profile");
    expect(wrapper.text()).toContain("engineer@example.com");

    // Navigate to Security view
    await wrapper.find("#nav-tab-security").trigger("click");
    expect(store.state.currentTab).toBe("security");
    expect(wrapper.text()).toContain("Account Security");
    expect(wrapper.text()).toContain("Active Devices & Sessions");
    expect(wrapper.text()).toContain("Change Password");

    // Navigate to AI Secrets view
    await wrapper.find("#nav-tab-secrets").trigger("click");
    expect(store.state.currentTab).toBe("secrets");
    expect(wrapper.text()).toContain("AI Provider Key Vault");
    expect(wrapper.text()).toContain("Hardware / KMS Envelope Encryption");

    // Click Sign Out
    await wrapper.find("#nav-signout-btn").trigger("click");
    await new Promise((r) => setTimeout(r, 20));
    expect(store.state.isAuthenticated).toBe(false);
    expect(store.state.user).toBeNull();
  });
});
