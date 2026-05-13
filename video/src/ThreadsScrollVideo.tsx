import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
} from "remotion";
import { PlaidBackground } from "./components/PlaidBackground";
import { ThreadsCard } from "./components/ThreadsCard";
import type { ThreadsScrollProps } from "./types";

export const ThreadsScrollVideo: React.FC<ThreadsScrollProps> = ({
  posts,
  fps,
}) => {
  const effectiveFps = fps || 30;

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

      {/* Render each post as a Sequence */}
      {posts.map((post, index) => {
        const postDurationFrames = Math.round(post.durationInSeconds * effectiveFps);
        const from = currentFrame;
        currentFrame += postDurationFrames;

        return (
          <Sequence
            key={index}
            from={from}
            durationInFrames={postDurationFrames}
          >
            {/* Center the card on screen */}
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
              <Audio src={staticFile(post.audioFile)} />
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
