/**
 * VRM 1.0 Avatar Loader and Animation Retargeting Manager.
 * Uses Three.js GLTFLoader and @pixiv/three-vrm.
 */

export class VrmManager {
  constructor(THREE, scene, GLTFLoader, VRMLoaderPlugin) {
    this.THREE = THREE;
    this.scene = scene;
    this.GLTFLoader = GLTFLoader;
    this.VRMLoaderPlugin = VRMLoaderPlugin;

    this.currentVrm = null;
    this.currentObjectURL = null;
    this.boneNodes = {}; // Cached mapping of normalized humanoid bone nodes
    this.hipsNode = null;
    this.vrmMotionData = null; // { bones: { [bone]: [[x,y,z,w], ...] }, root_translation: [[x,y,z], ...] }
    this.isLoaded = false;
  }

  setMotionData(vrmMotionData) {
    this.vrmMotionData = vrmMotionData;
  }

  async loadFromFile(file, onProgress, onSuccess, onError) {
    if (!file || !file.name.toLowerCase().endsWith('.vrm')) {
      if (onError) onError(new Error('Invalid file format. Please select a .vrm file.'));
      return;
    }

    try {
      this.disposeCurrent();

      const objectUrl = URL.createObjectURL(file);
      this.currentObjectURL = objectUrl;

      const loader = new this.GLTFLoader();
      loader.crossOrigin = 'anonymous';
      loader.register((parser) => new this.VRMLoaderPlugin(parser));

      loader.load(
        objectUrl,
        (gltf) => {
          const vrm = gltf.userData.vrm;
          if (!vrm) {
            throw new Error('GLTF loaded but VRM metadata was not detected.');
          }

          this.currentVrm = vrm;
          this.scene.add(vrm.scene);

          // Rotate to face camera if needed (VRM avatars face -Z or +Z)
          // Default VRM humanoid faces +Z
          vrm.scene.rotation.y = Math.PI; // Face front towards viewer at +Z

          // Cache normalized humanoid bone nodes
          this.boneNodes = {};
          if (vrm.humanoid) {
            const standardBones = [
              'hips', 'spine', 'chest', 'upperChest', 'neck', 'head',
              'leftShoulder', 'leftUpperArm', 'leftLowerArm', 'leftHand',
              'rightShoulder', 'rightUpperArm', 'rightLowerArm', 'rightHand',
              'leftUpperLeg', 'leftLowerLeg', 'leftFoot', 'leftToes',
              'rightUpperLeg', 'rightLowerLeg', 'rightFoot', 'rightToes'
            ];

            for (const boneName of standardBones) {
              const node = vrm.humanoid.getNormalizedBoneNode(boneName);
              if (node) {
                this.boneNodes[boneName] = node;
              }
            }
            this.hipsNode = vrm.humanoid.getNormalizedBoneNode('hips');
          }

          this.isLoaded = true;

          const meta = vrm.meta || {};
          const vrmInfo = {
            name: meta.title || file.name,
            author: meta.authors ? (Array.isArray(meta.authors) ? meta.authors.join(', ') : meta.authors) : (meta.author || 'Unknown'),
            version: meta.metaVersion || '1.0',
            fileSizeMB: (file.size / (1024 * 1024)).toFixed(2),
          };

          if (onSuccess) onSuccess(vrmInfo);
        },
        (progress) => {
          if (onProgress && progress.total > 0) {
            const percent = Math.round((progress.loaded / progress.total) * 100);
            onProgress(percent);
          }
        },
        (err) => {
          console.error('Failed to parse VRM:', err);
          if (onError) onError(err);
        }
      );
    } catch (e) {
      console.error('Exception during VRM load:', e);
      if (onError) onError(e);
    }
  }

  updateFrame(frameIndex, delta = 0.016) {
    if (!this.currentVrm || !this.vrmMotionData) return;

    const { bones, root_translation } = this.vrmMotionData;
    if (!bones) return;

    // Apply bone rotations
    for (const [boneName, node] of Object.entries(this.boneNodes)) {
      const quatArray = bones[boneName];
      if (quatArray && quatArray.length > 0) {
        const clampedFrame = Math.max(0, Math.min(frameIndex, quatArray.length - 1));
        const [x, y, z, w] = quatArray[clampedFrame];
        node.quaternion.set(x, y, z, w);
      }
    }

    // Apply hips root translation
    if (this.hipsNode && root_translation && root_translation.length > 0) {
      const clampedFrame = Math.max(0, Math.min(frameIndex, root_translation.length - 1));
      const [rx, ry, rz] = root_translation[clampedFrame];
      this.hipsNode.position.set(rx, ry, rz);
    }

    // Update VRM internal state (spring bones, lookAt, expressions)
    this.currentVrm.update(delta);
  }

  disposeCurrent() {
    if (this.currentVrm) {
      this.scene.remove(this.currentVrm.scene);
      this.currentVrm.scene.traverse((obj) => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) {
          if (Array.isArray(obj.material)) {
            obj.material.forEach((mat) => {
              if (mat.map) mat.map.dispose();
              mat.dispose();
            });
          } else {
            if (obj.material.map) obj.material.map.dispose();
            obj.material.dispose();
          }
        }
      });
      this.currentVrm = null;
      this.boneNodes = {};
      this.hipsNode = null;
      this.isLoaded = false;
    }

    if (this.currentObjectURL) {
      URL.revokeObjectURL(this.currentObjectURL);
      this.currentObjectURL = null;
    }
  }

  dispose() {
    this.disposeCurrent();
  }
}
