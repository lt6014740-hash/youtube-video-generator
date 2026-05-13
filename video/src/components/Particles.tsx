import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
} from "remotion";

interface ParticlesProps {
  accentColor: string;
  count?: number;
}

interface Particle {
  x: number;
  y: number;
  size: number;
  speed: number;
  delay: number;
  opacity: number;
}

const generateParticles = (count: number): Particle[] => {
  const particles: Particle[] = [];
  for (let i = 0; i < count; i++) {
    const seed = i * 137.508;
    particles.push({
      x: (seed * 7.31) % 100,
      y: (seed * 3.17) % 100,
      size: 2 + (seed % 4),
      speed: 0.3 + (seed % 1),
      delay: (seed * 2.13) % 60,
      opacity: 0.15 + ((seed * 1.7) % 0.35),
    });
  }
  return particles;
};

export const Particles: React.FC<ParticlesProps> = ({
  accentColor,
  count = 15,
}) => {
  const frame = useCurrentFrame();
  const particles = React.useMemo(() => generateParticles(count), [count]);

  return (
    <AbsoluteFill style={{ pointerEvents: "none", overflow: "hidden" }}>
      {particles.map((p, i) => {
        const yOffset = interpolate(
          (frame + p.delay) * p.speed,
          [0, 300],
          [0, -120],
          { extrapolateRight: "extend" }
        );

        const xDrift = Math.sin((frame + p.delay) * 0.02 * p.speed) * 30;

        const twinkle = interpolate(
          (frame + p.delay * 3) % 80,
          [0, 40, 80],
          [p.opacity * 0.5, p.opacity, p.opacity * 0.5],
        );

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${p.x}%`,
              top: `${p.y}%`,
              width: p.size,
              height: p.size,
              borderRadius: "50%",
              background: accentColor,
              opacity: twinkle,
              transform: `translate(${xDrift}px, ${yOffset}px)`,
              boxShadow: `0 0 ${p.size * 2}px ${accentColor}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
