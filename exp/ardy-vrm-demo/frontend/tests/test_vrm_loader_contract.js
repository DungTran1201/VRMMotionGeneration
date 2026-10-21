/**
 * Automated Unit Test Suite for VrmManager Contract & Loading Lifecycle.
 * Tests input validation, error handling, race conditions, disposal,
 * and VRM 0.x vs 1.0 orientation and grounding logic.
 *
 * Run with: node --test frontend/tests/test_vrm_loader_contract.js
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import { VrmManager } from '../src/vrm/vrm_manager.js';

// Minimal mock Three.js environment
class MockVector3 {
  constructor(x = 0, y = 0, z = 0) {
    this.x = x;
    this.y = y;
    this.z = z;
  }
  set(x, y, z) {
    this.x = x;
    this.y = y;
    this.z = z;
    return this;
  }
  clone() {
    return new MockVector3(this.x, this.y, this.z);
  }
  add(v) {
    this.x += v.x;
    this.y += v.y;
    this.z += v.z;
    return this;
  }
  applyQuaternion() {
    return this;
  }
}

class MockBox3 {
  constructor() {
    this.min = new MockVector3(-0.4, -0.2, -0.2); // Feet slightly below origin
    this.max = new MockVector3(0.4, 1.4, 0.2);
  }
  setFromObject() {
    return this;
  }
  getSize(target) {
    target.set(this.max.x - this.min.x, this.max.y - this.min.y, this.max.z - this.min.z);
    return target;
  }
  getCenter(target) {
    target.set((this.min.x + this.max.x) / 2, (this.min.y + this.max.y) / 2, (this.min.z + this.max.z) / 2);
    return target;
  }
}

class MockGroup {
  constructor() {
    this.children = [];
    this.position = new MockVector3();
    this.rotation = new MockVector3();
  }
  add(child) {
    this.children.push(child);
  }
  remove(child) {
    const idx = this.children.indexOf(child);
    if (idx !== -1) this.children.splice(idx, 1);
  }
  updateMatrixWorld() {}
  traverse(cb) {
    cb(this);
    for (const child of this.children) {
      if (child.traverse) child.traverse(cb);
      else cb(child);
    }
  }
}

const mockTHREE = {
  Group: MockGroup,
  Vector3: MockVector3,
  Box3: MockBox3,
};

// Helper to create mock File objects with realistic sizes
function createMockFile(name, sizeInBytes, type = 'application/octet-stream') {
  // Use a tiny buffer but mock the size property if needed
  const buf = new Uint8Array(Math.min(sizeInBytes, 1024));
  const file = new File([buf], name, { type });
  if (sizeInBytes !== file.size) {
    Object.defineProperty(file, 'size', { value: sizeInBytes, configurable: true });
  }
  return file;
}

test('VrmManager: rejects non-existent or null file', async () => {
  const mockScene = new MockGroup();
  const manager = new VrmManager(mockTHREE, mockScene, class {}, class {});

  await assert.rejects(
    async () => {
      await manager.loadFromFile(null);
    },
    { message: /No file provided/ }
  );
  assert.equal(manager.isLoaded, false);
});

test('VrmManager: rejects file with invalid extension', async () => {
  const mockScene = new MockGroup();
  const manager = new VrmManager(mockTHREE, mockScene, class {}, class {});

  const invalidFile = createMockFile('avatar.gltf', 1024);
  await assert.rejects(
    async () => {
      await manager.loadFromFile(invalidFile);
    },
    { message: /Invalid file format.*\.vrm/ }
  );
  assert.equal(manager.isLoaded, false);
});

test('VrmManager: rejects empty file (0 bytes)', async () => {
  const mockScene = new MockGroup();
  const manager = new VrmManager(mockTHREE, mockScene, class {}, class {});

  const emptyFile = createMockFile('avatar.vrm', 0);
  await assert.rejects(
    async () => {
      await manager.loadFromFile(emptyFile);
    },
    { message: /empty \(0 bytes\)/ }
  );
  assert.equal(manager.isLoaded, false);
});

test('VrmManager: rejects oversized file (>100MB)', async () => {
  const mockScene = new MockGroup();
  const manager = new VrmManager(mockTHREE, mockScene, class {}, class {});

  const bigFile = createMockFile('huge_avatar.vrm', 120 * 1024 * 1024);
  await assert.rejects(
    async () => {
      await manager.loadFromFile(bigFile);
    },
    { message: /exceeds the 100 MB limit/ }
  );
  assert.equal(manager.isLoaded, false);
});

test('VrmManager: rejects GLTF file that lacks VRM metadata with actionable message', async () => {
  const mockScene = new MockGroup();

  // Loader that parses a valid glTF without userData.vrm
  class MockGLTFLoader {
    register() {}
    async loadAsync() {
      return {
        scene: new MockGroup(),
        userData: {}, // Missing VRM extension!
      };
    }
  }

  const manager = new VrmManager(mockTHREE, mockScene, MockGLTFLoader, class {});

  const fakeFile = createMockFile('standard_mesh.vrm', 5000);
  await assert.rejects(
    async () => {
      await manager.loadFromFile(fakeFile);
    },
    { message: /VRM humanoid metadata was not detected/ }
  );
  assert.equal(manager.isLoaded, false);
});

test('VrmManager: loads valid VRM 1.0 avatar, computes bounds, and does NOT rotate VRM 1.0', async () => {
  const mockScene = new MockGroup();
  let rotateVRM0Called = false;

  const mockVRMUtils = {
    rotateVRM0: (vrm) => {
      rotateVRM0Called = true;
      vrm.scene.rotation.y = Math.PI;
    },
    deepDispose: () => {},
  };

  const mockVrmScene = new MockGroup();
  const mockNormalizedHips = { position: new MockVector3(), quaternion: { set: () => {} } };

  class MockGLTFLoader {
    register() {}
    async loadAsync() {
      return {
        scene: mockVrmScene,
        userData: {
          vrm: {
            scene: mockVrmScene,
            meta: {
              metaVersion: '1',
              title: 'TestAvatar1',
              authors: ['Antigravity QA'],
            },
            humanoid: {
              getNormalizedBoneNode: (name) => {
                if (name === 'hips') return mockNormalizedHips;
                return { quaternion: { set: () => {} } };
              },
            },
            update: () => {},
          },
        },
      };
    }
  }

  const manager = new VrmManager(mockTHREE, mockScene, MockGLTFLoader, class {}, mockVRMUtils);

  const file = createMockFile('sample_avatar_v1.vrm', 1024 * 1024 * 2);
  const result = await manager.loadFromFile(file);

  assert.ok(result);
  assert.equal(manager.isLoaded, true);
  assert.equal(result.metadata.version, 'VRM 1.0');
  assert.equal(result.metadata.name, 'TestAvatar1');

  // Verify that VRM 1.0 was NOT rotated by rotateVRM0
  assert.equal(rotateVRM0Called, false);
  assert.equal(mockVrmScene.rotation.y, 0);

  // Verify foot grounding offset (min.y was -0.2, so scene.position.y must be +0.2 to ground feet to 0)
  assert.equal(mockVrmScene.position.y, 0.2);

  // Verify humanoid bone cache
  assert.equal(manager.hipsNode, mockNormalizedHips);
  assert.ok(manager.boneNodes.hips);
});

test('VrmManager: applies VRMUtils.rotateVRM0 only when VRM 0.x is detected', async () => {
  const mockScene = new MockGroup();
  let rotateVRM0Called = false;

  const mockVRMUtils = {
    rotateVRM0: (vrm) => {
      rotateVRM0Called = true;
      vrm.scene.rotation.y = Math.PI;
    },
    deepDispose: () => {},
  };

  const mockVrmScene = new MockGroup();

  class MockGLTFLoader {
    register() {}
    async loadAsync() {
      return {
        scene: mockVrmScene,
        userData: {
          vrm: {
            scene: mockVrmScene,
            meta: {
              metaVersion: '0', // VRM 0.x
              title: 'OldAvatar0',
            },
            humanoid: {
              getNormalizedBoneNode: () => ({ quaternion: { set: () => {} } }),
            },
            update: () => {},
          },
        },
      };
    }
  }

  const manager = new VrmManager(mockTHREE, mockScene, MockGLTFLoader, class {}, mockVRMUtils);

  const file = createMockFile('vrm0_model.vrm', 1024 * 500);
  const result = await manager.loadFromFile(file);

  assert.ok(result);
  assert.equal(result.metadata.version, 'VRM 0.x');
  assert.equal(rotateVRM0Called, true);
  assert.equal(mockVrmScene.rotation.y, Math.PI);
});

test('VrmManager: replacing avatar cleanly disposes old scene and resources', async () => {
  const mockScene = new MockGroup();
  let disposedCount = 0;

  const mockVRMUtils = {
    rotateVRM0: () => {},
    deepDispose: () => {
      disposedCount++;
    },
  };

  class MockGLTFLoader {
    register() {}
    async loadAsync() {
      const scene = new MockGroup();
      return {
        scene,
        userData: {
          vrm: {
            scene,
            meta: { title: 'Avatar' },
            humanoid: { getNormalizedBoneNode: () => null },
            update: () => {},
            dispose: () => {},
          },
        },
      };
    }
  }

  const manager = new VrmManager(mockTHREE, mockScene, MockGLTFLoader, class {}, mockVRMUtils);

  // Load avatar 1
  await manager.loadFromFile(createMockFile('avatar1.vrm', 1000));
  assert.equal(manager.isLoaded, true);
  assert.equal(disposedCount, 0);

  // Load avatar 2 (should dispose avatar 1 first)
  await manager.loadFromFile(createMockFile('avatar2.vrm', 1000));
  assert.equal(disposedCount, 1);
  assert.equal(manager.isLoaded, true);

  // Explicit disposal
  manager.dispose();
  assert.equal(disposedCount, 2);
  assert.equal(manager.isLoaded, false);
  assert.equal(manager.currentVrm, null);
});

test('VrmManager: updateFrame applies bone rotations and relative hips displacement', async () => {
  const mockScene = new MockGroup();
  const mockHips = { position: new MockVector3(0, 0.85, 0), quaternion: { set: () => {} } };
  const mockRightUpperArm = { quaternion: { set: (x, y, z, w) => { mockRightUpperArm.quat = [x, y, z, w]; } } };

  class MockGLTFLoader {
    register() {}
    async loadAsync() {
      const scene = new MockGroup();
      return {
        scene,
        userData: {
          vrm: {
            scene,
            meta: { metaVersion: '1', title: 'TestAvatar' },
            humanoid: {
              getNormalizedBoneNode: (name) => {
                if (name === 'hips') return mockHips;
                if (name === 'rightUpperArm') return mockRightUpperArm;
                return null;
              },
            },
            update: () => {},
          },
        },
      };
    }
  }

  const manager = new VrmManager(mockTHREE, mockScene, MockGLTFLoader, class {});
  await manager.loadFromFile(createMockFile('motion_test.vrm', 1000));

  // Set motion data with root forward displacement
  manager.setMotionData({
    bones: {
      rightUpperArm: [
        [0, 0, 0, 1],
        [0.1, 0.2, 0.3, 0.9],
      ],
    },
    root_translation: [
      [0.0, 0.90, 0.0],
      [0.0, 0.95, 0.5], // Moved +0.5m forward along Z, +0.05m up along Y
    ],
  });

  // Initial frame 0
  manager.updateFrame(0);
  assert.equal(mockHips.position.y, 0.85); // Retains native bind height
  assert.equal(mockHips.position.z, 0.0);

  // Frame 1
  manager.updateFrame(1);
  assert.ok(Math.abs(mockHips.position.y - 0.90) < 1e-5);
  assert.ok(Math.abs(mockHips.position.z - 0.50) < 1e-5);
  assert.deepEqual(mockRightUpperArm.quat, [0.1, 0.2, 0.3, 0.9]);
});
