import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type TransitionType = "fade" | "slideLeft" | "slideUp" | "zoom" | "wipe" | "glitch";

interface TransitionProps {
  type: TransitionType;
  durationInFrames?: number;
  children: React.ReactNode;
}

export const Transition: React.FC<TransitionProps> = ({
  type,
  durationInFrames = 15,
  children,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames: totalDuration } = useVideoConfig();

  const enterProgress = interpolate(
    frame,
    [0, durationInFrames],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // exitProgress goes from 1 (fully visible) to 0 (fully exited)
  const exitProgress = interpolate(
    frame,
    [totalDuration - durationInFrames, totalDuration],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const getEnterStyle = (): React.CSSProperties => {
    switch (type) {
      case "fade":
        return { opacity: enterProgress };
      case "slideLeft":
        return {
          opacity: enterProgress,
          transform: `translateX(${interpolate(enterProgress, [0, 1], [100, 0])}px)`,
        };
      case "slideUp":
        return {
          opacity: enterProgress,
          transform: `translateY(${interpolate(enterProgress, [0, 1], [80, 0])}px)`,
        };
      case "zoom":
        return {
          opacity: enterProgress,
          transform: `scale(${interpolate(enterProgress, [0, 1], [1.3, 1])})`,
        };
      case "wipe": {
        const clipPercent = interpolate(enterProgress, [0, 1], [100, 0]);
        return {
          clipPath: `inset(0 ${clipPercent}% 0 0)`,
        };
      }
      case "glitch": {
        const glitchOffset = frame < durationInFrames
          ? Math.sin(frame * 3) * (1 - enterProgress) * 20
          : 0;
        return {
          opacity: enterProgress,
          transform: `translateX(${glitchOffset}px)`,
          filter: frame < durationInFrames / 2
            ? `hue-rotate(${(1 - enterProgress) * 90}deg)`
            : "none",
        };
      }
      default:
        return { opacity: enterProgress };
    }
  };

  const getExitStyle = (): React.CSSProperties => {
    // exitProgress: 1 = visible, 0 = gone
    switch (type) {
      case "fade":
        return { opacity: exitProgress };
      case "slideLeft":
        return {
          opacity: exitProgress,
          transform: `translateX(${(1 - exitProgress) * -100}px)`,
        };
      case "slideUp":
        return {
          opacity: exitProgress,
          transform: `translateY(${(1 - exitProgress) * -60}px)`,
        };
      case "zoom":
        return {
          opacity: exitProgress,
          transform: `scale(${0.8 + exitProgress * 0.2})`,
        };
      case "wipe": {
        const clipPercent = (1 - exitProgress) * 100;
        return {
          clipPath: `inset(0 0 0 ${clipPercent}%)`,
        };
      }
      case "glitch":
        return { opacity: exitProgress };
      default:
        return { opacity: exitProgress };
    }
  };

  const isExiting = frame > totalDuration - durationInFrames;
  const style = isExiting ? getExitStyle() : getEnterStyle();

  return (
    <AbsoluteFill style={style}>
      {children}
    </AbsoluteFill>
  );
};
