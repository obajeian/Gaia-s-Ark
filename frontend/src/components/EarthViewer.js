import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const EarthViewer = ({ data, onRegionClick }) => {
  const mountRef = useRef();
  const sceneRef = useRef();
  const rendererRef = useRef();
  const cameraRef = useRef();
  const controlsRef = useRef();
  const earthRef = useRef();
  const cloudsRef = useRef();
  const [hoveredPoint, setHoveredPoint] = useState(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      45,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.z = 4; // Zoomed out slightly for better view
    cameraRef.current = camera;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setClearColor(0x000000, 0);
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enablePan = true; // Enable pan for better exploration
    controls.minDistance = 1.2; // Allow closer zoom
    controls.maxDistance = 10;
    controlsRef.current = controls;

    // Texture Loader
    const textureLoader = new THREE.TextureLoader();

    // Earth Group
    const earthGroup = new THREE.Group();
    scene.add(earthGroup);
    earthRef.current = earthGroup;

    // 1. Earth Sphere (Night Lights)
    const earthGeometry = new THREE.SphereGeometry(1, 64, 64);
    const earthMaterial = new THREE.MeshBasicMaterial({
      map: textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_lights_2048.png'),
      color: 0xcccccc // Slightly dim to make points pop
    });
    const earth = new THREE.Mesh(earthGeometry, earthMaterial);
    earthGroup.add(earth);

    // 2. Atmosphere Glow Shader (Subtle Holographic Rim)
    const vertexShader = `
      varying vec3 vNormal;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `;

    const fragmentShader = `
      varying vec3 vNormal;
      void main() {
        float intensity = pow(0.5 - dot(vNormal, vec3(0, 0, 1.0)), 5.0);
        gl_FragColor = vec4(0.2, 0.5, 1.0, 0.4) * intensity;
      }
    `;

    const atmosphereGeometry = new THREE.SphereGeometry(1.2, 64, 64);
    const atmosphereMaterial = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      blending: THREE.AdditiveBlending,
      side: THREE.BackSide,
      transparent: true
    });
    const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    scene.add(atmosphere);

    // Lighting (Simplified for Night Mode)
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.0); // Flat lighting for map clarity
    scene.add(ambientLight);

    // Stars Background (Dimmer)
    const starsGeometry = new THREE.BufferGeometry();
    const starsVertices = [];
    for (let i = 0; i < 3000; i++) {
      starsVertices.push(
        (Math.random() - 0.5) * 2000,
        (Math.random() - 0.5) * 2000,
        (Math.random() - 0.5) * 2000
      );
    }
    starsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starsVertices, 3));
    const starsMaterial = new THREE.PointsMaterial({ color: 0x888888, size: 1.5, transparent: true, opacity: 0.5 });
    const stars = new THREE.Points(starsGeometry, starsMaterial);
    scene.add(stars);

    // Raycaster for interaction
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onMouseMove = (event) => {
      // Calculate mouse position in normalized device coordinates
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      // Update tooltip position
      setTooltipPos({ x: event.clientX, y: event.clientY });

      // Raycasting
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(scene.children, true);

      let foundPoint = null;
      for (let intersect of intersects) {
        if (intersect.object.userData && intersect.object.userData.isMangrovePoint) {
          foundPoint = intersect.object;
          break;
        }
      }

      if (foundPoint) {
        document.body.style.cursor = 'pointer';
        setHoveredPoint(foundPoint.userData);

        // Scale up effect
        if (foundPoint.scale.x === 1) {
          foundPoint.scale.set(1.5, 1.5, 1.5);
        }
      } else {
        document.body.style.cursor = 'default';
        setHoveredPoint(null);

        // Reset scales
        scene.traverse((child) => {
          if (child.userData.isMangrovePoint && child.scale.x !== 1) {
            child.scale.set(1, 1, 1);
          }
        });
      }
    };

    const onClick = (event) => {
      if (hoveredPoint) {
        onRegionClick(hoveredPoint.region);
      }
    };

    renderer.domElement.addEventListener('mousemove', onMouseMove);
    renderer.domElement.addEventListener('click', onClick);

    // Animation Loop
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();

      // Slow rotation of clouds and earth
      if (earthGroup) earthGroup.rotation.y += 0.0005;
      if (cloudsRef.current) cloudsRef.current.rotation.y += 0.0007;

      renderer.render(scene, camera);
    };
    animate();

    // Handle Resize
    const handleResize = () => {
      if (!mountRef.current) return;
      camera.aspect = mountRef.current.clientWidth / mountRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      renderer.domElement.removeEventListener('mousemove', onMouseMove);
      renderer.domElement.removeEventListener('click', onClick);

      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [onRegionClick]); // Removed hoveredPoint from dep array to avoid re-init

  // Add Data Points
  useEffect(() => {
    if (!earthRef.current || !data.length) return;

    // Clear existing points
    const pointsToRemove = [];
    earthRef.current.traverse((child) => {
      if (child.userData && child.userData.isMangrovePoint) {
        pointsToRemove.push(child);
      }
    });
    pointsToRemove.forEach(point => earthRef.current.remove(point));

    // Add new points
    data.forEach((point) => {
      // Convert lat/lon to 3D coordinates
      // Three.js SphereGeometry UV mapping aligns such that:
      // phi (lat) goes from 0 (North Pole) to PI (South Pole)
      // theta (lon) goes from 0 to 2PI, starting at -X axis (usually)

      const phi = (90 - point.latitude) * (Math.PI / 180);
      const theta = (point.longitude + 180) * (Math.PI / 180);
      const radius = 1.01; // Just above surface

      const x = -(radius * Math.sin(phi) * Math.cos(theta));
      const z = (radius * Math.sin(phi) * Math.sin(theta));
      const y = (radius * Math.cos(phi));

      // Color gradient based on carbon
      const carbonValue = point.predicted_carbon || 50;
      const normalizedCarbon = Math.min(1, Math.max(0, carbonValue / 200));
      const color = new THREE.Color();
      color.setHSL(0.3 * normalizedCarbon, 1, 0.5); // Red (low) to Green (high)

      // Reduced point size for better clarity
      const pointGeometry = new THREE.SphereGeometry(0.008, 16, 16);
      const pointMaterial = new THREE.MeshBasicMaterial({ color: color });
      const pointMesh = new THREE.Mesh(pointGeometry, pointMaterial);

      pointMesh.position.set(x, y, z);
      pointMesh.userData = { ...point, isMangrovePoint: true };

      earthRef.current.add(pointMesh);

      // Removed glow effect to prevent clustering/unreadability
    });
  }, [data]);

  return (
    <div className="earth-viewer">
      <div ref={mountRef} className="earth-canvas" />

      {/* Tooltip */}
      {hoveredPoint && (
        <div
          className="earth-tooltip"
          style={{
            top: tooltipPos.y + 15,
            left: tooltipPos.x + 15
          }}
        >
          <h4>{hoveredPoint.region}</h4>
          <div className="tooltip-stat">
            <span>Carbon:</span>
            <strong>{hoveredPoint.predicted_carbon} t</strong>
          </div>
          <div className="tooltip-stat">
            <span>Area:</span>
            <strong>{hoveredPoint.mangrove_area.toFixed(1)} ha</strong>
          </div>
        </div>
      )}

      <div className="earth-controls-overlay">
        <div className="control-hint">
          🖱️ Left Click + Drag to Rotate
        </div>
        <div className="control-hint">
          🖱️ Right Click + Drag to Pan
        </div>
        <div className="control-hint">
          🖱️ Scroll to Zoom
        </div>
      </div>
    </div>
  );
};

export default EarthViewer;