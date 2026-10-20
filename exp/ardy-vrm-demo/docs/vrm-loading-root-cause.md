# Root Cause Analysis: VRM Avatar Loading Failures & Architectural Diagnostics

## 1. Executive Summary

This investigation diagnoses the technical root causes of VRM avatar loading failures and orientation anomalies in the ARDY Motion Lab demonstration (`exp/ardy-vrm-demo`). Prior to this fix, user-selected `.vrm` avatars frequently failed silently, became stuck in an indeterminate "Loading..." state, loaded backwards, or appeared visually broken/buried below the floor grid.

All findings below are classified as `VERIFIED` with direct code and runtime evidence.

---

## 2. Evidence-Based Root Cause Breakdown

### Root Cause 1 (VERIFIED): Asynchronous Uncaught Exception in `GLTFLoader.load()` Callback
- **File Reference:** `exp/ardy-vrm-demo/frontend/src/vrm/vrm_manager.js` (legacy lines 43–47)
- **Mechanism:**
  ```javascript
  loader.load(
    objectUrl,
    (gltf) => {
      const vrm = gltf.userData.vrm;
      if (!vrm) {
        throw new Error('GLTF loaded but VRM metadata was not detected.');
      }
      // ...
    }
  );
  ```
- **Observed Behavior:**
  In JavaScript, exceptions thrown inside asynchronous callbacks passed to `loader.load()` are not caught by the synchronous `try...catch` enclosing `loadFromFile()`. Furthermore, Three.js `GLTFLoader` does not forward exceptions raised in the `onLoad` handler to the `onError` callback.
- **Consequence:**
  The throw turns into an unhandled rejection. The error was never surfaced to the UI, `vrmEmptyState` remained hidden, and the status badge remained stuck showing `Parsing...` indefinitely.
- **Chosen Fix:**
  Transitioned to a modern Promise-based contract (`loadFromFile(file): Promise<{ vrm, metadata, diagnostics }>`) utilizing `loader.loadAsync()` inside a guarded `try...catch...finally` block.

---

### Root Cause 2 (VERIFIED): Unconditional 180° Model Inversion (`Math.PI`) Breaking VRM 1.0 Models
- **File Reference:** `exp/ardy-vrm-demo/frontend/src/vrm/vrm_manager.js` (legacy line 54)
- **Mechanism:**
  ```javascript
  vrm.scene.rotation.y = Math.PI; // Face front towards viewer at +Z
  ```
- **Specification Context:**
  - In standard **glTF 2.0**: +Y is Up, +Z is Back (towards viewer), -Z is Forward. A camera situated at `+Z` looking down `-Z` looks directly at the face of an object oriented toward `-Z`.
  - In **VRM 0.0**: The specification legacy defined +Z as forward (facing away from the standard glTF forward).
  - In **VRM 1.0**: The specification unified with glTF 2.0, defining `-Z` as forward. A VRM 1.0 avatar already faces front towards a camera placed at `+Z`.
- **Consequence:**
  Applying `Math.PI` unconditionally turned VRM 1.0 avatars backwards, causing them to present their backs to the user during animation playback.
- **Chosen Fix:**
  Inspect `vrm.meta?.metaVersion`. Apply `@pixiv/three-vrm`'s utility `VRMUtils.rotateVRM0(vrm)` **only** when `metaVersion === '0'`. VRM 1.0 models are preserved in their native canonical coordinate frame.

---

### Root Cause 3 (VERIFIED): Absence of Bounding Box Computation, Normalization & Foot Grounding
- **File Reference:** `exp/ardy-vrm-demo/frontend/src/vrm/vrm_manager.js` (legacy lines 50–55)
- **Mechanism:**
  The loader attached `vrm.scene` directly to the Three.js scene hierarchy without computing `THREE.Box3` or measuring model dimensions.
- **Consequence:**
  Avatars authored with origins at the pelvis/hips or with arbitrary root offsets were positioned with feet buried below the stage floor grid (`y = 0`) or hovering above it.
- **Chosen Fix:**
  Execute `vrm.scene.updateMatrixWorld(true)` and compute `Box3`. Dynamically offset `vrm.scene.position.y = -box.min.y` and center `x`/`z` inside an `avatarRoot` container, ensuring the avatar's soles align precisely with the floor grid (`y = 0.0`) without altering normalized humanoid bone nodes.

---

### Root Cause 4 (VERIFIED): Dual Viewports vs. Shared Comparison World
- **File Reference:** `exp/ardy-vrm-demo/frontend/src/scene/viewer_stage.js` (legacy lines 8–23)
- **Mechanism:**
  Created two independent `THREE.Scene`, `THREE.PerspectiveCamera`, `THREE.WebGLRenderer`, and `OrbitControls` instances, rendering into two separated dashboard cards (`#skeletonCanvas`, `#vrmCanvas`).
- **Consequence:**
  Comparison was unnatural due to separate camera angles, independent orbital motion, separate floor grids, and card-heavy dashboard styling.
- **Chosen Fix:**
  Refactored to a single unified `ViewerStage` with one scene, one camera, one renderer, and one world floor grid. Skeleton and VRM avatar are mounted side-by-side with explicit horizontal comparison offsets (`x = -0.75m` and `x = +0.75m`).

---

### Root Cause 5 (VERIFIED): Duplicate File Inputs and Fragile DOM Dispatch
- **File Reference:** `exp/ardy-vrm-demo/frontend/index.html` (legacy lines 99 and 163)
- **Mechanism:**
  Contained two separate `<input type="file">` elements, with an inline JavaScript handler:
  `onchange="document.getElementById('vrmFileInput').files = this.files; ..."`
- **Consequence:**
  Caused cross-browser synchronization issues, double event triggers, and swallowed errors during drag-and-drop.
- **Chosen Fix:**
  A single authoritative hidden `<input type="file" id="vrmFileInput" accept=".vrm">`, invoked programmatically via both the UI button and viewport drag-and-drop.

---

### Root Cause 6 (VERIFIED): Multiple Three.js Instance Collision via CDN Import Maps
- **File Reference:** `exp/ardy-vrm-demo/frontend/index.html` (legacy import map)
- **Mechanism:**
  `@pixiv/three-vrm@3.3.4` imported from `esm.sh` defaulted to pulling an internal bundle of Three.js, conflicting with the app's top-level `three@0.170.0`.
- **Consequence:**
  Risk of `instanceof` check failures between Three.js classes across modules and console warnings regarding multiple Three.js instances.
- **Chosen Fix:**
  Pinned `@pixiv/three-vrm` with explicit external flag:
  `"@pixiv/three-vrm": "https://esm.sh/@pixiv/three-vrm@3.3.4?external=three"`. Both the app and the loader plugin now reference the exact same Three.js r170 singleton.

---

## 3. Alternatives Considered

| Alternative | Evaluation | Decision |
|---|---|---|
| Complete toolchain migration to Vite + NPM bundling | Introduces new build steps, `package.json`, and changes how backend serves static files. Unnecessary since CDN ESM import map works reliably when pinned with `?external=three`. | **Rejected**: Kept lightweight CDN architecture with pinned versions. |
| Server-side VRM parsing & validation via Python | Adds heavy Python glTF/VRM dependencies, consumes server memory, and uploads entire avatars to server. | **Rejected**: Client-side parsing via Three.js + three-vrm is faster and privacy-preserving. |
| Automatic avatar rescale to fixed 1.70m | Destroys natural avatar proportions and author intent. | **Rejected**: Retained model scale; applied foot grounding and camera auto-framing instead. |
