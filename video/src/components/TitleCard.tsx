import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

interface TitleCardProps {
  title: string;
  backgroundColor: string;
  accentColor: string;
  subtitleColor: string;
  fontFamily: string;
  language: string;
}

export const TitleCard: React.FC<TitleCardProps> = ({
  title,
  backgroundColor,
  accentColor,
  subtitleColor,
  fontFamily,
  language,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 60 },
    delay: 10,
  });

  const lineWidth = interpolate(
    frame,
    [15, 45],
    [0, 400],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const fadeOut = interpolate(
    frame,
    [durationInFrames - 15, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const pulseScale = interpolate(
    frame,
    [0, 30, 60],
    [1, 1.05, 1],
    { extrapolateRight: "extend" }
  );

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, ${backgroundColor} 0%, #000000 100%)`,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        opacity: fadeOut,
      }}
    >
      {/* Animated background circles */}
      <div
        style={{
          position: "absolute",
          width: 600,
          height: 600,
          borderRadius: "50%",
          border: `2px solid ${accentColor}30`,
          transform: `scale(${pulseScale})`,
        }}
      />
      <div
        style={{
          position: "absolute",
          width: 400,
          height: 400,
          borderRadius: "50%",
          border: `2px solid ${accentColor}20`,
          transform: `scale(${pulseScale * 1.1})`,
        }}
      />

      <div
        style={{
          textAlign: "center",
          padding: "0 100px",
          transform: `translateY(${interpolate(titleSpring, [0, 1], [60, 0])}px)`,
          opacity: titleSpring,
        }}
      >
        {/* Accent line top */}
        <div
          style={{
            width: lineWidth,
            height: 4,
            background: `linear-gradient(90deg, transparent, ${accentColor}, transparent)`,
            margin: "0 auto 40px",
            borderRadius: 2,
          }}
        />

        <h1
          style={{
            color: subtitleColor,
            fontSize: 72,
            fontFamily,
            fontWeight: 900,
            margin: 0,
            lineHeight: 1.2,
            textShadow: `0 4px 20px ${accentColor}40`,
            letterSpacing: -1,
          }}
        >
          {title}
        </h1>

        {/* Accent line bottom */}
        <div
          style={{
            width: lineWidth,
            height: 4,
            background: `linear-gradient(90deg, transparent, ${accentColor}, transparent)`,
            margin: "40px auto 0",
            borderRadius: 2,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
