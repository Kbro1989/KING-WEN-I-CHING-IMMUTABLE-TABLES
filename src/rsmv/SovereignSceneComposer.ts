/**
 * SovereignSceneComposer — POG3 Runtime 3D Scene Manager
 * Loads all 64 Shap-E/RSMV NPCs with oracle state, collision, and interaction.
 * Integrates with existing RSMV viewer and kingwen_512_oracle_widget.html
 */
import * as THREE from 'three';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { SovereignNPC, parseKitToNPC } from './SovereignNPC.js';
import { CollisionVisLoader } from './CollisionVisLoader.js';

export interface SceneConfig {
  container: HTMLElement;
  apiBaseUrl: string;           // e.g., "http://localhost:8765"
  enableCollision: boolean;
  enableVoice: boolean;
  theme: 'dark' | 'light';
}

export class SovereignSceneComposer {
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private renderer: THREE.WebGLRenderer;
  private controls: OrbitControls;
  private raycaster = new THREE.Raycaster();
  private mouse = new THREE.Vector2();
  private npcs = new Map<number, THREE.Group>();
  private collisionLoader: CollisionVisLoader;
  private config: SceneConfig;
  private animationId: number = 0;

  constructor(config: SceneConfig) {
    this.config = config;
    this.collisionLoader = new CollisionVisLoader(config.apiBaseUrl);

    // Scene setup
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(config.theme === 'dark' ? 0x111111 : 0xf0f0f0);

    // Camera: positioned to see all 64 NPCs arranged in 8×8 grid
    this.camera = new THREE.PerspectiveCamera(45, config.container.clientWidth / config.container.clientHeight, 0.1, 1000);
    this.camera.position.set(0, 20, 40);

    // Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(config.container.clientWidth, config.container.clientHeight);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.shadowMap.enabled = true;
    config.container.appendChild(this.renderer.domElement);

    // Controls
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.maxPolarAngle = Math.PI / 2;

    // Lighting
    const ambient = new THREE.AmbientLight(0xffffff, 0.4);
    this.scene.add(ambient);

    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(10, 20, 10);
    dirLight.castShadow = true;
    this.scene.add(dirLight);

    // Ground plane
    const groundGeo = new THREE.PlaneGeometry(80, 80);
    const groundMat = new THREE.MeshStandardMaterial({
      color: config.theme === 'dark' ? 0x222222 : 0xcccccc,
      roughness: 0.8,
      metalness: 0.2,
    });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    this.scene.add(ground);

    // Event bindings
    this.renderer.domElement.addEventListener('click', this.onClick.bind(this));
    this.renderer.domElement.addEventListener('mousemove', this.onHover.bind(this));
    window.addEventListener('resize', this.onResize.bind(this));
  }

