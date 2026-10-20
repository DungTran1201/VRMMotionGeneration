/**
 * Unified Fullscreen 3D Stage.
 * Manages a single Three.js scene, camera, lighting, and floor grid for
 * side-by-side comparison of Motion Skeleton and VRM Avatar in a shared world.
 */

export class ViewerStage {
  /**
   * @param {object} THREE - Three.js core library
   * @param {class} OrbitControls - Three.js OrbitControls
   * @param {HTMLCanvasElement} stageCanvas - Fullscreen WebGL canvas
   */
  constructor(THREE, OrbitControls, stageCanvas) {
    this.THREE = THREE;
    this.OrbitControls = OrbitControls;
    this.canvas = stageCanvas;

    // Single shared scene
    this.scene = new THREE.Scene();
    this.scene.name = 'ARDY_SharedStage';

    // Single shared camera
    this.defaultCameraPos = new THREE.Vector3(0, 1.25, 3.2);
    this.defaultCameraTarget = new THREE.Vector3(0, 0.9, 0);

    this.camera = new THREE.PerspectiveCamera(38, 1, 0.1, 50);
    this.camera.position.copy(this.defaultCameraPos);

    // Single WebGL renderer
    this.renderer = new THREE.WebGLRenderer({
      canvas: stageCanvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;

    // Single OrbitControls
    this.controls = new this.OrbitControls(this.camera, stageCanvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.target.copy(this.defaultCameraTarget);
    this.controls.maxPolarAngle = Math.PI / 2 + 0.04; // Keep camera above world floor
    this.controls.minDistance = 0.5;
    this.controls.maxDistance = 12.0;

    // Lighting setup for high contrast technical viewing
    this.setupLighting();

    // World floor grid & contact markers
    this.setupWorldFloor();

    // Root groups for side-by-side comparison
    this.stageRoot = new THREE.Group();
    this.stageRoot.name = 'StageRoot';
    this.scene.add(this.stageRoot);

    // Skeleton at left offset (-0.75m), VRM Avatar at right offset (+0.75m)
    this.skeletonRoot = new THREE.Group();
    this.skeletonRoot.name = 'SkeletonComparisonRoot';
    this.skeletonRoot.position.set(-0.75, 0, 0);
    this.stageRoot.add(this.skeletonRoot);

    this.vrmRoot = new THREE.Group();
    this.vrmRoot.name = 'VRMComparisonRoot';
    this.vrmRoot.position.set(0.75, 0, 0);
    this.stageRoot.add(this.vrmRoot);

    // Setup responsive resize
    this.setupResize();
  }

  setupLighting() {
    const THREE = this.THREE;

    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    this.scene.add(ambientLight);

    // Key directional light (front right)
    const keyLight = new THREE.DirectionalLight(0xffffff, 1.4);
    keyLight.position.set(2.5, 4.0, 3.0);
    this.scene.add(keyLight);

    // Soft cyan fill light (front left)
    const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.55);
    fillLight.position.set(-3.0, 2.0, -1.0);
    this.scene.add(fillLight);

    // Indigo rim light (rear)
    const rimLight = new THREE.DirectionalLight(0x818cf8, 0.4);
    rimLight.position.set(0, 2.5, -3.5);
    this.scene.add(rimLight);
  }

  setupWorldFloor() {
    const THREE = this.THREE;

    // Primary world grid
    const grid = new THREE.GridHelper(12, 48, 0x06b6d4, 0x1e293b);
    grid.position.y = 0.0;
    this.scene.add(grid);

    // Circular contact base markers
    const createMarker = (x, color) => {
      const ringGeo = new THREE.RingGeometry(0.35, 0.38, 32);
      ringGeo.rotateX(-Math.PI / 2);
      const ringMat = new THREE.MeshBasicMaterial({
        color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.4,
      });
      const marker = new THREE.Mesh(ringGeo, ringMat);
      marker.position.set(x, 0.002, 0);
      return marker;
    };

    this.scene.add(createMarker(-0.75, 0x06b6d4)); // Cyan for skeleton
    this.scene.add(createMarker(0.75, 0x10b981));  // Emerald for VRM avatar
  }

  setupResize() {
    this.resizeObserver = new ResizeObserver(() => {
      this.handleResize();
    });

    const container = this.canvas.parentElement || document.body;
    this.resizeObserver.observe(container);
    window.addEventListener('resize', () => this.handleResize());

    // Initial resize pass
    setTimeout(() => this.handleResize(), 50);
  }

  handleResize() {
    const container = this.canvas.parentElement || document.body;
    const width = container.clientWidth || window.innerWidth;
    const height = container.clientHeight || window.innerHeight;

    if (width > 0 && height > 0) {
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height, false);
    }
  }

  resetCamera() {
    this.controls.target.copy(this.defaultCameraTarget);
    this.camera.position.copy(this.defaultCameraPos);
    this.controls.update();
  }

  frameAvatar() {
    this.controls.target.set(0.75, 0.9, 0);
    this.camera.position.set(0.75, 1.15, 2.3);
    this.controls.update();
  }

  frameSkeleton() {
    this.controls.target.set(-0.75, 0.9, 0);
    this.camera.position.set(-0.75, 1.15, 2.3);
    this.controls.update();
  }

  frameBoth() {
    this.resetCamera();
  }

  render() {
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }

  dispose() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
    this.renderer.dispose();
    this.controls.dispose();
  }
}
