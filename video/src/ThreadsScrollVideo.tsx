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

const MemeBelow: React.FC<{ src: string }> = ({ src }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 14, stiffness: 100 } });
  const opacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });

  return (
    <div
      style={{
        marginTop: 16,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          opacity,
          borderRadius: 16,
          overflow: "hidden",
          boxShadow: "0 8px 30px rgba(0,0,0,0.4)",
          maxWidth: 500,
          maxHeight: 350,
          background: "#1a1a1a",
        }}
      >
        <Img
          src={staticFile(src)}
          style={{ width: "100%", height: "100%", objectFit: "contain" }}
        />
      </div>
    </div>
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

      {/* Render each post as a Sequence — meme appears below card after narration */}
      {posts.map((post, index) => {
        const totalFrames = Math.round(post.durationInSeconds * effectiveFps);
        const memeSec = post.memeImage ? (post.memeDuration ?? 3) : 0;
        const memeFrames = Math.round(memeSec * effectiveFps);
        const cardFrames = totalFrames - memeFrames;
        const from = currentFrame;
        currentFrame += totalFrames;

        return (
          <Sequence key={index} from={from} durationInFrames={totalFrames}>
            <AbsoluteFill
              style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                padding: "40px 60px",
              }}
            >
              <ThreadsCard post={post} delay={0} />

              {/* Meme appears below card after narration finishes */}
              {post.memeImage && memeFrames > 0 && (
                <Sequence from={cardFrames} durationInFrames={memeFrames}>
                  <MemeBelow src={post.memeImage} />
                </Sequence>
              )}
            </AbsoluteFill>

            {/* Audio narration */}
            {post.audioFile && (
              <Audio src={staticFile(post.audioFile)} volume={0.9} />
            )}
          </Sequence>
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
