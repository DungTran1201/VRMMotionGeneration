/**
 * VRM and Humanoid Avatar Lifecycle Manager using Three.js & @pixiv/three-vrm.
 */

import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';
import { ALL_STANDARD_BONES, REQUIRED_HUMANOID_BONES } from '../motion/schema_validator.js';

export class AvatarManager {
  constructor(canvas) {
    this.canvas = canvas;
    this.currentVrm = null;
    this.fallbackRig = null;
    this.isUsingVrm = false;
    this.avatarName = 'Procedural Humanoid';

    // Callbacks
    this.onBonesUpdated = null;
    this.onError = null;

    this._initScene();
  }

  _initScene() {
    // 1. Renderer
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: false,
      powerPreference: 'high-performance'
    });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.0;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // 2. Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0a0e17);
    this.scene.fog = new THREE.FogExp2(0x0a0e17, 0.04);

    // 3. Camera
    this.camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 50.0);
    this.defaultCamPos = new THREE.Vector3(0.0, 1.25, 3.2);
    this.defaultLookAt = new THREE.Vector3(0.0, 0.9, 0.0);
    this.camera.position.copy(this.defaultCamPos);

    // 4. Orbit Controls
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.target.copy(this.defaultLookAt);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.maxPolarAngle = Math.PI / 2 + 0.05; // slightly below ground
    this.controls.minDistance = 0.5;
    this.controls.maxDistance = 15.0;

    // 5. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    this.scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.8);
    keyLight.position.set(2.0, 4.0, 3.0);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 1024;
    keyLight.shadow.mapSize.height = 1024;
    keyLight.shadow.camera.near = 0.5;
    keyLight.shadow.camera.far = 15.0;
    keyLight.shadow.bias = -0.0005;
    this.scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x6366f1, 0.6);
    fillLight.position.set(-3.0, 2.0, -2.0);
    this.scene.add(fillLight);

    // 6. Ground Grid & Shadow Receiver
    const gridHelper = new THREE.GridHelper(10, 20, 0x374151, 0x1f2937);
    gridHelper.position.y = 0.0;
    this.scene.add(gridHelper);

    const floorGeo = new THREE.PlaneGeometry(30, 30);
    const floorMat = new THREE.ShadowMaterial({ opacity: 0.35 });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    this.scene.add(floor);

    // 7. Initialize Fallback Mannequin Rig
    this._createFallbackRig();

    // Resize Handler
    window.addEventListener('resize', () => this.onWindowResize());
  }

  _createFallbackRig() {
    this.disposeCurrentAvatar();

    const rootGroup = new THREE.Group();
    rootGroup.name = 'ProceduralHumanoidRig';

    const mat = new THREE.MeshStandardMaterial({
      color: 0x6366f1,
      roughness: 0.3,
      metalness: 0.2
    });
    const jointMat = new THREE.MeshStandardMaterial({
      color: 0x06b6d4,
      roughness: 0.2,
      metalness: 0.5
    });

    // Bones Dictionary
    this.fallbackBones = {};

    // Helper to create bone mesh
    const makeJoint = (name, parent, pos, r = 0.045) => {
      const node = new THREE.Group();
      node.name = name;
      node.position.set(...pos);

      const sphere = new THREE.Mesh(new THREE.SphereGeometry(r, 16, 16), jointMat);
      sphere.castShadow = true;
      node.add(sphere);

      if (parent) parent.add(node);
      this.fallbackBones[name] = node;
      return node;
    };

    const makeLimb = (node, endPos, radius = 0.035) => {
      const p1 = new THREE.Vector3(0, 0, 0);
      const p2 = new THREE.Vector3(...endPos);
      const len = p1.distanceTo(p2);

      const cylinder = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, len, 16), mat);
      cylinder.castShadow = true;
      cylinder.position.copy(p1.clone().add(p2).multiplyScalar(0.5));
      cylinder.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), p2.clone().normalize());
      node.add(cylinder);
    };

    // Construct hierarchy
    const hips = makeJoint('hips', rootGroup, [0, 0.95, 0], 0.07);
    const spine = makeJoint('spine', hips, [0, 0.18, 0], 0.06);
    makeLimb(hips, [0, 0.18, 0], 0.05);

    const chest = makeJoint('chest', spine, [0, 0.18, 0], 0.06);
    makeLimb(spine, [0, 0.18, 0], 0.055);

    const neck = makeJoint('neck', chest, [0, 0.12, 0], 0.035);
    makeLimb(chest, [0, 0.12, 0], 0.035);

    const head = makeJoint('head', neck, [0, 0.14, 0], 0.08);
    makeLimb(neck, [0, 0.14, 0], 0.035);

    // Left Arm
    const lShoulder = makeJoint('leftShoulder', chest, [0.12, 0.08, 0], 0.035);
    const lUpperArm = makeJoint('leftUpperArm', lShoulder, [0.12, 0, 0], 0.04);
    const lLowerArm = makeJoint('leftLowerArm', lUpperArm, [0.24, 0, 0], 0.035);
    makeLimb(lUpperArm, [0.24, 0, 0], 0.03);
    const lHand = makeJoint('leftHand', lLowerArm, [0.20, 0, 0], 0.035);
    makeLimb(lLowerArm, [0.20, 0, 0], 0.025);

    // Right Arm
    const rShoulder = makeJoint('rightShoulder', chest, [-0.12, 0.08, 0], 0.035);
    const rUpperArm = makeJoint('rightUpperArm', rShoulder, [-0.12, 0, 0], 0.04);
    const rLowerArm = makeJoint('rightLowerArm', rUpperArm, [-0.24, 0, 0], 0.035);
    makeLimb(rUpperArm, [-0.24, 0, 0], 0.03);
    const rHand = makeJoint('rightHand', rLowerArm, [-0.20, 0, 0], 0.035);
    makeLimb(rLowerArm, [-0.20, 0, 0], 0.025);

    // Left Leg
    const lUpperLeg = makeJoint('leftUpperLeg', hips, [0.10, -0.05, 0], 0.05);
    const lLowerLeg = makeJoint('leftLowerLeg', lUpperLeg, [0, -0.42, 0], 0.04);
    makeLimb(lUpperLeg, [0, -0.42, 0], 0.04);
    const lFoot = makeJoint('leftFoot', lLowerLeg, [0, -0.40, 0.05], 0.035);
    makeLimb(lLowerLeg, [0, -0.40, 0.05], 0.035);
    const lToes = makeJoint('leftToes', lFoot, [0, 0, 0.12], 0.025);
    makeLimb(lFoot, [0, 0, 0.12], 0.025);

    // Right Leg
    const rUpperLeg = makeJoint('rightUpperLeg', hips, [-0.10, -0.05, 0], 0.05);
    const rLowerLeg = makeJoint('rightLowerLeg', rUpperLeg, [0, -0.42, 0], 0.04);
    makeLimb(rUpperLeg, [0, -0.42, 0], 0.04);
    const rFoot = makeJoint('rightFoot', rLowerLeg, [0, -0.40, 0.05], 0.035);
    makeLimb(rLowerLeg, [0, -0.40, 0.05], 0.035);
    const rToes = makeJoint('rightToes', rFoot, [0, 0, 0.12], 0.025);
    makeLimb(rFoot, [0, 0, 0.12], 0.025);

    this.scene.add(rootGroup);
    this.fallbackRig = rootGroup;
    this.isUsingVrm = false;
    this.avatarName = 'Procedural Humanoid';

    this._notifyBoneCoverage();
  }

  async loadVrmFile(file) {
    const url = URL.createObjectURL(file);
    try {
      await this.loadVrmUrl(url, file.name);
    } finally {
      URL.revokeObjectURL(url);
    }
  }

  async loadVrmUrl(url, filename = 'custom.vrm') {
    const loader = new GLTFLoader();
    loader.crossOrigin = 'anonymous';
    loader.register((parser) => new VRMLoaderPlugin(parser));

    return new Promise((resolve, reject) => {
      loader.load(
        url,
        (gltf) => {
          const vrm = gltf.userData.vrm;
          if (!vrm) {
            const err = new Error('File loaded, but no valid VRM humanoid data was found.');
            if (this.onError) this.onError(err);
            reject(err);
            return;
          }

          this.disposeCurrentAvatar();

          this.currentVrm = vrm;
          this.isUsingVrm = true;
          this.avatarName = filename;

          // Calling rotateVRM0 rotates VRM0.0 models facing Z-forward by 180 degrees to standard -Z
          VRMUtils.rotateVRM0(vrm);

          this.scene.add(vrm.scene);

          // Enable shadows
          vrm.scene.traverse((obj) => {
            if (obj.isMesh) {
              obj.castShadow = true;
              obj.receiveShadow = true;
            }
          });

          this._notifyBoneCoverage();
          resolve(vrm);
        },
        undefined,
        (error) => {
          if (this.onError) this.onError(error);
          reject(error);
        }
      );
    });
  }

  disposeCurrentAvatar() {
    if (this.currentVrm) {
      this.scene.remove(this.currentVrm.scene);
      this.currentVrm.scene.traverse((child) => {
        if (child.geometry) child.geometry.dispose();
        if (child.material) {
          if (Array.isArray(child.material)) {
            child.material.forEach((m) => m.dispose());
          } else {
            child.material.dispose();
          }
        }
      });
      VRMUtils.deepDispose(this.currentVrm.scene);
      this.currentVrm = null;
    }

    if (this.fallbackRig) {
      this.scene.remove(this.fallbackRig);
      this.fallbackRig.traverse((child) => {
        if (child.geometry) child.geometry.dispose();
        if (child.material) child.material.dispose();
      });
      this.fallbackRig = null;
    }
  }

  _notifyBoneCoverage() {
    const boneStatus = {};
    let presentCount = 0;

    for (const boneName of ALL_STANDARD_BONES) {
      let isPresent = false;
      if (this.isUsingVrm && this.currentVrm && this.currentVrm.humanoid) {
        const node = this.currentVrm.humanoid.getNormalizedBoneNode(boneName) ||
                     this.currentVrm.humanoid.getRawBoneNode(boneName);
        isPresent = node !== null && node !== undefined;
      } else if (!this.isUsingVrm && this.fallbackBones) {
        isPresent = this.fallbackBones[boneName] !== undefined;
      }

      boneStatus[boneName] = isPresent;
      if (isPresent) presentCount++;
    }

    if (this.onBonesUpdated) {
      this.onBonesUpdated({
        bones: boneStatus,
        total: ALL_STANDARD_BONES.length,
        presentCount,
        avatarName: this.avatarName,
        isUsingVrm: this.isUsingVrm
      });
    }
  }

  applyPose(rootPos, rootQuat, bonesMap, delta = 0.016) {
    if (this.isUsingVrm && this.currentVrm && this.currentVrm.humanoid) {
      // 1. Root / Hips position
      const hipsNode = this.currentVrm.humanoid.getNormalizedBoneNode('hips') ||
                       this.currentVrm.humanoid.getRawBoneNode('hips');
      if (hipsNode && rootPos) {
        hipsNode.position.set(rootPos[0], rootPos[1], rootPos[2]);
      }

      // 2. Bone rotations
      for (const [boneName, boneData] of Object.entries(bonesMap)) {
        const q = boneData.rotation;
        if (!q || q.length !== 4) continue;

        const node = this.currentVrm.humanoid.getNormalizedBoneNode(boneName) ||
                     this.currentVrm.humanoid.getRawBoneNode(boneName);
        if (node) {
          node.quaternion.set(q[0], q[1], q[2], q[3]);
        }
      }

      this.currentVrm.update(delta);
    } else if (!this.isUsingVrm && this.fallbackBones) {
      // Procedural Rig
      if (this.fallbackBones['hips'] && rootPos) {
        this.fallbackBones['hips'].position.set(rootPos[0], rootPos[1], rootPos[2]);
      }

      for (const [boneName, boneData] of Object.entries(bonesMap)) {
        const q = boneData.rotation;
        if (!q || q.length !== 4) continue;

        const node = this.fallbackBones[boneName];
        if (node) {
          node.quaternion.set(q[0], q[1], q[2], q[3]);
        }
      }
    }
  }

  resetCamera() {
    this.camera.position.copy(this.defaultCamPos);
    this.controls.target.copy(this.defaultLookAt);
    this.controls.update();
  }

  onWindowResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  render() {
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}
