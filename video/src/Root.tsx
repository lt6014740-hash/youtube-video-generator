import React from "react";
import { Composition } from "remotion";
import { YouTubeVideo } from "./YouTubeVideo";
import type { VideoProps } from "./types";

const DEFAULT_PROPS: VideoProps = {
  title: "Welcome to AI Video Generator",
  scenes: [
    {
      sceneNumber: 1,
      title: "Introduction",
      narration:
        "Welcome to our AI-powered video generator. This tool creates professional YouTube videos automatically.",
      visualDescription: "Modern tech introduction with animated graphics",
      durationInSeconds: 10,
      audioFile: "",
    },
    {
      sceneNumber: 2,
      title: "How It Works",
      narration:
        "Simply provide a topic, choose your language, and let AI handle the rest. From script to final video in minutes.",
      visualDescription: "Step-by-step workflow visualization",
      durationInSeconds: 12,
      audioFile: "",
    },
    {
      sceneNumber: 3,
      title: "Multi-Language Support",
      narration:
        "Our tool supports Vietnamese, English, Chinese, Japanese, Korean and many more languages for global reach.",
      visualDescription: "World map with language highlights",
      durationInSeconds: 10,
      audioFile: "",
    },
  ],
  subtitles: [
    {
      text: "Welcome to our AI-powered video generator.",
      startFrame: 120,
      endFrame: 240,
    },
    {
      text: "This tool creates professional YouTube videos.",
      startFrame: 240,
      endFrame: 420,
    },
    {
      text: "Simply provide a topic and choose your language.",
      startFrame: 420,
      endFrame: 600,
    },
    {
      text: "From script to final video in minutes.",
      startFrame: 600,
      endFrame: 780,
    },
    {
      text: "Supporting Vietnamese, English, Chinese and more.",
      startFrame: 780,
      endFrame: 960,
    },
  ],
  totalDurationInSeconds: 41,
  backgroundColor: "#1a1a2e",
  subtitleColor: "#ffffff",
  accentColor: "#e94560",
  fontFamily: "Inter, system-ui, sans-serif",
  language: "en",
  fps: 30,
  width: 1920,
  height: 1080,
};

export const RemotionRoot: React.FC = () => {
  const totalFrames = Math.round(
    (DEFAULT_PROPS.totalDurationInSeconds + 4 + 5) * DEFAULT_PROPS.fps
  );

  return (
    <>
      <Composition
        id="YouTubeVideo"
        component={YouTubeVideo as React.FC}
        durationInFrames={totalFrames}
        fps={DEFAULT_PROPS.fps}
        width={DEFAULT_PROPS.width}
        height={DEFAULT_PROPS.height}
        defaultProps={DEFAULT_PROPS as unknown as Record<string, unknown>}
      />
    </>
  );
};
