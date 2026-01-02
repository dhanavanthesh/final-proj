import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

export default function Helix3D({
  bases = [],
  hydrogenBonds = [],
  animationFrames = [],
  showHydrogenBonds = true,
  autoRotate = true,
  onFrameChange = null
}) {
  const mountRef = useRef();
  const animationRef = useRef();
  const controlsRef = useRef();
  const baseMeshesRef = useRef([]);
  const sceneRef = useRef();
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  // Main 3D scene setup
  useEffect(() => {
    if (!bases.length) return;

    const width = 600, height = 480;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f7fb);
    sceneRef.current = scene;

    // Camera setup with better positioning
    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.set(0, 0, 20);

    // Renderer with high-quality settings
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    mountRef.current.appendChild(renderer.domElement);

    // Professional three-point lighting system
    // Key light (main illumination)
    const keyLight = new THREE.DirectionalLight(0xffffff, 1.0);
    keyLight.position.set(10, 10, 10);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 2048;
    keyLight.shadow.mapSize.height = 2048;
    keyLight.shadow.camera.near = 0.5;
    keyLight.shadow.camera.far = 50;
    scene.add(keyLight);

    // Fill light (softens shadows)
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.5);
    fillLight.position.set(-10, 5, -5);
    scene.add(fillLight);

    // Rim light (edge definition)
    const rimLight = new THREE.DirectionalLight(0xffffff, 0.3);
    rimLight.position.set(0, -10, -10);
    scene.add(rimLight);

    // Ambient light (base illumination)
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);

    // OrbitControls for interactive manipulation
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 5;
    controls.maxDistance = 50;
    controls.autoRotate = autoRotate;
    controls.autoRotateSpeed = 1.0;
    controls.enablePan = true;
    controls.enableZoom = true;
    controlsRef.current = controls;

    // Performance optimization: use instanced meshes for large sequences
    const baseMeshes = [];
    if (bases.length > 200) {
      // Instanced rendering for performance
      const baseGeometry = new THREE.SphereGeometry(0.32, 16, 16);
      const instancedMesh = new THREE.InstancedMesh(
        baseGeometry,
        new THREE.MeshPhongMaterial({
          vertexColors: true,
          shininess: 60,
          specular: 0x444444
        }),
        bases.length
      );

      const matrix = new THREE.Matrix4();
      const color = new THREE.Color();

      bases.forEach((b, i) => {
        const x = b.position[0] * 4;
        const y = b.position[1] * 4;
        const z = b.position[2] * 2;

        matrix.setPosition(x, y, z);
        instancedMesh.setMatrixAt(i, matrix);

        color.set(b.color || '#888');
        instancedMesh.setColorAt(i, color);
      });

      instancedMesh.castShadow = true;
      instancedMesh.receiveShadow = true;
      scene.add(instancedMesh);
      baseMeshes.push(instancedMesh);
    } else {
      // Standard rendering for better quality on small sequences
      bases.forEach((b, i) => {
        const color = b.color || '#888';
        const geometry = new THREE.SphereGeometry(0.32, 24, 24);
        const material = new THREE.MeshPhongMaterial({
          color,
          shininess: 60,
          specular: 0x444444,
          emissive: 0x000000,
          emissiveIntensity: 0
        });
        const sphere = new THREE.Mesh(geometry, material);
        sphere.position.set(
          b.position[0] * 4,
          b.position[1] * 4,
          b.position[2] * 2
        );
        sphere.castShadow = true;
        sphere.receiveShadow = true;
        sphere.userData.baseIndex = i;
        sphere.userData.originalColor = color;
        scene.add(sphere);
        baseMeshes.push(sphere);
      });
    }
    baseMeshesRef.current = baseMeshes;

    // Enhanced ribbon backbone using TubeGeometry
    const backbonePoints = bases.map(b =>
      new THREE.Vector3(b.position[0] * 4, b.position[1] * 4, b.position[2] * 2)
    );

    if (backbonePoints.length > 1) {
      const curve = new THREE.CatmullRomCurve3(backbonePoints);
      const tubeGeometry = new THREE.TubeGeometry(curve, 100, 0.15, 8, false);
      const tubeMaterial = new THREE.MeshPhongMaterial({
        color: 0x888888,
        shininess: 30,
        opacity: 0.7,
        transparent: true
      });
      const ribbon = new THREE.Mesh(tubeGeometry, tubeMaterial);
      ribbon.castShadow = true;
      ribbon.receiveShadow = true;
      scene.add(ribbon);
    }

    // Hydrogen bonds visualization (if provided)
    if (showHydrogenBonds && hydrogenBonds && hydrogenBonds.length > 0) {
      hydrogenBonds.forEach(bond => {
        const points = [
          new THREE.Vector3(bond.from[0] * 4, bond.from[1] * 4, bond.from[2] * 2),
          new THREE.Vector3(bond.to[0] * 4, bond.to[1] * 4, bond.to[2] * 2)
        ];

        const geometry = new THREE.BufferGeometry().setFromPoints(points);

        // Color based on bond strength (2 or 3 hydrogen bonds)
        const bondColor = bond.strength === 3 ? 0x00CED1 : 0xFFD700;
        const material = new THREE.LineDashedMaterial({
          color: bondColor,
          dashSize: 0.2,
          gapSize: 0.1,
          linewidth: 2,
          opacity: 0.6,
          transparent: true
        });

        const line = new THREE.Line(geometry, material);
        line.computeLineDistances();
        scene.add(line);
      });
    }

    // Animation loop
    function animate() {
      if (controlsRef.current) {
        controlsRef.current.update();
      }
      renderer.render(scene, camera);
      animationRef.current = requestAnimationFrame(animate);
    }
    animate();

    // Cleanup
    return () => {
      cancelAnimationFrame(animationRef.current);
      if (controlsRef.current) {
        controlsRef.current.dispose();
      }
      renderer.dispose();
      if (mountRef.current && mountRef.current.contains(renderer.domElement)) {
        mountRef.current.removeChild(renderer.domElement);
      }
    };
  }, [bases, hydrogenBonds, showHydrogenBonds, autoRotate]);

  // Animation frame playback
  useEffect(() => {
    if (!isPlaying || !animationFrames.length || bases.length > 200) return;

    const interval = setInterval(() => {
      setCurrentFrame(prev => {
        const next = prev + 1;
        if (next >= animationFrames.length) {
          setIsPlaying(false);
          return prev;
        }
        return next;
      });
    }, 500); // 500ms per frame

    return () => clearInterval(interval);
  }, [isPlaying, animationFrames, bases.length]);

  // Update base colors based on animation frame
  useEffect(() => {
    if (!animationFrames.length || !baseMeshesRef.current.length || bases.length > 200) return;

    const frame = animationFrames[currentFrame];
    if (!frame) return;

    baseMeshesRef.current.forEach((mesh, index) => {
      if (!mesh.material) return;

      if (index <= currentFrame && frame.state_color) {
        // Highlight decoded bases with state color
        mesh.material.color.set(frame.state_color);
        mesh.material.emissive = new THREE.Color(frame.state_color);
        mesh.material.emissiveIntensity = 0.3;
      } else {
        // Undecoded bases remain in original color
        const originalColor = mesh.userData.originalColor || '#cccccc';
        mesh.material.color.set(originalColor);
        mesh.material.emissive = new THREE.Color(0x000000);
        mesh.material.emissiveIntensity = 0;
      }
    });

    if (onFrameChange) {
      onFrameChange(currentFrame, frame);
    }
  }, [currentFrame, animationFrames, bases.length, onFrameChange]);

  // Toggle auto-rotation
  useEffect(() => {
    if (controlsRef.current) {
      controlsRef.current.autoRotate = autoRotate;
    }
  }, [autoRotate]);

  return (
    <div style={{ textAlign: 'center' }}>
      <div ref={mountRef} style={{ width: 600, height: 480, margin: '0 auto' }} />

      {animationFrames.length > 0 && bases.length <= 200 && (
        <div style={{
          marginTop: '1rem',
          padding: '1rem',
          background: 'white',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', justifyContent: 'center' }}>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              style={{
                padding: '0.5rem 1rem',
                background: isPlaying ? '#ff9800' : '#0a5ec0',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              {isPlaying ? '⏸ Pause' : '▶ Play'} Decoding Animation
            </button>
            <button
              onClick={() => {
                setCurrentFrame(0);
                setIsPlaying(false);
              }}
              style={{
                padding: '0.5rem 1rem',
                background: '#666',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              ⏮ Reset
            </button>
          </div>
          <div style={{ marginTop: '1rem' }}>
            <input
              type="range"
              min="0"
              max={animationFrames.length - 1}
              value={currentFrame}
              onChange={e => {
                setIsPlaying(false);
                setCurrentFrame(parseInt(e.target.value));
              }}
              style={{ width: '100%' }}
            />
            <div style={{ marginTop: '0.5rem', color: '#666', fontSize: '0.9rem' }}>
              Frame: {currentFrame + 1} / {animationFrames.length}
              {animationFrames[currentFrame] && (
                <span style={{ marginLeft: '1rem' }}>
                  Base: <strong>{animationFrames[currentFrame].current_base}</strong>
                  {' → State: '}
                  <strong style={{ color: animationFrames[currentFrame].state_color }}>
                    {animationFrames[currentFrame].decoded_state}
                  </strong>
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
