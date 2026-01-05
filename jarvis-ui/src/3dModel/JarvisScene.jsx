import { Canvas, useFrame } from "@react-three/fiber";
import { useRef } from "react";
import * as THREE from "three";

/* =========================
   ROTATING RING
========================= */
function Ring({ radius, thickness, speed, tilt, phase, color }) {
  const ref = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() + phase;

    // 🔁 multi-axis rotation
    ref.current.rotation.z += speed;
    ref.current.rotation.x = tilt + Math.sin(t * 0.6) * 0.12;
    ref.current.rotation.y = Math.cos(t * 0.4) * 0.12;

    // 💓 subtle breathing
    const scale = 1 + Math.sin(t * 1.5) * 0.015;
    ref.current.scale.set(scale, scale, scale);
  });

  return (
    <mesh ref={ref}>
      <torusGeometry args={[radius, thickness, 32, 160]} />
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={1.6}
        metalness={0.85}
        roughness={0.2}
      />
    </mesh>
  );
}

/* =========================
   ARC CORE
========================= */
function Core() {
  const ref = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    // 💡 energy pulse
    const pulse = 1 + Math.sin(t * 3) * 0.12;
    ref.current.scale.set(pulse, pulse, pulse);
  });

  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.22, 32, 32]} />
      <meshStandardMaterial
        color="#e0f2fe"
        emissive="#60a5fa"
        emissiveIntensity={2.4}
        toneMapped={false}
      />
    </mesh>
  );
}

/* =========================
   SCENE
========================= */
export default function JarvisScene() {
  return (
    <Canvas
      camera={{ position: [0, 0, 4], fov: 45 }}
      gl={{ alpha: true, antialias: true }}
    >
      {/* LIGHTING */}
      <ambientLight intensity={0.35} />
      <pointLight position={[2, 2, 3]} intensity={2.2} />
      <pointLight position={[-2, -2, -3]} intensity={1.4} />

      {/* ARC REACTOR */}
      <group>
        <Ring
          radius={1.45}
          thickness={0.035}
          speed={0.003}
          tilt={0.3}
          phase={0}
          color="#2563eb"
        />
        <Ring
          radius={1.15}
          thickness={0.045}
          speed={-0.004}
          tilt={-0.2}
          phase={1.5}
          color="#60a5fa"
        />
        <Ring
          radius={0.85}
          thickness={0.03}
          speed={0.006}
          tilt={0.15}
          phase={3}
          color="#93c5fd"
        />
        <Core />
      </group>
    </Canvas>
  );
}
