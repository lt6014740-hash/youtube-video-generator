import React from "react";
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export interface TimelineEvent {
  time: string;
  label: string;
  icon?: string;
}

interface TimelineProps {
  events: TimelineEvent[];
  activeIndex: number;
  accentColor: string;
  fontFamily: string;
}

export const Timeline: React.FC<TimelineProps> = ({
  events,
  activeIndex,
  accentColor,
  fontFamily,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const appear = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 70 },
    delay: 5,
  });

  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        top: "50%",
        transform: "translateY(-50%)",
        display: "flex",
        flexDirection: "column",
        gap: 0,
        opacity: appear,
      }}
    >
      {events.map((event, i) => {
        const isActive = i === activeIndex;
        const isPast = i < activeIndex;
        const dotDelay = 8 + i * 6;
        const dotAppear = spring({
          frame,
          fps,
          config: { damping: 12, stiffness: 90 },
          delay: dotDelay,
        });

        const pulsePhase = isActive
          ? interpolate(frame % 50, [0, 25, 50], [1, 1.3, 1])
          : 1;

        return (
          <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 16 }}>
            {/* Vertical line + dot */}
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                opacity: dotAppear,
              }}
            >
              {/* Dot */}
              <div
                style={{
                  width: isActive ? 22 : 14,
                  height: isActive ? 22 : 14,
                  borderRadius: "50%",
                  background: isActive
                    ? accentColor
                    : isPast
                      ? `${accentColor}aa`
                      : "rgba(255,255,255,0.2)",
                  border: isActive ? `3px solid #fff` : "none",
                  transform: `scale(${pulsePhase})`,
                  boxShadow: isActive ? `0 0 16px ${accentColor}` : "none",
                  transition: "all 0.3s",
                }}
              />
              {/* Connecting line */}
              {i < events.length - 1 && (
                <div
                  style={{
                    width: 3,
                    height: 40,
                    background: isPast
                      ? `${accentColor}88`
                      : "rgba(255,255,255,0.1)",
                  }}
                />
              )}
            </div>

            {/* Event info */}
            <div
              style={{
                transform: `translateX(${interpolate(dotAppear, [0, 1], [30, 0])}px)`,
                opacity: dotAppear,
                paddingBottom: 26,
              }}
            >
              <div
                style={{
                  fontSize: 13,
                  fontWeight: 700,
                  color: isActive ? accentColor : "rgba(255,255,255,0.4)",
                  fontFamily,
                  letterSpacing: 1,
                  textTransform: "uppercase",
                  marginBottom: 4,
                }}
              >
                {event.icon && `${event.icon} `}{event.time}
              </div>
              <div
                style={{
                  fontSize: isActive ? 18 : 15,
                  fontWeight: isActive ? 700 : 500,
                  color: isActive ? "#fff" : "rgba(255,255,255,0.5)",
                  fontFamily,
                  maxWidth: 220,
                  lineHeight: 1.3,
                }}
              >
                {event.label}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
