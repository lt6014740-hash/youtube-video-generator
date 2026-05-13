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
import type { SceneData } from "../types";
import { Background } from "./Background";
import { Highlight } from "./Highlight";
import { LowerThird } from "./LowerThird";
import { Particles } from "./Particles";
import { ProgressBar } from "./ProgressBar";
import type { TransitionType } from "./Transition";
import { Transition } from "./Transition";

interface SceneProps {
  scene: SceneData;
  sceneIndex: number;
  totalScenes: number;
  backgroundColor: string;
  accentColor: string;
  fontFamily: string;
  subtitleColor: string;
}

const TRANSITION_TYPES: TransitionType[] = [
  "slideLeft", "zoom", "wipe", "fade", "slideUp", "glitch",
];

const SCENE_ICONS = ["🎬", "📚", "💡", "🌟", "🎯", "🔥", "✨", "🚀", "🎨", "🏆"];

export const Scene: React.FC<SceneProps> = ({
  scene,
  sceneIndex,
  totalScenes,
  backgroundColor,
  accentColor,
  fontFamily,
  subtitleColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const hasImage = !!scene.imageFile;
  const hasQuote = !!scene.quote;
  const transitionType = TRANSITION_TYPES[sceneIndex % TRANSITION_TYPES.length];
  const icon = SCENE_ICONS[sceneIndex % SCENE_ICONS.length];

  const titleAppear = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 80 },
    delay: 8,
  });

  const sceneNumberAppear = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 100 },
  });

  const contentAppear = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 60 },
    delay: 18,
  });

  const quoteAppear = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 50 },
    delay: 30,
  });

  const iconScale = interpolate(
    frame,
    [0, 20, 40, 60],
    [0, 1.2, 0.9, 1],
    { extrapolateRight: "clamp" }
  );

  const iconRotate = interpolate(
    frame,
    [0, 20, 40],
    [-15, 10, 0],
    { extrapolateRight: "clamp" }
  );

  const imageZoom = interpolate(
    frame,
    [0, fps * scene.durationInSeconds],
    [1.0, 1.12],
    { extrapolateRight: "clamp" }
  );

  const imagePanX = interpolate(
    frame,
    [0, fps * scene.durationInSeconds],
    [sceneIndex % 2 === 0 ? -20 : 20, sceneIndex % 2 === 0 ? 20 : -20],
    { extrapolateRight: "clamp" }
  );

  const titleUnderlineWidth = interpolate(
    frame,
    [15, 45],
    [0, 100],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const badgePulse = interpolate(
    frame % 60,
    [0, 30, 60],
    [1, 1.05, 1],
  );

  return (
    <AbsoluteFill>
      <Transition type={transitionType} durationInFrames={12}>
        {/* Background: image with Ken Burns or gradient */}
        {hasImage ? (
          <AbsoluteFill style={{ overflow: "hidden" }}>
            <Img
              src={staticFile(scene.imageFile!)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                transform: `scale(${imageZoom}) translateX(${imagePanX}px)`,
              }}
            />
            {/* Cinematic dark overlay */}
            <AbsoluteFill
              style={{
                background:
                  "linear-gradient(180deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0.2) 30%, rgba(0,0,0,0.25) 60%, rgba(0,0,0,0.8) 100%)",
              }}
            />
            {/* Vignette effect */}
            <AbsoluteFill
              style={{
                background: "radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.4) 100%)",
              }}
            />
          </AbsoluteFill>
        ) : (
          <Background
            backgroundColor={backgroundColor}
            accentColor={accentColor}
            sceneIndex={sceneIndex}
          />
        )}

        {/* Floating particles */}
        <Particles accentColor={accentColor} count={12} />

        {/* Progress bar at top */}
        <ProgressBar
          accentColor={accentColor}
          totalScenes={totalScenes}
          currentSceneIndex={sceneIndex}
        />

        {/* Scene number badge with pulse */}
        <div
          style={{
            position: "absolute",
            top: 50,
            left: 60,
            display: "flex",
            alignItems: "center",
            gap: 12,
            opacity: sceneNumberAppear,
            transform: `translateX(${interpolate(sceneNumberAppear, [0, 1], [-80, 0])}px) scale(${badgePulse})`,
          }}
        >
          <div
            style={{
              background: `linear-gradient(135deg, ${accentColor}, ${accentColor}cc)`,
              borderRadius: 14,
              padding: "10px 22px",
              fontSize: 20,
              fontWeight: 800,
              color: "#fff",
              fontFamily,
              letterSpacing: 1.5,
              boxShadow: `0 4px 20px ${accentColor}60`,
              textTransform: "uppercase",
            }}
          >
            {icon} Scene {scene.sceneNumber}
          </div>
        </div>

        {/* Threads logo badge (top right) */}
        <div
          style={{
            position: "absolute",
            top: 50,
            right: 60,
            opacity: sceneNumberAppear,
            transform: `translateX(${interpolate(sceneNumberAppear, [0, 1], [80, 0])}px)`,
          }}
        >
          <div
            style={{
              background: "rgba(0,0,0,0.6)",
              backdropFilter: "blur(8px)",
              borderRadius: 12,
              padding: "8px 18px",
              fontSize: 16,
              fontWeight: 600,
              color: "rgba(255,255,255,0.7)",
              fontFamily,
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            🧵 Threads • 12/5/2026
          </div>
        </div>

        {/* Main content area */}
        <div
          style={{
            position: "absolute",
            top: hasQuote ? "25%" : "45%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: "82%",
            textAlign: "center",
          }}
        >
          {/* Animated icon */}
          <div
            style={{
              fontSize: 80,
              marginBottom: 24,
              transform: `scale(${iconScale}) rotate(${iconRotate}deg)`,
              opacity: sceneNumberAppear,
              filter: `drop-shadow(0 4px 12px ${accentColor}40)`,
            }}
          >
            {icon}
          </div>

          {/* Scene title with highlight effect */}
          <Highlight
            text={scene.title}
            accentColor={accentColor}
            fontFamily={fontFamily}
            delay={8}
          />

          {/* Animated underline */}
          <div
            style={{
              width: `${titleUnderlineWidth}%`,
              maxWidth: 500,
              height: 3,
              background: `linear-gradient(90deg, transparent, ${accentColor}, transparent)`,
              margin: "20px auto 0",
              borderRadius: 2,
              opacity: contentAppear,
            }}
          />

          {/* Visual description (when no image) */}
          {!hasImage && (
            <p
              style={{
                color: `${subtitleColor}80`,
                fontSize: 24,
                fontFamily,
                fontWeight: 400,
                fontStyle: "italic",
                margin: "16px 0 0",
                opacity: contentAppear,
                transform: `translateY(${interpolate(contentAppear, [0, 1], [20, 0])}px)`,
              }}
            >
              {scene.visualDescription}
            </p>
          )}
        </div>

        {/* Quote box with animated border */}
        {hasQuote && (
          <div
            style={{
              position: "absolute",
              bottom: 240,
              left: "50%",
              transform: "translate(-50%, 0)",
              width: "78%",
              opacity: quoteAppear,
              filter: `drop-shadow(0 8px 32px rgba(0,0,0,0.5))`,
            }}
          >
            <div
              style={{
                background: "rgba(0,0,0,0.7)",
                backdropFilter: "blur(12px)",
                borderRadius: 20,
                padding: "24px 32px",
                borderLeft: `5px solid ${accentColor}`,
                borderBottom: `1px solid rgba(255,255,255,0.08)`,
                position: "relative",
                overflow: "hidden",
              }}
            >
              {/* Gradient accent on top */}
              <div
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  right: 0,
                  height: 2,
                  background: `linear-gradient(90deg, ${accentColor}, transparent)`,
                }}
              />

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  marginBottom: 12,
                }}
              >
                <span style={{ fontSize: 14, color: accentColor, fontWeight: 700 }}>
                  📌 TRÍCH DẪN TỪ THREADS
                </span>
                {scene.quoteAuthor && (
                  <span
                    style={{
                      fontSize: 14,
                      color: "rgba(255,255,255,0.4)",
                      fontFamily,
                    }}
                  >
                    •
                  </span>
                )}
                {scene.quoteAuthor && (
                  <span
                    style={{
                      fontSize: 14,
                      color: accentColor,
                      fontWeight: 600,
                      fontFamily,
                    }}
                  >
                    @{scene.quoteAuthor}
                  </span>
                )}
              </div>

              <p
                style={{
                  color: "#ffffff",
                  fontSize: 24,
                  fontFamily,
                  fontWeight: 500,
                  fontStyle: "italic",
                  margin: 0,
                  lineHeight: 1.5,
                  textShadow: "0 1px 4px rgba(0,0,0,0.5)",
                }}
              >
                &ldquo;{scene.quote}&rdquo;
              </p>
            </div>
          </div>
        )}

        {/* Lower-third news bar */}
        {scene.quoteAuthor && (
          <LowerThird
            source={`@${scene.quoteAuthor}`}
            category="TRENDING"
            accentColor={accentColor}
            fontFamily={fontFamily}
          />
        )}

        {/* Audio */}
        {scene.audioFile && (
          <Audio src={staticFile(scene.audioFile)} />
        )}
      </Transition>
    </AbsoluteFill>
  );
};
