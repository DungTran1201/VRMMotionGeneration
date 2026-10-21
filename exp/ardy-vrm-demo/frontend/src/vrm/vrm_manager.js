/**
 * VRM Avatar Loader and Animation Retargeting Manager.
 * Supports VRM 1.0 and VRM 0.x humanoid specifications.
 * Uses Three.js GLTFLoader and @pixiv/three-vrm.
 */

export class VrmManager {
  /**
   * @param {object} THREE - Three.js core library
   * @param {THREE.Object3D} scene - Parent group/scene to attach avatarRoot
   * @param {class} GLTFLoader - Three.js GLTFLoader
   * @param {class} VRMLoaderPlugin - @pixiv/three-vrm VRMLoaderPlugin
   * @param {object} [VRMUtils] - @pixiv/three-vrm VRMUtils (rotateVRM0, deepDispose)
   */
  constructor(THREE, scene, GLTFLoader, VRMLoaderPlugin, VRMUtils = null) {
    this.THREE = THREE;
    this.scene = scene;
    this.GLTFLoader = GLTFLoader;
    this.VRMLoaderPlugin = VRMLoaderPlugin;
    this.VRMUtils = VRMUtils;

    // Presentation container distinct from raw animation bones
    this.avatarRoot = new THREE.Group();
    this.avatarRoot.name = 'VRM_Avatar_Root';
    this.scene.add(this.avatarRoot);

    this.currentVrm = null;
    this.boneNodes = {}; // Cached mapping of normalized humanoid bone nodes
    this.hipsNode = null;
    this.vrmMotionData = null; // { bones: { [bone]: [[x,y,z,w], ...] }, root_translation: [[x,y,z], ...] }
    this.isLoaded = false;
    this.currentLoadToken = 0;
    this.currentMetadata = null;
    this.maxFileSizeBytes = 100 * 1024 * 1024; // 100 MB configurable limit
  }

  setMotionData(vrmMotionData) {
    this.vrmMotionData = vrmMotionData;
  }

