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

interface SceneProps {
  scene: SceneData;
  sceneIndex: number;
  backgroundColor: string;
  accentColor: string;
  fontFamily: string;
  subtitleColor: string;
}

export const Scene: React.FC<SceneProps> = ({
  scene,
  sceneIndex,
  backgroundColor,
  accentColor,
  fontFamily,
  subtitleColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const hasImage = !!scene.imageFile;
  const hasQuote = !!scene.quote;

  const titleAppear = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 80 },
    delay: 5,
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
    delay: 15,
  });

  const quoteAppear = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 50 },
    delay: 25,
  });

  const iconScale = interpolate(
    frame,
    [0, 30, 60, 90],
    [0.8, 1.1, 0.95, 1],
    { extrapolateRight: "clamp" }
  );

  const imageZoom = interpolate(
    frame,
    [0, fps * scene.durationInSeconds],
    [1.0, 1.08],
    { extrapolateRight: "clamp" }
  );

  const SCENE_ICONS = ["🎬", "📚", "💡", "🌟", "🎯", "🔥", "✨", "🚀", "🎨", "🏆"];
  const icon = SCENE_ICONS[sceneIndex % SCENE_ICONS.length];

  return (
    <AbsoluteFill>
      {/* Background: image or gradient */}
      {hasImage ? (
        <AbsoluteFill>
          <Img
            src={staticFile(scene.imageFile!)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${imageZoom})`,
            }}
          />
          {/* Dark overlay for readability */}
          <AbsoluteFill
            style={{
              background:
                "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.3) 40%, rgba(0,0,0,0.7) 100%)",
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

      {/* Scene number badge */}
      <div
        style={{
          position: "absolute",
          top: 60,
          left: 80,
          display: "flex",
          alignItems: "center",
          gap: 16,
          opacity: sceneNumberAppear,
          transform: `translateX(${interpolate(sceneNumberAppear, [0, 1], [-50, 0])}px)`,
        }}
      >
        <div
          style={{
            background: accentColor,
            borderRadius: 12,
            padding: "8px 20px",
            fontSize: 22,
            fontWeight: 700,
            color: "#fff",
            fontFamily,
            letterSpacing: 1,
          }}
        >
          SCENE {scene.sceneNumber}
        </div>
      </div>

      {/* Main content area */}
      <div
        style={{
          position: "absolute",
          top: hasQuote ? "30%" : "50%",
          left: "50%",
          transform: `translate(-50%, -50%)`,
          width: "80%",
          textAlign: "center",
        }}
      >
        {/* Icon */}
        <div
          style={{
            fontSize: 80,
            marginBottom: 30,
            transform: `scale(${iconScale})`,
            opacity: sceneNumberAppear,
          }}
        >
          {icon}
        </div>

        {/* Scene title */}
        <h2
          style={{
            color: subtitleColor,
            fontSize: hasImage ? 52 : 56,
            fontFamily,
            fontWeight: 800,
            margin: "0 0 24px 0",
            opacity: titleAppear,
            transform: `translateY(${interpolate(titleAppear, [0, 1], [30, 0])}px)`,
            textShadow: hasImage
              ? "0 2px 12px rgba(0,0,0,0.8), 0 4px 24px rgba(0,0,0,0.5)"
              : "0 4px 8px rgba(0,0,0,0.3)",
            lineHeight: 1.3,
          }}
        >
          {scene.title}
        </h2>

        {/* Visual description hint (only when no image) */}
        {!hasImage && (
          <p
            style={{
              color: `${subtitleColor}80`,
              fontSize: 24,
              fontFamily,
              fontWeight: 400,
              fontStyle: "italic",
              margin: 0,
              opacity: contentAppear,
              transform: `translateY(${interpolate(contentAppear, [0, 1], [20, 0])}px)`,
            }}
          >
            {scene.visualDescription}
          </p>
        )}
      </div>

      {/* Quote box */}
      {hasQuote && (
        <div
          style={{
            position: "absolute",
            bottom: 160,
            left: "50%",
            transform: `translate(-50%, 0)`,
            width: "75%",
            opacity: quoteAppear,
          }}
        >
          <div
            style={{
              background: "rgba(0,0,0,0.65)",
              backdropFilter: "blur(8px)",
              borderRadius: 20,
              padding: "28px 36px",
              borderLeft: `5px solid ${accentColor}`,
            }}
          >
            <div
              style={{
                color: "#e0e0e0",
                fontSize: 13,
                fontFamily,
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: 2,
                marginBottom: 10,
              }}
            >
              📌 Trích dẫn từ Threads
            </div>
            <p
              style={{
                color: "#ffffff",
                fontSize: 26,
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
            {scene.quoteAuthor && (
              <p
                style={{
                  color: accentColor,
                  fontSize: 20,
                  fontFamily,
                  fontWeight: 700,
                  margin: "12px 0 0 0",
                }}
              >
                — @{scene.quoteAuthor}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Audio for this scene */}
      {scene.audioFile && (
        <Audio src={staticFile(scene.audioFile)} />
      )}
    </AbsoluteFill>
  );
};
