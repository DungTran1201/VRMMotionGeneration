# Canonical System Schemas

This directory contains versioned, machine-readable JSON Schema definitions for application contracts, inter-process communication (IPC), settings, and system diagnostics.

> **Note**: This directory was transitioned from `models/` to `schemas/` via ADR-0001 to prevent confusion with machine learning weights or checkpoints.

---

## Schema Catalog

1. **`desktop-ipc.schema.json`**: Defines valid IPC channel names, request payloads, and response envelopes for the Electron contextBridge interface.
2. **`system-diagnostics.schema.json`**: Defines standard operating metrics, runtime environment tags (`web` vs `electron`), and system capabilities.
3. **`app-settings.schema.json`**: Defines user preferences, theme selection (`dark`, `light`, `system`), and platform behavior options.
