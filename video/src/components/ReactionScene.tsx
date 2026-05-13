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
import type { ReactionSceneData } from "../types";
import { Particles } from "./Particles";
import { ProgressBar } from "./ProgressBar";
import { RatingBar } from "./RatingBar";
import { ReactionBar, type ReactionEmoji } from "./ReactionBar";
import { Transition, type TransitionType } from "./Transition";

interface ReactionSceneProps {
  scene: ReactionSceneData;
  sceneIndex: number;
  totalScenes: number;
  accentColor: string;
  fontFamily: string;
}

const TRANSITION_TYPES: TransitionType[] = [
  "zoom", "slideLeft", "fade", "wipe", "slideUp", "zoom",
];

export const ReactionScene: React.FC<ReactionSceneProps> = ({
  scene,
  sceneIndex,
  totalScenes,
  accentColor,
  fontFamily,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const transitionType = TRANSITION_TYPES[sceneIndex % TRANSITION_TYPES.length];

  const titleAppear = spring({
    frame, fps,
    config: { damping: 15, stiffness: 80 },
    delay: 5,
  });

  const contentAppear = spring({
    frame, fps,
    config: { damping: 15, stiffness: 60 },
    delay: 15,
  });

  const imageZoom = interpolate(
    frame,
    [0, fps * scene.durationInSeconds],
    [1.0, 1.08],
    { extrapolateRight: "clamp" }
  );

  const defaultReactions: ReactionEmoji[] = [
    { emoji: "😱", label: "Sốc", count: 0, color: "#ef4444" },
    { emoji: "🔥", label: "Hot", count: 0, color: "#f59e0b" },
    { emoji: "👏", label: "Hay", count: 0, color: "#10b981" },
    { emoji: "😂", label: "Hài", count: 0, color: "#3b82f6" },
  ];

  const reactions = scene.reactions || defaultReactions;

  return (
    <AbsoluteFill>
      <Transition type={transitionType} durationInFrames={12}>
        {/* Background */}
        {scene.imageFile ? (
          <AbsoluteFill style={{ overflow: "hidden" }}>
            <Img
              src={staticFile(scene.imageFile)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                transform: `scale(${imageZoom})`,
              }}
            />
            <AbsoluteFill
              style={{
                background:
                  "linear-gradient(180deg, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.2) 35%, rgba(0,0,0,0.75) 100%)",
              }}
            />
          </AbsoluteFill>
        ) : (
          <AbsoluteFill
            style={{
              background: "linear-gradient(135deg, #0f0a1e 0%, #1a0a2e 50%, #0a0a1e 100%)",
            }}
          />
        )}

        {/* Particles */}
        <Particles accentColor={accentColor} count={10} />

        {/* Progress bar */}
        <ProgressBar
          accentColor={accentColor}
          totalScenes={totalScenes}
          currentSceneIndex={sceneIndex}
        />

        {/* Category badge */}
        <div
          style={{
            position: "absolute",
            top: 50,
            left: 60,
            opacity: titleAppear,
            transform: `translateX(${interpolate(titleAppear, [0, 1], [-60, 0])}px)`,
          }}
        >
          <div
            style={{
              background: accentColor,
              padding: "8px 22px",
              borderRadius: 10,
              fontSize: 16,
              fontWeight: 800,
              color: "#fff",
              fontFamily,
              letterSpacing: 2,
              textTransform: "uppercase",
              boxShadow: `0 4px 16px ${accentColor}50`,
            }}
          >
            🎬 REVIEW & REACTION
          </div>
        </div>

        {/* Main content layout */}
        <div
          style={{
            position: "absolute",
            top: "15%",
            left: "50%",
            transform: "translate(-50%, 0)",
            width: "85%",
          }}
        >
          {/* Title */}
          <h2
            style={{
              color: "#ffffff",
              fontSize: 48,
              fontFamily,
              fontWeight: 800,
              margin: "0 0 24px 0",
              opacity: titleAppear,
              transform: `translateY(${interpolate(titleAppear, [0, 1], [30, 0])}px)`,
              textShadow: "0 2px 16px rgba(0,0,0,0.8)",
              lineHeight: 1.3,
              textAlign: "center",
            }}
          >
            {scene.title}
          </h2>

          {/* Reaction bar */}
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              marginBottom: 30,
            }}
          >
            <ReactionBar
              reactions={reactions}
              accentColor={accentColor}
              fontFamily={fontFamily}
              delay={20}
            />
          </div>

          {/* Rating bars (if provided) */}
          {scene.ratings && scene.ratings.length > 0 && (
            <div
              style={{
                background: "rgba(0,0,0,0.5)",
                backdropFilter: "blur(8px)",
                borderRadius: 16,
                padding: "20px 28px",
                opacity: contentAppear,
                maxWidth: 600,
                margin: "0 auto",
              }}
            >
              {scene.ratings.map((rating, i) => (
                <RatingBar
                  key={i}
                  label={rating.label}
                  value={rating.value}
                  maxValue={rating.maxValue}
                  accentColor={accentColor}
                  fontFamily={fontFamily}
                  delay={25 + i * 8}
                  barColor={rating.color}
                />
              ))}
            </div>
          )}

          {/* Quote from community */}
          {scene.quote && (
            <div
              style={{
                marginTop: 24,
                opacity: contentAppear,
                transform: `translateY(${interpolate(contentAppear, [0, 1], [20, 0])}px)`,
              }}
            >
              <div
                style={{
                  background: "rgba(0,0,0,0.6)",
                  backdropFilter: "blur(10px)",
                  borderRadius: 16,
                  padding: "20px 28px",
                  borderLeft: `4px solid ${accentColor}`,
                  maxWidth: 700,
                  margin: "0 auto",
                }}
              >
                <div
                  style={{
                    fontSize: 12,
                    fontWeight: 700,
                    color: accentColor,
                    fontFamily,
                    letterSpacing: 2,
                    marginBottom: 10,
                  }}
                >
                  💬 Ý KIẾN CỘNG ĐỒNG
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
                  &ldquo;{scene.quote}&rdquo;
                </p>
                {scene.quoteAuthor && (
                  <p
                    style={{
                      color: accentColor,
                      fontSize: 16,
                      fontFamily,
                      fontWeight: 700,
                      margin: "10px 0 0",
                    }}
                  >
                    — @{scene.quoteAuthor}
                  </p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Audio */}
        {scene.audioFile && (
          <Audio src={staticFile(scene.audioFile)} />
        )}
      </Transition>
    </AbsoluteFill>
  );
};
