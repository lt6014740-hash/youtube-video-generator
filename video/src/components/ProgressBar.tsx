import React from "react";
import {
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

interface ProgressBarProps {
  accentColor: string;
  totalScenes: number;
  currentSceneIndex: number;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  accentColor,
  totalScenes,
  currentSceneIndex,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const localProgress = interpolate(
    frame,
    [0, durationInFrames],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const shimmerX = interpolate(
    frame % 60,
    [0, 60],
    [-200, 1920],
  );

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: 6,
        background: "rgba(255,255,255,0.1)",
      }}
    >
      {/* Overall scene segments */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "100%",
          display: "flex",
          gap: 2,
        }}
      >
        {Array.from({ length: totalScenes }).map((_, i) => (
          <div
            key={i}
            style={{
              flex: 1,
              height: "100%",
              background:
                i < currentSceneIndex
                  ? accentColor
                  : i === currentSceneIndex
                    ? `linear-gradient(90deg, ${accentColor} ${localProgress * 100}%, rgba(255,255,255,0.15) ${localProgress * 100}%)`
                    : "rgba(255,255,255,0.08)",
              borderRadius: 3,
              overflow: "hidden",
              position: "relative",
            }}
          >
            {/* Shimmer effect on active segment */}
            {i === currentSceneIndex && (
              <div
                style={{
                  position: "absolute",
                  top: 0,
                  left: shimmerX - 100,
                  width: 100,
                  height: "100%",
                  background: `linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)`,
                }}
              />
            )}
          </div>
        ))}
      </div>

      {/* Scene counter */}
      <div
        style={{
          position: "absolute",
          top: 14,
          right: 20,
          fontSize: 14,
          color: "rgba(255,255,255,0.5)",
          fontFamily: "Inter, system-ui, sans-serif",
          fontWeight: 600,
        }}
      >
        {currentSceneIndex + 1}/{totalScenes}
      </div>
    </div>
  );
};
