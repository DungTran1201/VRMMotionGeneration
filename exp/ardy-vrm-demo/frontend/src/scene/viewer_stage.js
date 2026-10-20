/**
 * Dual Viewport Stage Setup.
 * Manages separate Three.js scenes, cameras, lighting, and OrbitControls
 * for side-by-side comparison of Motion Skeleton and VRM Avatar.
 */

export class ViewerStage {
  constructor(THREE, OrbitControls, skeletonCanvas, vrmCanvas) {
    this.THREE = THREE;
    this.OrbitControls = OrbitControls;

    // Viewport 1: Skeleton
    this.skeleton = this.createViewport(skeletonCanvas, 'Skeleton Viewport');

    // Viewport 2: VRM
    this.vrm = this.createViewport(vrmCanvas, 'VRM Viewport');

    this.defaultCameraPos = new THREE.Vector3(0, 1.1, 2.8);
    this.defaultCameraTarget = new THREE.Vector3(0, 0.9, 0);

    this.resetCamera();
    this.setupResizeListeners(skeletonCanvas, vrmCanvas);
  }

  createViewport(canvas, name) {
    const THREE = this.THREE;

    const scene = new THREE.Scene();
    scene.name = name;

    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 50);
    camera.position.set(0, 1.1, 2.8);

    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;

    const controls = new this.OrbitControls(camera, canvas);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 0.9, 0);
    controls.maxPolarAngle = Math.PI / 2 + 0.05; // Do not go below floor
    controls.minDistance = 0.5;
    controls.maxDistance = 10.0;

    // Lighting setup
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.2);
    keyLight.position.set(1.5, 3.5, 2.5);
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x38bdf8, 0.5);
    fillLight.position.set(-2.0, 1.5, -1.0);
    scene.add(fillLight);

    // Floor Grid
    const grid = new THREE.GridHelper(8, 32, 0x06b6d4, 0x1e293b);
    grid.position.y = 0.0;
    scene.add(grid);

    return { scene, camera, renderer, controls, canvas };
  }

  resetCamera() {
    [this.skeleton, this.vrm].forEach((vp) => {
      vp.camera.position.copy(this.defaultCameraPos);
      vp.controls.target.copy(this.defaultCameraTarget);
      vp.controls.update();
    });
  }

  setupResizeListeners(c1, c2) {
    const resizeObserver = new ResizeObserver(() => {
      this.resizeViewport(this.skeleton);
      this.resizeViewport(this.vrm);
    });

    if (c1.parentElement) resizeObserver.observe(c1.parentElement);
    if (c2.parentElement) resizeObserver.observe(c2.parentElement);

    // Initial resize pass
    setTimeout(() => {
      this.resizeViewport(this.skeleton);
      this.resizeViewport(this.vrm);
    }, 50);
  }

  resizeViewport(vp) {
    const container = vp.canvas.parentElement;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    if (width > 0 && height > 0) {
      vp.camera.aspect = width / height;
      vp.camera.updateProjectionMatrix();
      vp.renderer.setSize(width, height, false);
    }
  }

  render() {
    this.skeleton.controls.update();
    this.vrm.controls.update();

    this.skeleton.renderer.render(this.skeleton.scene, this.skeleton.camera);
    this.vrm.renderer.render(this.vrm.scene, this.vrm.camera);
  }
}
