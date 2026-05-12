import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

interface BackgroundProps {
  backgroundColor: string;
  accentColor: string;
  sceneIndex: number;
}

const GRADIENT_PAIRS = [
  ["#1a1a2e", "#16213e"],
  ["#0f3460", "#533483"],
  ["#16213e", "#1a1a2e"],
  ["#533483", "#0f3460"],
  ["#1a1a2e", "#0f3460"],
];

export const Background: React.FC<BackgroundProps> = ({
  backgroundColor,
  accentColor,
  sceneIndex,
}) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const gradientPair =
    GRADIENT_PAIRS[sceneIndex % GRADIENT_PAIRS.length] || [backgroundColor, "#000000"];

  const rotation = interpolate(frame, [0, 300], [0, 360], {
    extrapolateRight: "extend",
  });

  const scale = interpolate(frame, [0, 150, 300], [1, 1.2, 1], {
    extrapolateRight: "extend",
  });

  return (
    <AbsoluteFill>
      <div
        style={{
          width: "100%",
          height: "100%",
          background: `linear-gradient(135deg, ${gradientPair[0]} 0%, ${gradientPair[1]} 100%)`,
        }}
      />

      {/* Animated accent circles */}
      <div
        style={{
          position: "absolute",
          top: "20%",
          right: "10%",
          width: 300,
          height: 300,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${accentColor}20 0%, transparent 70%)`,
          transform: `rotate(${rotation}deg) scale(${scale})`,
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "15%",
          left: "5%",
          width: 200,
          height: 200,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${accentColor}15 0%, transparent 70%)`,
          transform: `rotate(${-rotation}deg) scale(${scale * 0.8})`,
        }}
      />

      {/* Grid pattern overlay */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundImage: `
            linear-gradient(${accentColor}08 1px, transparent 1px),
            linear-gradient(90deg, ${accentColor}08 1px, transparent 1px)
          `,
          backgroundSize: "60px 60px",
          opacity: 0.5,
        }}
      />
    </AbsoluteFill>
  );
};