  /**
   * Loads a VRM avatar file asynchronously with full error boundary and lifecycle validation.
   * @param {File|Blob} file - The .vrm file selected by the user
   * @param {Function} [onProgress] - Optional progress callback: (percent: number|null) => void
   * @param {Function} [onSuccess] - Optional legacy success callback: (metadata: object) => void
   * @param {Function} [onError] - Optional legacy error callback: (err: Error) => void
   * @returns {Promise<{ vrm: object, metadata: object, diagnostics: object }>}
   */
  async loadFromFile(file, onProgress, onSuccess, onError) {
    try {
      // 1. Input validation
      if (!file) {
        throw new Error('No file provided. Please select a .vrm avatar file.');
      }

      if (!file.name || !file.name.toLowerCase().endsWith('.vrm')) {
        throw new Error('Invalid file format. Only .vrm files are supported.');
      }

      if (file.size === 0) {
        throw new Error('The selected VRM file is empty (0 bytes).');
      }

      if (file.size > this.maxFileSizeBytes) {
        const mbLimit = (this.maxFileSizeBytes / (1024 * 1024)).toFixed(0);
        throw new Error(`File size (${(file.size / (1024 * 1024)).toFixed(1)} MB) exceeds the ${mbLimit} MB limit.`);
      }

      // 2. Race condition protection with atomic load token
      const loadToken = ++this.currentLoadToken;

      // 3. Create blob URL and prepare loader
      const objectUrl = URL.createObjectURL(file);

      const loader = new this.GLTFLoader();
      loader.crossOrigin = 'anonymous';
      loader.register((parser) => new this.VRMLoaderPlugin(parser));

      let gltf;
      try {
        gltf = await loader.loadAsync(objectUrl, (event) => {
          if (this.currentLoadToken !== loadToken) return;
          if (onProgress) {
            if (event && event.lengthComputable && event.total > 0) {
              const percent = Math.min(100, Math.round((event.loaded / event.total) * 100));
              onProgress(percent);
            } else {
              onProgress(null); // Indeterminate progress
            }
          }
        });
      } finally {
        // Always revoke object URL once Three.js parses the buffer
        URL.revokeObjectURL(objectUrl);
      }

      // Verify token has not been superseded by a subsequent load
      if (this.currentLoadToken !== loadToken) {
        if (gltf?.userData?.vrm?.scene) {
          this.disposeObject(gltf.userData.vrm.scene);
        }
        return null;
      }

      // 4. Validate VRM humanoid metadata presence
      const vrm = gltf.userData.vrm;
      if (!vrm) {
        throw new Error(
          'GLTF model loaded successfully, but VRM humanoid metadata was not detected. Ensure the file is a valid VRM avatar, not a generic glTF/GLB asset.'
        );
      }

      // 5. Cleanly dispose previous avatar before mounting new one
      this.disposeCurrent();

      this.currentVrm = vrm;
      this.avatarRoot.add(vrm.scene);

      // 6. Version detection & orientation handling
      // VRM 0.x models face +Z (away from camera). VRMUtils.rotateVRM0 turns VRM 0.x models to face -Z (glTF standard).
      // VRM 1.0 models already face -Z per glTF specification. Do NOT rotate VRM 1.0 models.
      const metaVersion = vrm.meta?.metaVersion || (vrm.meta?.vrmVersion?.startsWith('0') ? '0' : '1');
      if (metaVersion === '0' && this.VRMUtils?.rotateVRM0) {
        this.VRMUtils.rotateVRM0(vrm);
      }

      // 7. Bounding Box, Centering, and Foot Grounding
      vrm.scene.updateMatrixWorld(true);
      const box = new this.THREE.Box3().setFromObject(vrm.scene);
      const size = new this.THREE.Vector3();
      box.getSize(size);
      const center = new this.THREE.Vector3();
      box.getCenter(center);

      let groundOffsetY = 0;
      let centerOffsetX = 0;
      let centerOffsetZ = 0;

      if (isFinite(box.min.y) && isFinite(size.y) && size.y > 0.001) {
        // Ground feet to floor y = 0 and center horizontally in avatarRoot
        groundOffsetY = -box.min.y;
        centerOffsetX = -center.x;
        centerOffsetZ = -center.z;
        vrm.scene.position.set(centerOffsetX, groundOffsetY, centerOffsetZ);
        vrm.scene.updateMatrixWorld(true);
      }

      // 8. Humanoid Bone Inspection & Caching
      this.boneNodes = {};
      const requiredBones = [
        'hips', 'spine', 'head',
        'leftUpperLeg', 'leftLowerLeg', 'leftFoot',
        'rightUpperLeg', 'rightLowerLeg', 'rightFoot',
        'leftUpperArm', 'leftLowerArm', 'leftHand',
        'rightUpperArm', 'rightLowerArm', 'rightHand'
      ];
      const standardBones = [
        'hips', 'spine', 'chest', 'upperChest', 'neck', 'head',
        'leftShoulder', 'leftUpperArm', 'leftLowerArm', 'leftHand',
        'rightShoulder', 'rightUpperArm', 'rightLowerArm', 'rightHand',
        'leftUpperLeg', 'leftLowerLeg', 'leftFoot', 'leftToes',
        'rightUpperLeg', 'rightLowerLeg', 'rightFoot', 'rightToes'
      ];

      const missingRequired = [];
      if (vrm.humanoid) {
        for (const boneName of standardBones) {
          const node = vrm.humanoid.getNormalizedBoneNode(boneName);
          if (node) {
            this.boneNodes[boneName] = node;
          }
        }
        for (const boneName of requiredBones) {
          if (!this.boneNodes[boneName]) {
            missingRequired.push(boneName);
          }
        }
        this.hipsNode = vrm.humanoid.getNormalizedBoneNode('hips');
        if (this.hipsNode && this.hipsNode.position) {
          this.restHipsPosition = typeof this.hipsNode.position.clone === 'function'
            ? this.hipsNode.position.clone()
            : new this.THREE.Vector3(this.hipsNode.position.x || 0, this.hipsNode.position.y || 0, this.hipsNode.position.z || 0);
        }
      }

      this.isLoaded = true;

      // 9. Structured Metadata and Diagnostics
      const meta = vrm.meta || {};
      const authorText = meta.authors
        ? (Array.isArray(meta.authors) ? meta.authors.join(', ') : meta.authors)
        : (meta.author || 'Unknown');

      const metadata = {
        name: meta.title || file.name.replace(/\.[^/.]+$/, ''),
        author: authorText,
        version: metaVersion === '0' ? 'VRM 0.x' : 'VRM 1.0',
        fileSizeMB: (file.size / (1024 * 1024)).toFixed(2),
        heightMeters: size.y ? size.y.toFixed(2) : '1.60',
      };

      const diagnostics = {
        boneCount: Object.keys(this.boneNodes).length,
        missingRequiredBones: missingRequired,
        groundOffsetY: groundOffsetY.toFixed(3),
        bounds: {
          width: size.x.toFixed(2),
          height: size.y.toFixed(2),
          depth: size.z.toFixed(2),
        },
      };

      this.currentMetadata = metadata;

      if (onSuccess) onSuccess(metadata);
      return { vrm, metadata, diagnostics };
    } catch (err) {
      this.isLoaded = false;
      this.currentVrm = null;
      if (onError) onError(err);
      throw err;
    }
  }

