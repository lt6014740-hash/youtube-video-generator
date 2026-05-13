import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export interface ReactionEmoji {
  emoji: string;
  label: string;
  count: number;
  color: string;
}

interface ReactionBarProps {
  reactions: ReactionEmoji[];
  accentColor: string;
  fontFamily: string;
  delay?: number;
}

export const ReactionBar: React.FC<ReactionBarProps> = ({
  reactions,
  accentColor,
  fontFamily,
  delay = 20,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const containerAppear = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 70 },
    delay,
  });

  const totalCount = reactions.reduce((sum, r) => sum + r.count, 0);

  return (
    <div
      style={{
        display: "flex",
        gap: 16,
        opacity: containerAppear,
        transform: `translateY(${interpolate(containerAppear, [0, 1], [30, 0])}px)`,
      }}
    >
      {reactions.map((reaction, i) => {
        const itemDelay = delay + 5 + i * 8;
        const itemAppear = spring({
          frame,
          fps,
          config: { damping: 12, stiffness: 100 },
          delay: itemDelay,
        });

        const bounce = interpolate(
          frame,
          [itemDelay + 10, itemDelay + 20, itemDelay + 30],
          [1, 1.3, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );

        const countUp = Math.round(
          interpolate(
            frame,
            [itemDelay, itemDelay + 30],
            [0, reaction.count],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
          )
        );

        const barWidth = totalCount > 0
          ? interpolate(
              frame,
              [itemDelay + 10, itemDelay + 40],
              [0, (reaction.count / totalCount) * 100],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            )
          : 0;

        return (
          <div
            key={i}
            style={{
              background: "rgba(0,0,0,0.5)",
              backdropFilter: "blur(8px)",
              borderRadius: 16,
              padding: "14px 20px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 8,
              minWidth: 100,
              opacity: itemAppear,
              transform: `scale(${itemAppear})`,
              border: `1px solid rgba(255,255,255,0.08)`,
              position: "relative",
              overflow: "hidden",
            }}
          >
            {/* Fill bar */}
            <div
              style={{
                position: "absolute",
                bottom: 0,
                left: 0,
                right: 0,
                height: `${barWidth}%`,
                background: `${reaction.color}20`,
                borderRadius: 16,
              }}
            />

            <span
              style={{
                fontSize: 36,
                transform: `scale(${bounce})`,
                display: "block",
                position: "relative",
              }}
            >
              {reaction.emoji}
            </span>
            <span
              style={{
                fontSize: 18,
                fontWeight: 800,
                color: reaction.color,
                fontFamily,
                position: "relative",
              }}
            >
              {countUp.toLocaleString()}
            </span>
            <span
              style={{
                fontSize: 12,
                fontWeight: 600,
                color: "rgba(255,255,255,0.5)",
                fontFamily,
                textTransform: "uppercase",
                letterSpacing: 1,
                position: "relative",
              }}
            >
              {reaction.label}
            </span>
          </div>
        );
      })}
    </div>
  );
};
