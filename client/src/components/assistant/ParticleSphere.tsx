import * as THREE from "three";
import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";

// ─── constants ───────────────────────────────────────────────────────────────
const COUNT = 3000;
const RADIUS = 1.5;

// ─── 3D particle sphere ───────────────────────────────────────────────────────
export default function ParticleSphere({
  amplitudeRef,
  appState,
}: {
  amplitudeRef: React.MutableRefObject<number>;
  appState: string;
}) {
  const pointsRef = useRef<THREE.Points>(null);
  const materialRef = useRef<THREE.PointsMaterial>(null);

  const { orig, pos } = useMemo(() => {
    const orig = new Float32Array(COUNT * 3);
    const pos = new Float32Array(COUNT * 3);
    for (let i = 0; i < COUNT; i++) {
      const theta = Math.random() * 2 * Math.PI;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = Math.cbrt(Math.random()) * RADIUS;
      const x = r * Math.sin(phi) * Math.cos(theta);
      const y = r * Math.cos(phi);
      const z = r * Math.sin(phi) * Math.sin(theta);
      orig[i * 3] = pos[i * 3] = x;
      orig[i * 3 + 1] = pos[i * 3 + 1] = y;
      orig[i * 3 + 2] = pos[i * 3 + 2] = z;
    }
    return { orig, pos };
  }, []);

  useFrame(({ clock }) => {
    if (!pointsRef.current || !materialRef.current) return;
    const t = clock.getElapsedTime();
    const amp = amplitudeRef.current;

    const rotationSpeed = appState === "idle" ? 0.05 : 0.15;
    pointsRef.current.rotation.y += rotationSpeed * 0.05;
    pointsRef.current.rotation.x += rotationSpeed * 0.02;

    let targetColor = "#ffffff";
    if (appState === "listening") targetColor = "#eab308";
    if (appState === "responding") targetColor = "#22c55e";
    materialRef.current.color.lerp(new THREE.Color(targetColor), 0.08);

    const attr = pointsRef.current.geometry.attributes.position;
    const arr = attr.array as Float32Array;

    for (let i = 0; i < COUNT; i++) {
      const ox = orig[i * 3],
        oy = orig[i * 3 + 1],
        oz = orig[i * 3 + 2];
      const noise =
        Math.sin(ox * 1.5 + t * 2) *
        Math.cos(oy * 1.5 - t * 1.5) *
        Math.sin(oz * 1.5 + t);
      const wave = (noise + 1) / 2;
      const push = 1 + amp * 1.8 * wave + amp * 0.2;
      arr[i * 3] = ox * push;
      arr[i * 3 + 1] = oy * push;
      arr[i * 3 + 2] = oz * push;
    }
    attr.needsUpdate = true;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={COUNT}
          array={pos}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        ref={materialRef}
        size={0.055}
        color="#ffffff"
        transparent
        opacity={0.89}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  );
};