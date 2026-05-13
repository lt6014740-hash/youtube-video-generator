import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { HistoricalProps, HistoricalSceneData } from "./types";

const SCENE_COLORS = [
  "#1a3a5c",
  "#4a2c2a",
  "#2d4a3e",
  "#3d2d5c",
  "#5c3d1a",
  "#1a4a4a",
  "#4a1a3d",
  "#2a3d5c",
];

const HeaderBar: React.FC<{ channelName?: string }> = ({ channelName }) => (
  <div
    style={{
      position: "absolute",
      top: 0,
      left: 0,
      right: 0,
      height: 100,
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 30px",
      background: "rgba(255,255,255,0.95)",
      zIndex: 100,
    }}
  >
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <div
        style={{
          width: 50,
          height: 50,
          borderRadius: "50%",
          background: "linear-gradient(135deg, #4a90d9, #357abd)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 28,
        }}
      >
        📚
      </div>
      <span
        style={{
          fontSize: 22,
          fontWeight: 800,
          color: "#1a1a2e",
          fontFamily: "'Roboto', sans-serif",
        }}
      >
        {channelName || "Kiến Thức Hay"}
      </span>
    </div>
    <div
      style={{
        fontSize: 16,
        fontWeight: 700,
        color: "#fff",
        background: "#e94560",
        padding: "8px 16px",
        borderRadius: 20,
      }}
    >
      SUBSCRIBE
    </div>
  </div>
);

