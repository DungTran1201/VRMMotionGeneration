/**
 * CoreSkeleton27 3D renderer for Three.js.
 * Renders joints and connecting bone lines with high visual clarity.
 */

export class SkeletonRenderer {
  constructor(THREE, scene) {
    this.THREE = THREE;
    this.scene = scene;
    this.group = new THREE.Group();
    this.group.name = 'CoreSkeleton27_Group';
    this.scene.add(this.group);

    this.jointMeshes = [];
    this.lineSegments = null;
    this.lineGeometry = null;
    this.skeletonData = null; // { bone_names, parent_indices, joint_positions }
    this.bonePairs = [];
    this.visible = true;

    // Materials
    this.jointMaterial = new THREE.MeshStandardMaterial({
      color: 0x06b6d4, // Cyan
      emissive: 0x0891b2,
      emissiveIntensity: 0.4,
      roughness: 0.3,
      metalness: 0.6,
    });

    this.rootJointMaterial = new THREE.MeshStandardMaterial({
      color: 0xf59e0b, // Amber root
      emissive: 0xd97706,
      emissiveIntensity: 0.6,
      roughness: 0.2,
      metalness: 0.7,
    });

    this.lineMaterial = new THREE.LineBasicMaterial({
      color: 0x38bdf8, // Sky cyan
      linewidth: 2,
    });

    this.jointGeometry = new THREE.SphereGeometry(0.024, 16, 16);
  }

  loadSkeletonData(skeletonData) {
    this.clear();
    this.skeletonData = skeletonData;

    const { bone_names, parent_indices, joint_positions } = skeletonData;
    if (!joint_positions || joint_positions.length === 0) return;

    const numJoints = bone_names.length;

    // Build bone connectivity pairs (parent -> child)
    this.bonePairs = [];
    for (let i = 0; i < parent_indices.length; i++) {
      const p = parent_indices[i];
      if (p >= 0) {
        this.bonePairs.push([p, i]);
      }
    }

    // Create joint spheres
    for (let i = 0; i < numJoints; i++) {
      const mat = (i === 0) ? this.rootJointMaterial : this.jointMaterial;
      const mesh = new this.THREE.Mesh(this.jointGeometry, mat);
      mesh.name = `joint_${bone_names[i]}`;
      this.group.add(mesh);
      this.jointMeshes.push(mesh);
    }

    // Create LineSegments for bones
    const numLines = this.bonePairs.length;
    const positions = new Float32Array(numLines * 2 * 3); // 2 vertices per line, 3 coords
    this.lineGeometry = new this.THREE.BufferGeometry();
    this.lineGeometry.setAttribute(
      'position',
      new this.THREE.BufferAttribute(positions, 3)
    );
    this.lineSegments = new this.THREE.LineSegments(this.lineGeometry, this.lineMaterial);
    this.lineSegments.frustumCulled = false;
    this.group.add(this.lineSegments);

    // Initial frame pose
    this.updateFrame(0);
  }

  updateFrame(frameIndex) {
    if (!this.skeletonData || !this.skeletonData.joint_positions) return;
    const totalFrames = this.skeletonData.joint_positions.length;
    if (totalFrames === 0) return;

    const clampedFrame = Math.max(0, Math.min(frameIndex, totalFrames - 1));
    const joints = this.skeletonData.joint_positions[clampedFrame];

    // Update joint spheres
    for (let i = 0; i < this.jointMeshes.length && i < joints.length; i++) {
      const [x, y, z] = joints[i];
      this.jointMeshes[i].position.set(x, y, z);
    }

    // Update bone line vertices
    if (this.lineSegments && this.lineGeometry) {
      const posAttr = this.lineGeometry.attributes.position;
      const posArray = posAttr.array;
      let ptr = 0;

      for (let b = 0; b < this.bonePairs.length; b++) {
        const [parentIdx, childIdx] = this.bonePairs[b];
        const [px, py, pz] = joints[parentIdx];
        const [cx, cy, cz] = joints[childIdx];

        posArray[ptr++] = px;
        posArray[ptr++] = py;
        posArray[ptr++] = pz;

        posArray[ptr++] = cx;
        posArray[ptr++] = cy;
        posArray[ptr++] = cz;
      }

      posAttr.needsUpdate = true;
    }
  }

  setVisible(visible) {
    this.visible = visible;
    this.group.visible = visible;
  }

  clear() {
    for (const mesh of this.jointMeshes) {
      this.group.remove(mesh);
    }
    this.jointMeshes = [];

    if (this.lineSegments) {
      this.group.remove(this.lineSegments);
      this.lineSegments = null;
    }
    if (this.lineGeometry) {
      this.lineGeometry.dispose();
      this.lineGeometry = null;
    }
  }

  dispose() {
    this.clear();
    this.jointGeometry.dispose();
    this.jointMaterial.dispose();
    this.rootJointMaterial.dispose();
    this.lineMaterial.dispose();
    this.scene.remove(this.group);
  }
}
