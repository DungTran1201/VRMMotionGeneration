# Full-Page 3D Workspace Design & Floating Tool Architecture

## 1. Visual Direction & Spatial Layout

The ARDY Motion Lab user interface has been refactored from a card-heavy dashboard into a **full-page, full-viewport 3D workspace** occupying `100dvw × 100dvh`.

### Core Design Principles:
1. **The 3D World is the Primary Surface:**
   The canvas is full-bleed with no scrollbars over the stage. Floor grid, lighting, and coordinate systems serve as the primary visual anchor.
2. **Glassmorphic Floating Windows:**
   Tool panels float over the 3D scene using high-contrast dark translucent glass (`rgba(15, 23, 42, 0.88)` with `backdrop-filter: blur(18px)`).
3. **Restrained Technical Cybernetic Aesthetic:**
   High contrast technical theme with restrained cyan (`#06b6d4`), sky blue (`#38bdf8`), and emerald (`#10b981`) accents.

---

## 2. Shared 3D World Architecture

Rather than maintaining separate viewports with independent cameras and renderers, the entire application operates within a single `THREE.Scene`:

```
THREE.Scene (ARDY_SharedStage)
 ├── Directional Lights (Key, Fill, Rim) & AmbientLight
 ├── World Floor Grid (12m x 12m, 48 divisions, y = 0.0)
 ├── Ground Contact Ring Markers (-0.75m cyan, +0.75m emerald)
 └── StageRoot (THREE.Group)
      ├── SkeletonComparisonRoot (position: x = -0.75, y = 0, z = 0)
      │    └── CoreSkeleton27 LineSegments & Joint Meshes
      └── VRMComparisonRoot (position: x = +0.75, y = 0, z = 0)
           └── VRM_Avatar_Root (Grounding offset applied)
                └── vrm.scene
```

### Camera & Framing Controls
- **Default Position:** `(0, 1.25, 3.2)`, target at `(0, 0.9, 0)`.
- **Frame Avatar:** Centers target on `(0.75, 0.9, 0)`, camera at `(0.75, 1.15, 2.3)`.
- **Frame Skeleton:** Centers target on `(-0.75, 0.9, 0)`, camera at `(-0.75, 1.15, 2.3)`.
- **Frame Both:** Returns to default balanced perspective.

---

## 3. Floating Tool Windows Specifications

The workspace features two customizable floating tool windows managed by `FloatingWindow`:

### Window 1: Motion Controls (`#winMotionControls`)
- **Location:** Floating top-left (default `top: 60px; left: 24px; width: 380px;`).
- **Capabilities:**
  - **Draggable:** Via title bar using Pointer Events with viewport clamping.
  - **Resizable:** Via diagonal resize handle at bottom-right (min-width: 320px, min-height: 220px).
  - **Collapsible:** Toggle button minimizes window body to a compact 38px title bar.
  - **Adjustable Opacity:** Slider controls window transparency between 40% and 100%.
  - **Close / Reopen:** Close button hides window; topbar "Controls" button restores it.
  - **Event Isolation:** Pointer events inside the window call `e.stopPropagation()`, preventing canvas OrbitControls from activating during window manipulation.
- **Controls Included:**
  - Natural language motion conditioning prompt textarea & preset chips.
  - Duration slider (1.0s to 6.0s) with live frame count calculation at 20 FPS.
  - Loop playback checkbox, Skeleton visibility toggle, Avatar visibility toggle.
  - VRM Avatar loading button & status info badge.
  - Generate Motion & Stop buttons.

### Window 2: Telemetry & Benchmarks (`#winTelemetry`)
- **Location:** Floating top-right (default `top: 60px; right: 24px; width: 320px;`).
- **Capabilities:** Draggable, resizable, collapsible, opacity-controlled, closeable.
- **Metrics Displayed (Truthful Provable Data Only):**
  - Generation status (`Idle`, `Generating`, `Complete`).
  - Active model checkpoint (`ARDY-Core-RP-20FPS-Horizon8`).
  - Duration (Requested vs Actual).
  - Diffusion inference time (ms).
  - Effective generation FPS.
  - Real-Time Factor (RTF).
  - End-to-end latency (ms).
  - Peak VRAM (MB).
  - Live renderer FPS (measured per 500ms).

---

## 4. Synchronized Floating Bottom Timeline Scrubber

- **Location:** Floating over bottom-center (`position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%); width: min(880px, calc(100vw - 32px));`).
- **Features:**
  - Single timeline slider (scrubber) controlling both skeleton joints and VRM bone quaternions.
  - Play / Pause toggle with spacebar keyboard shortcut.
  - Restart button (jumps to frame 1).
  - Time readout: `Frame X / Total (Xs / TotalDuration)`.
  - Playback speed selector: `0.25x`, `0.5x`, `1.0x`, `1.5x`, `2.0x`.
