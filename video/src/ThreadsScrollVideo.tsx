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
import { PlaidBackground } from "./components/PlaidBackground";
import { ThreadsCard } from "./components/ThreadsCard";
import type { ThreadsScrollProps } from "./types";

const MemeReveal: React.FC<{ src: string }> = ({ src }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 14, stiffness: 100 } });
  const opacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "rgba(0, 0, 0, 0.7)",
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          opacity,
          borderRadius: 20,
          overflow: "hidden",
          boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
          maxWidth: "75%",
          maxHeight: "75%",
        }}
      >
        <Img
          src={staticFile(src)}
          style={{ width: "100%", height: "100%", objectFit: "contain" }}
        />
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 60,
          display: "flex",
          alignItems: "center",
          gap: 10,
          opacity: interpolate(frame, [10, 20], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        <span style={{ fontSize: 28, color: "#fff", fontFamily: "Inter, system-ui, sans-serif", fontWeight: 600 }}>
          😂 Meme phản ứng
        </span>
      </div>
    </AbsoluteFill>
  );
};

export const ThreadsScrollVideo: React.FC<ThreadsScrollProps> = ({
  posts,
  fps,
  backgroundMusic,
  backgroundMusicVolume,
}) => {
  const effectiveFps = fps || 30;
  const bgMusicVol = backgroundMusicVolume ?? 0.15;

  let currentFrame = 0;

  return (
    <AbsoluteFill>
      {/* Plaid / checkered pastel background */}
      <PlaidBackground
        color1="#f0f4f8"
        color2="#d4e4f1"
        color3="#bdd4ea"
        cellSize={80}
      />

      {/* Background music — loops for entire video, lower volume */}
      {backgroundMusic && (
        <Audio
          src={staticFile(backgroundMusic)}
          volume={bgMusicVol}
          loop
        />
      )}

      {/* Render each post as a Sequence, with optional meme reveal after */}
      {posts.map((post, index) => {
        const totalFrames = Math.round(post.durationInSeconds * effectiveFps);
        const memeSec = post.memeImage ? (post.memeDuration ?? 3) : 0;
        const memeFrames = Math.round(memeSec * effectiveFps);
        const cardFrames = totalFrames - memeFrames;
        const from = currentFrame;
        currentFrame += totalFrames;

        return (
          <React.Fragment key={index}>
            {/* Comment card */}
            <Sequence from={from} durationInFrames={cardFrames}>
              <AbsoluteFill
                style={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  padding: "40px 60px",
                }}
              >
                <ThreadsCard post={post} delay={0} />
              </AbsoluteFill>

              {/* Audio narration */}
              {post.audioFile && (
                <Audio src={staticFile(post.audioFile)} volume={0.9} />
              )}
            </Sequence>

            {/* Meme reveal after narration */}
            {post.memeImage && memeFrames > 0 && (
              <Sequence from={from + cardFrames} durationInFrames={memeFrames}>
                <PlaidBackground
                  color1="#f0f4f8"
                  color2="#d4e4f1"
                  color3="#bdd4ea"
                  cellSize={80}
                />
                <MemeReveal src={post.memeImage} />
              </Sequence>
            )}
          </React.Fragment>
        );
      })}

      {/* Channel watermark bottom-right */}
      <AbsoluteFill
        style={{
          display: "flex",
          justifyContent: "flex-end",
          alignItems: "flex-end",
          padding: "0 30px 20px 0",
          pointerEvents: "none",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            opacity: 0.6,
          }}
        >
          <span
            style={{
              fontSize: 18,
              color: "#333",
              fontFamily: "Inter, system-ui, sans-serif",
              fontWeight: 600,
            }}
          >
            🧵 Threads Hot
          </span>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