const WordByWordCaption: React.FC<{
  text: string;
  frame: number;
  fps: number;
  durationFrames: number;
}> = ({ text, frame, durationFrames }) => {
  const words = text.split(" ");
  const framesPerWord = durationFrames / words.length;
  const currentWordIdx = Math.min(
    Math.floor(frame / framesPerWord),
    words.length - 1
  );

  const WORDS_PER_GROUP = 4;
  const groupStart =
    Math.floor(currentWordIdx / WORDS_PER_GROUP) * WORDS_PER_GROUP;
  const groupEnd = Math.min(groupStart + WORDS_PER_GROUP, words.length);
  const visibleWords = words.slice(groupStart, groupEnd);

  return (
    <div
      style={{
        position: "absolute",
        top: 108,
        left: 16,
        right: 16,
        height: 80,
        textAlign: "center",
        zIndex: 90,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexWrap: "wrap",
        gap: 8,
      }}
    >
      {visibleWords.map((word, idx) => {
        const globalIdx = groupStart + idx;
        const isActive = globalIdx === currentWordIdx;
        const isPast = globalIdx < currentWordIdx;
        return (
          <span
            key={`${groupStart}-${idx}`}
            style={{
              fontSize: 34,
              fontWeight: 900,
              fontFamily: "'Roboto', sans-serif",
              color: isActive
                ? "#e94560"
                : isPast
                  ? "#1a1a2e"
                  : "#999",
              textTransform: "uppercase",
              letterSpacing: 1,
              textShadow: isActive
                ? "0 2px 12px rgba(233,69,96,0.4)"
                : "none",
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};

const SceneContent: React.FC<{
  scene: HistoricalSceneData;
  sceneIndex: number;
}> = ({ scene, sceneIndex }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const durationFrames = scene.durationInSeconds * fps;
  const bgColor = scene.bgColor || SCENE_COLORS[sceneIndex % SCENE_COLORS.length];

  const enterProgress = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 80, mass: 0.8 },
  });

  const contentY = interpolate(enterProgress, [0, 1], [60, 0]);
  const contentOpacity = interpolate(enterProgress, [0, 1], [0, 1]);

  const iconScale = spring({
    frame: frame - 5,
    fps,
    config: { damping: 10, stiffness: 100, mass: 0.5 },
  });

  const pulseScale = interpolate(
    Math.sin(frame * 0.05),
    [-1, 1],
    [1.0, 1.03]
  );

  return (
    <AbsoluteFill>
      {/* White background */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "#ffffff",
        }}
      />

      {/* Header */}
      <HeaderBar />

      {/* Word-by-word caption */}
      <WordByWordCaption
        text={scene.narration}
        frame={frame}
        fps={fps}
        durationFrames={durationFrames}
      />

      {/* Main content area */}
      <div
        style={{
          position: "absolute",
          top: 200,
          left: 16,
          right: 16,
          bottom: 16,
          borderRadius: 24,
          overflow: "hidden",
          background: `linear-gradient(165deg, ${bgColor}, ${bgColor}dd)`,
          boxShadow: "0 8px 32px rgba(0,0,0,0.15)",
          transform: `translateY(${contentY}px) scale(${pulseScale})`,
          opacity: contentOpacity,
        }}
      >
        {/* Scene image if provided */}
        {scene.imageFile && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              opacity: 0.25,
            }}
          >
            <Img
              src={staticFile(scene.imageFile)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
              }}
            />
          </div>
        )}

        {/* Decorative grid overlay */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage:
              "linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)",
            backgroundSize: "40px 40px",
          }}
        />

        {/* Year badge */}
        {scene.year && (
          <div
            style={{
              position: "absolute",
              top: 20,
              right: 20,
              background: "rgba(233,69,96,0.9)",
              padding: "10px 22px",
              borderRadius: 12,
              fontSize: 24,
              fontWeight: 900,
              color: "#fff",
              fontFamily: "'Roboto', sans-serif",
              boxShadow: "0 4px 12px rgba(233,69,96,0.4)",
              transform: `scale(${iconScale})`,
            }}
          >
            {scene.year}
          </div>
        )}

        {/* Scene number badge */}
        <div
          style={{
            position: "absolute",
            top: 20,
            left: 20,
            width: 44,
            height: 44,
            borderRadius: "50%",
            background: "rgba(255,255,255,0.15)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 20,
            fontWeight: 800,
            color: "#fff",
            border: "2px solid rgba(255,255,255,0.3)",
          }}
        >
          {scene.sceneNumber}
        </div>

        {/* Center icon */}
        {scene.icon && (
          <div
            style={{
              position: "absolute",
              top: "15%",
              left: "50%",
              transform: `translateX(-50%) scale(${iconScale})`,
              fontSize: 100,
              filter: "drop-shadow(0 8px 16px rgba(0,0,0,0.3))",
            }}
          >
            {scene.icon}
          </div>
        )}

        {/* Scene title */}
        <div
          style={{
            position: "absolute",
            top: scene.icon ? "42%" : "25%",
            left: 30,
            right: 30,
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: 36,
              fontWeight: 900,
              color: "#fff",
              fontFamily: "'Roboto', sans-serif",
              textTransform: "uppercase",
              letterSpacing: 2,
              textShadow: "0 3px 10px rgba(0,0,0,0.5)",
              lineHeight: 1.3,
            }}
          >
            {scene.title}
          </div>
        </div>

        {/* Facts list */}
        {scene.facts && scene.facts.length > 0 && (
          <div
            style={{
              position: "absolute",
              top: scene.icon ? "58%" : "45%",
              left: 30,
              right: 30,
              display: "flex",
              flexDirection: "column",
              gap: 14,
            }}
          >
            {scene.facts.map((fact, i) => {
              const factDelay = (durationFrames * 0.2) + i * (durationFrames * 0.12);
              const factVisible = frame >= factDelay;
              const factProgress = spring({
                frame: frame - factDelay,
                fps,
                config: { damping: 14, stiffness: 100, mass: 0.6 },
              });
              const factX = interpolate(factProgress, [0, 1], [40, 0]);
              return (
                <div
                  key={i}
                  style={{
                    background: "rgba(255,255,255,0.12)",
                    borderRadius: 14,
                    padding: "14px 20px",
                    display: "flex",
                    alignItems: "center",
                    gap: 14,
                    opacity: factVisible ? factProgress : 0,
                    transform: `translateX(${factX}px)`,
                    backdropFilter: "blur(8px)",
                    border: "1px solid rgba(255,255,255,0.15)",
                  }}
                >
                  <div
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      background: "#e94560",
                      flexShrink: 0,
                    }}
                  />
                  <span
                    style={{
                      fontSize: 22,
                      color: "#fff",
                      fontFamily: "'Roboto', sans-serif",
                      fontWeight: 500,
                      lineHeight: 1.4,
                    }}
                  >
                    {fact}
                  </span>
                </div>
              );
            })}
          </div>
        )}

        {/* Progress indicator */}
        <div
          style={{
            position: "absolute",
            bottom: 20,
            left: 30,
            right: 30,
            height: 4,
            background: "rgba(255,255,255,0.15)",
            borderRadius: 2,
          }}
        >
          <div
            style={{
              height: "100%",
              borderRadius: 2,
              background: "linear-gradient(90deg, #e94560, #ff6b81)",
              width: `${(frame / durationFrames) * 100}%`,
            }}
          />
        </div>
      </div>

      {/* Audio */}
      {scene.audioFile && (
        <Audio src={staticFile(scene.audioFile)} volume={0.9} />
      )}
    </AbsoluteFill>
  );
};

export const HistoricalVideo: React.FC<HistoricalProps> = ({
  scenes,
  fps: propFps,
  backgroundMusic,
  backgroundMusicVolume,
  channelName,
}) => {
  const effectiveFps = propFps || 30;
  const bgMusicVol = backgroundMusicVolume ?? 0.15;

  let currentFrame = 0;

  return (
    <AbsoluteFill style={{ background: "#ffffff" }}>
      {/* Background music */}
      {backgroundMusic && (
        <Audio
          src={staticFile(backgroundMusic)}
          volume={bgMusicVol}
          loop
        />
      )}

      {/* Scenes */}
      {scenes.map((scene, index) => {
        const sceneDurationFrames = Math.round(
          scene.durationInSeconds * effectiveFps
        );
        const startFrame = currentFrame;
        currentFrame += sceneDurationFrames;

        return (
          <Sequence
            key={index}
            from={startFrame}
            durationInFrames={sceneDurationFrames}
          >
            <SceneContent scene={scene} sceneIndex={index} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
