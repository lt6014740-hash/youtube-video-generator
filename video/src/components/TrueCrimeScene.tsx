import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { TrueCrimeSceneData } from "../types";
import { Particles } from "./Particles";
import { ProgressBar } from "./ProgressBar";
import { Timeline, type TimelineEvent } from "./Timeline";
import { Transition, type TransitionType } from "./Transition";

interface TrueCrimeSceneProps {
  scene: TrueCrimeSceneData;
  sceneIndex: number;
  totalScenes: number;
  timelineEvents: TimelineEvent[];
  accentColor: string;
  fontFamily: string;
}

const TRANSITION_TYPES: TransitionType[] = [
  "fade", "zoom", "wipe", "slideLeft", "slideUp", "fade",
];

export const TrueCrimeScene: React.FC<TrueCrimeSceneProps> = ({
  scene,
  sceneIndex,
  totalScenes,
  timelineEvents,
  accentColor,
  fontFamily,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const transitionType = TRANSITION_TYPES[sceneIndex % TRANSITION_TYPES.length];

  const titleAppear = spring({
    frame, fps,
    config: { damping: 15, stiffness: 80 },
    delay: 8,
  });

  const contentAppear = spring({
    frame, fps,
    config: { damping: 15, stiffness: 60 },
    delay: 20,
  });

  const evidenceAppear = spring({
    frame, fps,
    config: { damping: 12, stiffness: 50 },
    delay: 35,
  });

  const imageZoom = interpolate(
    frame,
    [0, fps * scene.durationInSeconds],
    [1.0, 1.1],
    { extrapolateRight: "clamp" }
  );

  const scanlineY = interpolate(
    frame % 120,
    [0, 120],
    [0, 1080],
  );

  const phaseLabel = scene.phase || "";
  const PHASE_COLORS: Record<string, string> = {
    "BỐI CẢNH": "#3b82f6",
    "DIỄN BIẾN": "#f59e0b",
    "PHIÊN TÒA": "#ef4444",
    "PHÁN QUYẾT": "#10b981",
    "BÀI HỌC": "#8b5cf6",
  };
  const phaseColor = PHASE_COLORS[phaseLabel] || accentColor;

  return (
    <AbsoluteFill>
      <Transition type={transitionType} durationInFrames={12}>
        {/* Background image or dark gradient */}
        {scene.imageFile ? (
          <AbsoluteFill style={{ overflow: "hidden" }}>
            <Img
              src={staticFile(scene.imageFile)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                transform: `scale(${imageZoom})`,
                filter: "brightness(0.4) contrast(1.1)",
              }}
            />
            {/* Red/dark overlay for crime theme */}
            <AbsoluteFill
              style={{
                background: `linear-gradient(180deg, rgba(10,0,0,0.7) 0%, rgba(20,0,0,0.3) 40%, rgba(10,0,0,0.8) 100%)`,
              }}
            />
            {/* Scanline effect */}
            <AbsoluteFill
              style={{
                background: `repeating-linear-gradient(
                  0deg,
                  transparent,
                  transparent 2px,
                  rgba(0,0,0,0.03) 2px,
                  rgba(0,0,0,0.03) 4px
                )`,
              }}
            />
            {/* Moving scanline */}
            <div
              style={{
                position: "absolute",
                top: scanlineY,
                left: 0,
                right: 0,
                height: 2,
                background: `linear-gradient(90deg, transparent, ${accentColor}30, transparent)`,
              }}
            />
          </AbsoluteFill>
        ) : (
          <AbsoluteFill
            style={{
              background: "linear-gradient(135deg, #0a0a0a 0%, #1a0a0a 50%, #0a0a0a 100%)",
            }}
          />
        )}

        {/* Particles */}
        <Particles accentColor={accentColor} count={8} />

        {/* Progress bar */}
        <ProgressBar
          accentColor={accentColor}
          totalScenes={totalScenes}
          currentSceneIndex={sceneIndex}
        />

        {/* Timeline on the left */}
        <Timeline
          events={timelineEvents}
          activeIndex={sceneIndex}
          accentColor={accentColor}
          fontFamily={fontFamily}
        />

        {/* Phase badge (top center) */}
        {phaseLabel && (
          <div
            style={{
              position: "absolute",
              top: 50,
              left: "50%",
              transform: `translate(-50%, 0) scale(${titleAppear})`,
              opacity: titleAppear,
            }}
          >
            <div
              style={{
                background: phaseColor,
                padding: "8px 28px",
                borderRadius: 8,
                fontSize: 16,
                fontWeight: 800,
                color: "#fff",
                fontFamily,
                letterSpacing: 3,
                textTransform: "uppercase",
                boxShadow: `0 4px 20px ${phaseColor}60`,
              }}
            >
              {phaseLabel}
            </div>
          </div>
        )}

        {/* Main content (right side, since timeline is left) */}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "55%",
            transform: "translate(-30%, -50%)",
            width: "55%",
            textAlign: "left",
          }}
        >
          {/* Scene title */}
          <h2
            style={{
              color: "#ffffff",
              fontSize: 46,
              fontFamily,
              fontWeight: 800,
              margin: "0 0 20px 0",
              opacity: titleAppear,
              transform: `translateY(${interpolate(titleAppear, [0, 1], [30, 0])}px)`,
              textShadow: `0 2px 12px rgba(0,0,0,0.8), 0 0 40px ${accentColor}20`,
              lineHeight: 1.3,
              borderLeft: `4px solid ${phaseColor}`,
              paddingLeft: 20,
            }}
          >
            {scene.title}
          </h2>

          {/* Evidence/quote box */}
          {scene.evidence && (
            <div
              style={{
                opacity: evidenceAppear,
                transform: `translateY(${interpolate(evidenceAppear, [0, 1], [20, 0])}px)`,
                marginTop: 20,
              }}
            >
              <div
                style={{
                  background: "rgba(0,0,0,0.6)",
                  backdropFilter: "blur(8px)",
                  borderRadius: 14,
                  padding: "20px 24px",
                  borderLeft: `4px solid ${accentColor}`,
                  position: "relative",
                }}
              >
                <div
                  style={{
                    fontSize: 12,
                    fontWeight: 700,
                    color: accentColor,
                    fontFamily,
                    letterSpacing: 2,
                    textTransform: "uppercase",
                    marginBottom: 10,
                  }}
                >
                  📋 {scene.evidenceLabel || "BẰNG CHỨNG"}
                </div>
                <p
                  style={{
                    color: "#e0e0e0",
                    fontSize: 22,
                    fontFamily,
                    fontWeight: 500,
                    fontStyle: "italic",
                    margin: 0,
                    lineHeight: 1.5,
                  }}
                >
                  &ldquo;{scene.evidence}&rdquo;
                </p>
              </div>
            </div>
          )}
        </div>

        {/* "Vụ án" watermark */}
        <div
          style={{
            position: "absolute",
            bottom: 30,
            right: 40,
            opacity: 0.15,
            fontSize: 60,
            fontWeight: 900,
            color: accentColor,
            fontFamily,
            letterSpacing: 8,
            textTransform: "uppercase",
          }}
        >
          ⚖️ VỤ ÁN
        </div>

        {/* Audio */}
        {scene.audioFile && (
          <Audio src={staticFile(scene.audioFile)} />
        )}
      </Transition>
    </AbsoluteFill>
  );
};
