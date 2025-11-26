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
  const [selectedLocation, setSelectedLocation] = useState(null);

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    // Fog to blend distant stars
    scene.fog = new THREE.FogExp2(0x000000, 0.002);

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      45,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.001, // Adjusted for close zoom
      1000
    );
    camera.position.z = 3.5;
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
    controls.enablePan = false;
    controls.minDistance = 1.005; // Allow street level zoom (just above surface)
    controls.maxDistance = 8;
    controlsRef.current = controls;

    // Texture Loader
    const textureLoader = new THREE.TextureLoader();

    // Earth Group
    const earthGroup = new THREE.Group();
    scene.add(earthGroup);
    earthRef.current = earthGroup;

    // --- HOLOGRAPHIC EARTH SHADER ---
    // We use the earth lights texture to define "density" of the hologram
    const earthTexture = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_lights_2048.png');

    const earthVertexShader = `
      varying vec3 vNormal;
      varying vec2 vUv;
      varying vec3 vViewPosition;
      
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vUv = uv;
        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        vViewPosition = -mvPosition.xyz;
        gl_Position = projectionMatrix * mvPosition;
      }
    `;

    const earthFragmentShader = `
      uniform sampler2D map;
      uniform vec3 colorLand;
      uniform vec3 colorWater;
      varying vec3 vNormal;
      varying vec2 vUv;
      varying vec3 vViewPosition;

      void main() {
        // Sample texture (grayscale lights)
        vec4 texColor = texture2D(map, vUv);
        float landMask = texColor.r; // Use red channel as mask

        // Grid effect
        float gridScale = 40.0;
        float gridX = step(0.98, fract(vUv.x * gridScale));
        float gridY = step(0.98, fract(vUv.y * gridScale));
        float grid = max(gridX, gridY) * 0.3;

        // Fresnel (Rim Light)
        vec3 normal = normalize(vNormal);
        vec3 viewDir = normalize(vViewPosition);
        float fresnel = pow(1.0 - dot(normal, viewDir), 3.0);

        // Mix colors
        // Land glows green, Water is deep blue/transparent
        vec3 finalColor = mix(colorWater, colorLand, landMask);
        
        // Add grid to water areas mostly
        finalColor += vec3(0.0, 1.0, 0.8) * grid * (1.0 - landMask * 0.8);

        // Add Fresnel glow
        finalColor += vec3(0.0, 1.0, 0.5) * fresnel * 1.5;

        // Alpha
        float alpha = max(0.1, landMask) + fresnel * 0.5 + grid;

        gl_FragColor = vec4(finalColor, alpha);
      }
    `;

    const earthMaterial = new THREE.ShaderMaterial({
      uniforms: {
        map: { value: earthTexture },
        colorLand: { value: new THREE.Color(0x00ff88) }, // Neon Green
        colorWater: { value: new THREE.Color(0x001133) } // Deep Blue
      },
      vertexShader: earthVertexShader,
      fragmentShader: earthFragmentShader,
      transparent: true,
      blending: THREE.AdditiveBlending,
      side: THREE.FrontSide
    });

    // Occlusion Sphere (Black core to hide back side)
    const occlusionGeometry = new THREE.SphereGeometry(0.99, 64, 64);
    const occlusionMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 });
    const occlusionSphere = new THREE.Mesh(occlusionGeometry, occlusionMaterial);
    earthGroup.add(occlusionSphere);

    const earthGeometry = new THREE.SphereGeometry(1, 64, 64);
    const earth = new THREE.Mesh(earthGeometry, earthMaterial);
    earthGroup.add(earth);

    // --- ATMOSPHERE GLOW ---
    const atmoVertexShader = `
      varying vec3 vNormal;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `;

    const atmoFragmentShader = `
      varying vec3 vNormal;
      void main() {
        float intensity = pow(0.6 - dot(vNormal, vec3(0, 0, 1.0)), 4.0);
        gl_FragColor = vec4(0.0, 1.0, 0.8, 0.5) * intensity; // Cyan glow
      }
    `;

    const atmosphere = new THREE.Mesh(
      new THREE.SphereGeometry(1.2, 64, 64),
      new THREE.ShaderMaterial({
        vertexShader: atmoVertexShader,
        fragmentShader: atmoFragmentShader,
        blending: THREE.AdditiveBlending,
        side: THREE.BackSide,
        transparent: true
      })
    );
    scene.add(atmosphere);

    // --- STARFIELD ---
    const starsGeometry = new THREE.BufferGeometry();
    const starsCount = 5000;
    const posArray = new Float32Array(starsCount * 3);
    const sizeArray = new Float32Array(starsCount);

    for (let i = 0; i < starsCount * 3; i += 3) {
      posArray[i] = (Math.random() - 0.5) * 2000;
      posArray[i + 1] = (Math.random() - 0.5) * 2000;
      posArray[i + 2] = (Math.random() - 0.5) * 2000;

      // Varying sizes
      sizeArray[i / 3] = Math.random() * 2;
    }

    starsGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    starsGeometry.setAttribute('size', new THREE.BufferAttribute(sizeArray, 1));

    // Custom star shader for twinkling/roundness
    const starMaterial = new THREE.PointsMaterial({
      size: 2,
      color: 0xffffff,
      transparent: true,
      opacity: 0.8,
      sizeAttenuation: true
    });

    const stars = new THREE.Points(starsGeometry, starMaterial);
    scene.add(stars);

    // --- BORDERS & INTERACTION MESHES ---
    const interactionGroup = new THREE.Group();
    earthGroup.add(interactionGroup);

    // Helper to convert lat/lon to 3D vector
    const latLonToVector3 = (lat, lon, radius) => {
      const phi = (90 - lat) * (Math.PI / 180);
      const theta = (lon + 180) * (Math.PI / 180);
      const x = -(radius * Math.sin(phi) * Math.cos(theta));
      const z = (radius * Math.sin(phi) * Math.sin(theta));
      const y = (radius * Math.cos(phi));
      return new THREE.Vector3(x, y, z);
    };

    // Load GeoJSONs
    const loadGeoJSON = async () => {
      try {
        const [countriesRes, oceansRes] = await Promise.all([
          fetch('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson'),
          fetch('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_geography_marine_polys.geojson')
        ]);

        const countriesData = await countriesRes.json();
        const oceansData = await oceansRes.json();

        // --- OPTIMIZED RENDERING ---

        // 1. Countries (Merged Lines)
        const createMergedLines = (features, radius, color, opacity) => {
          const points = [];
          features.forEach(feature => {
            const geometries = feature.geometry.type === 'MultiPolygon'
              ? feature.geometry.coordinates
              : [feature.geometry.coordinates];

            geometries.forEach(polygon => {
              const outerRing = polygon[0];
              for (let i = 0; i < outerRing.length - 1; i++) {
                const [lon1, lat1] = outerRing[i];
                const [lon2, lat2] = outerRing[i + 1];
                points.push(latLonToVector3(lat1, lon1, radius));
                points.push(latLonToVector3(lat2, lon2, radius));
              }
            });
          });

          const geometry = new THREE.BufferGeometry().setFromPoints(points);
          const material = new THREE.LineBasicMaterial({
            color: color,
            transparent: true,
            opacity: opacity
          });
          return new THREE.LineSegments(geometry, material);
        };

        // Render Countries
        const countryLines = createMergedLines(countriesData.features, 1.005, 0x50ffb0, 0.3);
        earthGroup.add(countryLines);

        // Store data for hover check (Point in Polygon)
        earthRef.current.userData.geoData = {
          countries: countriesData.features,
          oceans: oceansData.features
        };

      } catch (error) {
        console.error("Error loading GeoJSON:", error);
      }
    };

    loadGeoJSON();

    // Raycaster
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    // Point in Polygon (Ray Casting algorithm)
    const isPointInPolygon = (point, vs) => {
      // point = [lon, lat], vs = [[lon, lat], ...]
      let x = point[0], y = point[1];
      let inside = false;
      for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
        let xi = vs[i][0], yi = vs[i][1];
        let xj = vs[j][0], yj = vs[j][1];

        let intersect = ((yi > y) !== (yj > y))
          && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
      }
      return inside;
    };

    const getRegionName = (lat, lon) => {
      if (!earthRef.current.userData.geoData) return null;
      const { countries, oceans } = earthRef.current.userData.geoData;

      // Check Countries first
      for (let feature of countries) {
        const geometries = feature.geometry.type === 'MultiPolygon'
          ? feature.geometry.coordinates
          : [feature.geometry.coordinates];

        for (let polygon of geometries) {
          if (isPointInPolygon([lon, lat], polygon[0])) {
            return feature.properties.NAME || feature.properties.name;
          }
        }
      }

      // Check Oceans
      for (let feature of oceans) {
        const geometries = feature.geometry.type === 'MultiPolygon'
          ? feature.geometry.coordinates
          : [feature.geometry.coordinates];

        for (let polygon of geometries) {
          if (isPointInPolygon([lon, lat], polygon[0])) {
            return feature.properties.NAME || feature.properties.name;
          }
        }
      }
      return null;
    };

    const onMouseMove = (event) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      setTooltipPos({ x: event.clientX, y: event.clientY });

      raycaster.setFromCamera(mouse, camera);

      let foundPoint = null;

      // 1. Check Mangrove Points (Priority)
      const mangrovePoints = earthGroup.children.filter(c => c.userData && c.userData.isMangrovePoint);
      const intersectsPoints = raycaster.intersectObjects(mangrovePoints, false);

      if (intersectsPoints.length > 0) {
        foundPoint = intersectsPoints[0].object;
      }

      if (foundPoint) {
        document.body.style.cursor = 'pointer';
        setHoveredPoint(foundPoint.userData);

        // Scale effect for Mangrove Points
        if (foundPoint.userData.isMangrovePoint && foundPoint.scale.x === 1) {
          foundPoint.scale.set(2.0, 2.0, 2.0);
        }

      } else {
        // 2. Check Earth for Region Name
        const intersectsEarth = raycaster.intersectObject(earth);
        if (intersectsEarth.length > 0) {
          const worldPoint = intersectsEarth[0].point;
          const localPoint = earth.worldToLocal(worldPoint.clone());

          const phi = Math.acos(localPoint.y / 1.0);
          const lat = 90 - (phi * 180 / Math.PI);
          const theta = Math.atan2(localPoint.z, -localPoint.x);
          const lon = (theta * 180 / Math.PI) - 180;

          const regionName = getRegionName(lat, lon);
          if (regionName) {
            setHoveredPoint({ region: regionName, isRegionLabel: true });
          } else {
            setHoveredPoint(null);
          }
        } else {
          setHoveredPoint(null);
        }

        document.body.style.cursor = 'default';

        // Reset scales
        earthGroup.traverse((child) => {
          if (child.userData.isMangrovePoint && child.scale.x !== 1) {
            child.scale.set(1, 1, 1);
          }
        });
      }
    };

    const onClick = (event) => {
      if (hoveredPoint && !hoveredPoint.isRegionLabel) {
        onRegionClick(hoveredPoint.region);
        return;
      }

      // If clicking on Earth (not a point), open OSM Modal
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersectsEarth = raycaster.intersectObject(earth);

      if (intersectsEarth.length > 0) {
        const worldPoint = intersectsEarth[0].point;
        const localPoint = earth.worldToLocal(worldPoint.clone());
        const phi = Math.acos(localPoint.y / 1.0);
        const lat = 90 - (phi * 180 / Math.PI);
        const theta = Math.atan2(localPoint.z, -localPoint.x);
        const lon = (theta * 180 / Math.PI) - 180;

        setSelectedLocation({ lat, lon });
      }
    };

    renderer.domElement.addEventListener('mousemove', onMouseMove);
    renderer.domElement.addEventListener('click', onClick);

    // Animation Loop
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();

      // Rotation DISABLED
      // if (earthGroup) earthGroup.rotation.y += 0.001;

      // Rotate Stars slowly
      if (stars) stars.rotation.y -= 0.0002;

      const time = Date.now() * 0.002;
      earthGroup.children.forEach(child => {
        if (child.userData.isMangrovePoint) {
          const scale = 1 + Math.sin(time + child.position.x) * 0.2;
          if (child.userData.region !== hoveredPoint?.region) {
            // Pulse
          }
        }
      });

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
  }, [onRegionClick]);

  // Add Data Points
  useEffect(() => {
    if (!earthRef.current || !data.length) return;

    // Clear existing points
    const pointsToRemove = [];
    earthRef.current.children.forEach((child) => {
      if (child.userData && child.userData.isMangrovePoint) {
        pointsToRemove.push(child);
      }
    });
    pointsToRemove.forEach(point => earthRef.current.remove(point));

    // Add new points
    data.forEach((point) => {
      const phi = (90 - point.latitude) * (Math.PI / 180);
      const theta = (point.longitude + 180) * (Math.PI / 180);
      const radius = 1.02; // Slightly higher than surface

      const x = -(radius * Math.sin(phi) * Math.cos(theta));
      const z = (radius * Math.sin(phi) * Math.sin(theta));
      const y = (radius * Math.cos(phi));

      // Neon Purple for Mangroves
      const color = new THREE.Color(0xbf00ff);

      // Use a glowing sprite or simple sphere
      const pointGeometry = new THREE.SphereGeometry(0.012, 16, 16);
      const pointMaterial = new THREE.MeshBasicMaterial({
        color: color,
        transparent: true,
        opacity: 0.9
      });
      const pointMesh = new THREE.Mesh(pointGeometry, pointMaterial);

      pointMesh.position.set(x, y, z);
      pointMesh.userData = { ...point, isMangrovePoint: true };

      earthRef.current.add(pointMesh);

      // Add a vertical line "marker" sticking out
      const lineGeo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(0, 0.05, 0) // Height of marker
      ]);
      const lineMat = new THREE.LineBasicMaterial({ color: 0xbf00ff, transparent: true, opacity: 0.5 });
      const line = new THREE.Line(lineGeo, lineMat);
      line.position.copy(pointMesh.position);
      line.lookAt(new THREE.Vector3(0, 0, 0)); // Point towards center (so line points out)
      // Fix rotation because lookAt points +Z to target, we want +Y to point away? 
      // Actually simpler: just position at surface and lookAt(0,0,0) makes Z axis point to center.
      // We want line along Z axis then.

      // Let's stick to simple spheres for now to avoid rotation math clutter
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
          {!hoveredPoint.isRegionLabel && (
            <>
              <div className="tooltip-stat">
                <span>Carbon:</span>
                <strong>{hoveredPoint.predicted_carbon} t</strong>
              </div>
              <div className="tooltip-stat">
                <span>Area:</span>
                <strong>{hoveredPoint.mangrove_area.toFixed(1)} ha</strong>
              </div>
            </>
          )}
        </div>
      )}

      {/* OSM Modal */}
      {selectedLocation && (
        <div className="osm-modal-overlay" onClick={() => setSelectedLocation(null)}>
          <div className="osm-modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="osm-close-btn" onClick={() => setSelectedLocation(null)}>×</button>
            <iframe
              className="osm-iframe"
              title="OpenStreetMap"
              width="100%"
              height="100%"
              frameBorder="0"
              scrolling="no"
              marginHeight="0"
              marginWidth="0"
              src={`https://www.openstreetmap.org/export/embed.html?bbox=${selectedLocation.lon - 0.1},${selectedLocation.lat - 0.1},${selectedLocation.lon + 0.1},${selectedLocation.lat + 0.1}&layer=mapnik`}
            />
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