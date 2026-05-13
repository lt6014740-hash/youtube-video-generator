import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

interface LowerThirdProps {
  source: string;
  category: string;
  accentColor: string;
  fontFamily: string;
}

export const LowerThird: React.FC<LowerThirdProps> = ({
  source,
  category,
  accentColor,
  fontFamily,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const slideIn = spring({
    frame,
    fps,
    config: { damping: 18, stiffness: 90 },
    delay: 10,
  });

  const slideOut = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames],
    [0, 200],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const tagSlide = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 100 },
    delay: 20,
  });

  const liveIndicatorPulse = interpolate(
    frame % 40,
    [0, 20, 40],
    [0.4, 1, 0.4],
  );

  return (
    <div
      style={{
        position: "absolute",
        bottom: 200,
        left: 0,
        right: 0,
        display: "flex",
        alignItems: "flex-end",
        padding: "0 60px",
        transform: `translateX(${interpolate(slideIn, [0, 1], [-600, 0]) + slideOut}px)`,
      }}
    >
      {/* Category tag */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 0,
        }}
      >
        <div
          style={{
            background: accentColor,
            padding: "10px 20px",
            display: "flex",
            alignItems: "center",
            gap: 8,
            opacity: tagSlide,
            transform: `scaleX(${tagSlide})`,
            transformOrigin: "left",
          }}
        >
          {/* Live dot */}
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              background: "#ff4444",
              opacity: liveIndicatorPulse,
              boxShadow: `0 0 ${6 + liveIndicatorPulse * 4}px #ff4444`,
            }}
          />
          <span
            style={{
              color: "#ffffff",
              fontSize: 16,
              fontFamily,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: 2,
            }}
          >
            {category}
          </span>
        </div>

        {/* Source info bar */}
        <div
          style={{
            background: "rgba(0,0,0,0.8)",
            backdropFilter: "blur(10px)",
            padding: "10px 24px",
            borderRight: `3px solid ${accentColor}`,
            opacity: slideIn,
          }}
        >
          <span
            style={{
              color: "#cccccc",
              fontSize: 15,
              fontFamily,
              fontWeight: 500,
            }}
          >
            Nguồn: {source}
          </span>
        </div>
      </div>
    </div>
  );
};
