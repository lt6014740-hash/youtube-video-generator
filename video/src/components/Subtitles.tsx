import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { SubtitleData } from "../types";

interface SubtitlesProps {
  subtitles: SubtitleData[];
  color: string;
  accentColor: string;
  fontFamily: string;
}

export const Subtitles: React.FC<SubtitlesProps> = ({
  subtitles,
  color,
  accentColor,
  fontFamily,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const currentSubtitle = subtitles.find(
    (s) => frame >= s.startFrame && frame <= s.endFrame
  );

  if (!currentSubtitle) return null;

  const localFrame = frame - currentSubtitle.startFrame;
  const duration = currentSubtitle.endFrame - currentSubtitle.startFrame;

  const fadeIn = spring({
    frame: localFrame,
    fps,
    config: { damping: 20, stiffness: 100 },
  });

  const fadeOut = interpolate(
    localFrame,
    [duration - 10, duration],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const translateY = interpolate(
    localFrame,
    [0, 10],
    [20, 0],
    { extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        position: "absolute",
        bottom: 120,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: "0 80px",
        opacity: fadeIn * fadeOut,
        transform: `translateY(${translateY}px)`,
      }}
    >
      <div
        style={{
          background: "rgba(0, 0, 0, 0.75)",
          backdropFilter: "blur(10px)",
          borderRadius: 16,
          padding: "20px 40px",
          borderLeft: `4px solid ${accentColor}`,
          maxWidth: "80%",
        }}
      >
        <p
          style={{
            color,
            fontSize: 42,
            fontFamily,
            fontWeight: 600,
            textAlign: "center",
            margin: 0,
            lineHeight: 1.5,
            textShadow: "0 2px 4px rgba(0,0,0,0.5)",
          }}
        >
          {currentSubtitle.text}
        </p>
      </div>
    </div>
  );
};