  updateFrame(frameIndex, delta = 0.016) {
    if (!this.currentVrm || !this.vrmMotionData) return;

    const { bones, root_translation } = this.vrmMotionData;
    if (!bones) return;

    // Apply retargeted bone rotations
    for (const [boneName, node] of Object.entries(this.boneNodes)) {
      const quatArray = bones[boneName];
      if (quatArray && quatArray.length > 0) {
        const clampedFrame = Math.max(0, Math.min(frameIndex, quatArray.length - 1));
        const [x, y, z, w] = quatArray[clampedFrame];
        node.quaternion.set(x, y, z, w);
      }
    }

    // Apply hips root translation relative to avatar's bind pose,
    // accounting for vrm.scene orientation (e.g. rotateVRM0) so displacement
    // advances along the exact world vector matching the skeleton
    if (this.hipsNode && root_translation && root_translation.length > 0) {
      const clampedFrame = Math.max(0, Math.min(frameIndex, root_translation.length - 1));
      const [rx, ry, rz] = root_translation[clampedFrame];
      const [r0x, r0y, r0z] = root_translation[0];

      // World displacement relative to frame 0
      const dx = rx - r0x;
      const dy = ry - r0y;
      const dz = rz - r0z;

      // Transform world displacement into vrm.scene local coordinate frame
      const disp = new this.THREE.Vector3(dx, dy, dz);
      if (this.currentVrm.scene?.quaternion) {
        disp.applyQuaternion(this.currentVrm.scene.quaternion.clone().invert());
      }

      const basePos = this.restHipsPosition || new this.THREE.Vector3(0, ry, 0);
      this.hipsNode.position.set(
        basePos.x + disp.x,
        basePos.y + disp.y,
        basePos.z + disp.z
      );
    }

    // Advance VRM spring bones, expressions, and lookAt exactly once per frame
    this.currentVrm.update(delta);
  }

  disposeObject(object) {
    if (!object) return;
    if (this.VRMUtils?.deepDispose) {
      this.VRMUtils.deepDispose(object);
    } else {
      object.traverse((child) => {
        if (child.geometry) child.geometry.dispose();
        if (child.skeleton) child.skeleton.dispose();
        if (child.material) {
          if (Array.isArray(child.material)) {
            child.material.forEach((m) => {
              if (m.map) m.map.dispose();
              m.dispose();
            });
          } else {
            if (child.material.map) child.material.map.dispose();
            child.material.dispose();
          }
        }
      });
    }
  }

  disposeCurrent() {
    if (this.currentVrm) {
      if (this.currentVrm.scene) {
        this.avatarRoot.remove(this.currentVrm.scene);
        this.disposeObject(this.currentVrm.scene);
      }
      if (typeof this.currentVrm.dispose === 'function') {
        try {
          this.currentVrm.dispose();
        } catch (_) {}
      }
      this.currentVrm = null;
      this.boneNodes = {};
      this.hipsNode = null;
      this.restHipsPosition = null;
      this.isLoaded = false;
      this.currentMetadata = null;
    }
  }

  dispose() {
    this.disposeCurrent();
    if (this.avatarRoot && this.scene) {
      this.scene.remove(this.avatarRoot);
    }
  }
}
