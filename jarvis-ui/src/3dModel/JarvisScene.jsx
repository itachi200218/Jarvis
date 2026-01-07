import { Canvas, useFrame } from "@react-three/fiber";
import { useRef } from "react";
import * as THREE from "three";

/* =========================
   FIRE AURA (COLOR SHIFTING)
========================= */
function FireAura({ scale = 2 }) {
  const ref = useRef();
  const materialRef = useRef();

  const colors = [
    new THREE.Color("#22d3ee"), // cyan
    new THREE.Color("#60a5fa"), // blue
    new THREE.Color("#a78bfa"), // purple
    new THREE.Color("#ef4444"), // 🔥 red
    new THREE.Color("#f97316"), // orange
  ];

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    // 🔁 rotation + unstable motion
    ref.current.rotation.z += 0.002;
    ref.current.rotation.x = Math.sin(t * 0.6) * 0.08;
    ref.current.rotation.y = Math.cos(t * 0.4) * 0.08;

    // 💓 breathing
    const pulse =
      1 +
      Math.sin(t * 2.5) * 0.05 +
      Math.sin(t * 6.5) * 0.02;

    ref.current.scale.setScalar(scale * pulse);

    // 🎨 COLOR CYCLE (EVERY 5 SECONDS)
    const index = Math.floor(t / 5) % colors.length;
    const nextIndex = (index + 1) % colors.length;

    const blend = (t % 5) / 5; // smooth blend 0 → 1

    const currentColor = colors[index].clone().lerp(
      colors[nextIndex],
      blend
    );

    materialRef.current.uniforms.color.value.copy(currentColor);
    materialRef.current.uniforms.intensity.value =
      0.25 + Math.sin(t * 3) * 0.08;
  });

  return (
    <mesh ref={ref}>
      <sphereGeometry args={[1, 64, 64]} />
      <shaderMaterial
        ref={materialRef}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        uniforms={{
          color: { value: new THREE.Color("#22d3ee") },
          intensity: { value: 0.3 },
        }}
        vertexShader={`
          varying vec2 vUv;
          void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);
          }
        `}
        fragmentShader={`
          varying vec2 vUv;
          uniform vec3 color;
          uniform float intensity;

          float noise(vec2 p){
            return sin(p.x*10.0)*sin(p.y*10.0);
          }

          void main(){
            vec2 uv = vUv - 0.5;
            float d = length(uv);

            float n = noise(uv * 4.0);
            float edge = smoothstep(0.55, 0.25 + n * 0.2, d);

            float alpha = (1.0 - edge) * intensity;
            gl_FragColor = vec4(color, alpha);
          }
        `}
      />
    </mesh>
  );
}


/* =========================
   ENERGY RING (ALWAYS MOVING)
========================= */
function EnergyRing({ radius, thickness, speed, tilt, color }) {
  const ref = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    ref.current.rotation.z += speed;
    ref.current.rotation.x = tilt + Math.sin(t * 0.6) * 0.12;
    ref.current.rotation.y = Math.cos(t * 0.5) * 0.12;

    // subtle breathing
    const scale = 1 + Math.sin(t * 2) * 0.015;
    ref.current.scale.set(scale, scale, scale);
  });

  return (
    <mesh ref={ref}>
      <torusGeometry args={[radius, thickness, 32, 200]} />
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={2.5}
        metalness={0.85}
        roughness={0.2}
        toneMapped={false}
      />
    </mesh>
  );
}

/* =========================
   CORE (REACTS TO SPEECH)
========================= */
function Core({ active }) {
  const ref = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    const pulse = active
      ? 1 + Math.sin(t * 6) * 0.22
      : 1 + Math.sin(t * 2) * 0.1;

    ref.current.scale.setScalar(pulse);
  });

  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.22, 32, 32]} />
      <meshStandardMaterial
        color="#e0f2fe"
        emissive="#60a5fa"
        emissiveIntensity={active ? 3.8 : 2.2}
        toneMapped={false}
      />
    </mesh>
  );
}

/* =========================
   MAIN SCENE
========================= */
export default function JarvisScene({ speaking = false }) {
  return (
    <Canvas
      camera={{ position: [0, 0, 4.6], fov: 45 }}
      gl={{ alpha: true, antialias: true }}
    >
      {/* LIGHTING */}
      <ambientLight intensity={0.25} />
      <pointLight position={[3, 3, 4]} intensity={2.4} />
      <pointLight position={[-3, -3, -4]} intensity={1.8} />

      <group>
        {/* 🔥 FIRE AURA */}
        <FireAura scale={2.4} active={speaking} />
        <FireAura scale={2.1} active={speaking} />
        <FireAura scale={1.8} active={speaking} />

        {/* 🔵 MOVING RINGS */}
        <EnergyRing radius={1.6} thickness={0.035} speed={0.004} tilt={0.35} color="#2563eb" />
        <EnergyRing radius={1.25} thickness={0.045} speed={-0.005} tilt={-0.25} color="#60a5fa" />
        <EnergyRing radius={0.95} thickness={0.03} speed={0.006} tilt={0.15} color="#93c5fd" />

        {/* ❤️ CORE */}
        <Core active={speaking} />
      </group>
    </Canvas>
  );
}