  /** Load all 64 NPCs from API and arrange in 8×8 grid */
  async loadAllNPCs(): Promise<void> {
    const loader = new PLYLoader();
    const gridSize = 8;
    const spacing = 8;

    for (let kitId = 1; kitId <= 64; kitId++) {
      const row = Math.floor((kitId - 1) / gridSize);
      const col = (kitId - 1) % gridSize;
      const x = (col - gridSize / 2) * spacing;
      const z = (row - gridSize / 2) * spacing;

      try {
        // Fetch kit metadata
        const kitRes = await fetch(`${this.config.apiBaseUrl}/kit/${kitId}`);
        const kitJson = await kitRes.json();
        const npc = parseKitToNPC(kitJson);

        // Load PLY mesh
        const plyUrl = `${this.config.apiBaseUrl}/3d/${kitId}`;
        const geometry = await new Promise<THREE.BufferGeometry>((resolve, reject) => {
          loader.load(plyUrl, resolve, undefined, reject);
        });

        // Apply K-Color tint from kit metadata
        const color = new THREE.Color(npc.kColorMap.blendedHex);
        const material = new THREE.MeshStandardMaterial({
          color,
          roughness: 0.5,
          metalness: 0.3,
          flatShading: false,
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        // Scale to uniform size (Shap-E outputs vary)
        geometry.computeBoundingBox();
        const bbox = geometry.boundingBox!;
        const size = new THREE.Vector3().subVectors(bbox.max, bbox.min);
        const maxDim = Math.max(size.x, size.y, size.z, 0.001);
        const scale = 3.0 / maxDim;
        mesh.scale.setScalar(scale);

        // Position in grid
        mesh.position.set(x, (size.y * scale) / 2, z);

        // Add collision bounds if enabled
        if (this.config.enableCollision) {
          const bvh = await this.collisionLoader.loadBVH(kitId);
          if (bvh) {
            const boxHelper = new THREE.BoxHelper(mesh, 0x00ff00);
            mesh.add(boxHelper);
            (mesh as any).bvhData = bvh;
          }
        }

        // Add label sprite
        const label = this.createLabelSprite(`${kitId}: ${npc.codename}`);
        label.position.set(0, (size.y * scale) / 2 + 0.5, 0);
        mesh.add(label);

        // Store metadata on mesh for raycasting
        (mesh as any).npcData = npc;
        (mesh as any).kitId = kitId;

        const group = new THREE.Group();
        group.add(mesh);
        this.scene.add(group);
        this.npcs.set(kitId, group);

        // Vortex rotation animation (Schauberger centripetal/centrifugal)
        (mesh as any).vortexSpeed = npc.schauberger.motionMode === 'centripetal' ? 0.01 : -0.02;
        (mesh as any).vortexAxis = new THREE.Vector3(0, 1, 0);

      } catch (err) {
        console.error(`[HEX ${kitId}] Failed to load NPC:`, err);
        // Place fallback cube
        const fallback = new THREE.Mesh(
          new THREE.BoxGeometry(1, 1, 1),
          new THREE.MeshStandardMaterial({ color: 0xff0000, wireframe: true })
        );
        fallback.position.set(x, 0.5, z);
        (fallback as any).kitId = kitId;
        const group = new THREE.Group();
        group.add(fallback);
        this.scene.add(group);
        this.npcs.set(kitId, group);
      }
    }

    console.log(`[SCENE] Loaded ${this.npcs.size}/64 NPCs`);
  }

  /** Raycast click → consult intent → oracle resolution */
  private onClick(event: MouseEvent): void {
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(this.scene.children, true);

    for (const hit of intersects) {
      let obj: any = hit.object;
      while (obj && !obj.npcData && obj.parent) {
        obj = obj.parent;
      }

      if (obj?.npcData) {
        this.handleNPCClick(obj.kitId, obj.npcData, hit.point);
        break;
      }
    }
  }

  private async handleNPCClick(kitId: number, npc: SovereignNPC, point: THREE.Vector3): Promise<void> {
    console.log(`[CLICK] HEX ${kitId} — ${npc.codename} (${npc.oracleState.action})`);

    const consultText = `consult hexagram ${kitId} ${npc.codename} at position ${point.x.toFixed(2)},${point.y.toFixed(2)},${point.z.toFixed(2)}`;

    try {
      const res = await fetch(`${this.config.apiBaseUrl}/expand`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: consultText,
          hexagram_id: kitId,
          session_id: 'threejs-viewfinder',
        }),
      });
      const result = await res.json();

      window.dispatchEvent(new CustomEvent('sovereign-consult', {
        detail: { kitId, npc, consultResult: result, clickPoint: point },
      }));

    } catch (err) {
      console.error('[CONSULT] Failed:', err);
    }
  }

  private onHover(event: MouseEvent): void {
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(this.scene.children, true);

    this.npcs.forEach(group => {
      group.traverse((child: THREE.Object3D) => {
        const m = child as THREE.Mesh;
        if (m.material && (m.material as THREE.MeshStandardMaterial).emissive) {
          (m.material as THREE.MeshStandardMaterial).emissive.setHex(0x000000);
        }
      });
    });

    if (intersects.length > 0) {
      let obj: any = intersects[0].object;
      while (obj && !obj.npcData && obj.parent) obj = obj.parent;
      if (obj?.npcData) {
        const group = this.npcs.get(obj.kitId);
        if (group) {
          group.traverse((child: THREE.Object3D) => {
            const m = child as THREE.Mesh;
            if (m.material && (m.material as THREE.MeshStandardMaterial).emissive) {
              (m.material as THREE.MeshStandardMaterial).emissive.setHex(0x444444);
            }
          });
        }
        document.body.style.cursor = 'pointer';
        return;
      }
    }
    document.body.style.cursor = 'default';
  }

  private createLabelSprite(text: string): THREE.Sprite {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;
    canvas.width = 256;
    canvas.height = 64;
    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    ctx.fillRect(0, 0, 256, 64);
    ctx.font = 'bold 16px monospace';
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'center';
    ctx.fillText(text, 128, 40);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(4, 1, 1);
    return sprite;
  }

  private onResize(): void {
    const w = this.config.container.clientWidth;
    const h = this.config.container.clientHeight;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  /** Animation loop with Schauberger vortex rotation */
  animate(): void {
    this.animationId = requestAnimationFrame(this.animate.bind(this));

    this.npcs.forEach(group => {
      const speed = (group as any).vortexSpeed || 0.005;
      group.rotation.y += speed;
    });

    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }

  dispose(): void {
    cancelAnimationFrame(this.animationId);
    this.renderer.dispose();
    this.controls.dispose();
    this.npcs.clear();
  }
}
