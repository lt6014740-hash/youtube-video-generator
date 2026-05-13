import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

interface RatingBarProps {
  label: string;
  value: number;
  maxValue: number;
  accentColor: string;
  fontFamily: string;
  delay?: number;
  barColor?: string;
}

export const RatingBar: React.FC<RatingBarProps> = ({
  label,
  value,
  maxValue,
  accentColor,
  fontFamily,
  delay = 0,
  barColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const appear = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 80 },
    delay,
  });

  const fillWidth = interpolate(
    frame,
    [delay + 10, delay + 45],
    [0, (value / maxValue) * 100],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const countUp = interpolate(
    frame,
    [delay + 10, delay + 45],
    [0, value],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const color = barColor || accentColor;

  return (
    <div
      style={{
        opacity: appear,
        transform: `translateX(${interpolate(appear, [0, 1], [-40, 0])}px)`,
        marginBottom: 12,
      }}
    >
      {/* Label row */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 6,
        }}
      >
        <span
          style={{
            fontSize: 18,
            fontWeight: 600,
            color: "#ffffff",
            fontFamily,
          }}
        >
          {label}
        </span>
        <span
          style={{
            fontSize: 20,
            fontWeight: 800,
            color,
            fontFamily,
          }}
        >
          {countUp.toFixed(1)}/{maxValue}
        </span>
      </div>

      {/* Bar background */}
      <div
        style={{
          width: "100%",
          height: 10,
          background: "rgba(255,255,255,0.1)",
          borderRadius: 5,
          overflow: "hidden",
          position: "relative",
        }}
      >
        {/* Fill */}
        <div
          style={{
            width: `${fillWidth}%`,
            height: "100%",
            background: `linear-gradient(90deg, ${color}cc, ${color})`,
            borderRadius: 5,
            position: "relative",
          }}
        >
          {/* Shimmer */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: interpolate(frame % 40, [0, 40], [-50, 300]),
              width: 50,
              height: "100%",
              background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)",
            }}
          />
        </div>
      </div>
    </div>
  );
};
