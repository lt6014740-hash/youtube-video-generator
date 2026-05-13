import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

interface HighlightProps {
  text: string;
  accentColor: string;
  fontFamily: string;
  delay?: number;
}

export const Highlight: React.FC<HighlightProps> = ({
  text,
  accentColor,
  fontFamily,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const appear = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 80 },
    delay,
  });

  const glowPulse = interpolate(
    frame,
    [delay + 20, delay + 50, delay + 80],
    [0, 1, 0.6],
    { extrapolateLeft: "clamp", extrapolateRight: "extend" }
  );

  const borderDraw = interpolate(
    frame,
    [delay + 5, delay + 30],
    [0, 100],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        display: "inline-block",
        position: "relative",
        opacity: appear,
        transform: `scale(${interpolate(appear, [0, 1], [0.9, 1])})`,
      }}
    >
      {/* Glow background */}
      <div
        style={{
          position: "absolute",
          inset: -8,
          background: `${accentColor}${Math.round(glowPulse * 40).toString(16).padStart(2, "0")}`,
          borderRadius: 16,
          filter: `blur(${8 + glowPulse * 4}px)`,
        }}
      />

      {/* Animated border */}
      <div
        style={{
          position: "absolute",
          inset: -4,
          borderRadius: 14,
          background: `conic-gradient(from 0deg, ${accentColor} ${borderDraw}%, transparent ${borderDraw}%)`,
          mask: "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
          maskComposite: "exclude",
          WebkitMaskComposite: "xor",
          padding: 3,
        }}
      />

      {/* Text content */}
      <span
        style={{
          position: "relative",
          color: "#ffffff",
          fontSize: 48,
          fontFamily,
          fontWeight: 800,
          padding: "8px 24px",
          display: "inline-block",
          textShadow: `0 0 ${10 + glowPulse * 10}px ${accentColor}`,
        }}
      >
        {text}
      </span>
    </div>
  );
};
