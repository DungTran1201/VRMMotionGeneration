# Motion and VRM Avatar Lifecycle Specification

## 1. File Selection and Input Pathways

The VRM loader accepts avatar inputs through two identical code pathways:
1. **File Picker:** Clicking the "Load / Replace VRM" button triggers the authoritative hidden `<input type="file" id="vrmFileInput" accept=".vrm">`.
2. **Stage Drag & Drop:** Dragging any `.vrm` file over the browser viewport activates `#stageDropOverlay`. Dropping the file forwards `dataTransfer.files[0]` directly to `loadVrmFile()`.

Both pathways funnel through `VrmManager.loadFromFile(file)`.

---

## 2. Asynchronous Loading Contract

`VrmManager.loadFromFile(file)` guarantees a strict Promise-returning contract:

```typescript
loadFromFile(
  file: File | Blob,
  onProgress?: (percent: number | null) => void
): Promise<{
  vrm: VRM;
  metadata: {
    name: string;
    author: string;
    version: 'VRM 0.x' | 'VRM 1.0';
    fileSizeMB: string;
    heightMeters: string;
  };
  diagnostics: {
    boneCount: number;
    missingRequiredBones: string[];
    groundOffsetY: string;
    bounds: { width: string; height: string; depth: string };
  };
}>;
```

### Lifecycle Steps:
1. **Input Validation:**
   - Null check -> rejects with `"No file provided"`.
   - File extension -> rejects non-`.vrm` files.
   - Empty check -> rejects 0-byte files.
   - Size limit -> rejects files exceeding 100 MB.
2. **Race Condition Prevention:**
   - Increments `currentLoadToken`.
   - If another file is chosen while parsing is underway, the superseded load token cancels mounting and discards parsed resources.
3. **Blob URL & GLTFLoader:**
   - Creates `URL.createObjectURL(file)`.
   - Executes `loader.loadAsync()`.
   - Enclosed in `finally { URL.revokeObjectURL(objectUrl); }` to avoid object URL memory leaks.
4. **VRM Humanoid Verification:**
   - Confirms `gltf.userData.vrm` exists.
   - If missing, rejects with descriptive guidance distinguishing general GLTF/GLB models from VRM humanoids.
5. **Orientation & Grounding:**
   - Detects `metaVersion`. Applies `VRMUtils.rotateVRM0(vrm)` if and only if version is `'0'`.
   - Computes `Box3`, offsets `position.y = -box.min.y` to align feet to world floor (`y = 0.0`), and centers horizontal origin.
6. **Bone Caching & Motion Binding:**
   - Normalizes and caches humanoid bone nodes (`hips`, `spine`, `chest`, limbs).
   - If a motion sequence was already generated, binds it immediately to the new avatar without requiring a re-run of inference.

---

## 3. Resource Disposal and Replacement

When an avatar is replaced or removed:
- `vrm.scene` is detached from `avatarRoot`.
- `VRMUtils.deepDispose(vrm.scene)` traverses and disposes all geometries, materials, skeletons, and textures.
- `vrm.dispose()` is called if available.
- All cached bone node references and hips references are set to null.
- Object URLs are revoked.

---

## 4. Single Synchronized Motion Timeline

Both rigs (the 27-joint skeleton and the VRM avatar) consume data from the **same unified motion payload**:
- **Frame Rate:** Canonical 20.0 FPS model rate.
- **Root Translation:** Both rigs use the same `root_translation` trajectory (meters).
- **Update Frequency:** `vrm.update(delta)` is invoked exactly once per animation frame inside the main render loop.
- **Rig Toggles:** Hiding the skeleton does not pause or disrupt avatar playback.
