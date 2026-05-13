import React from "react";
import { Composition } from "remotion";
import { ReactionVideo } from "./ReactionVideo";
import { TrueCrimeVideo } from "./TrueCrimeVideo";
import { YouTubeVideo } from "./YouTubeVideo";
import type { ReactionProps, TrueCrimeProps, VideoProps } from "./types";

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
    { text: "Welcome to our AI-powered video generator.", startFrame: 120, endFrame: 240 },
    { text: "This tool creates professional YouTube videos.", startFrame: 240, endFrame: 420 },
    { text: "Simply provide a topic and choose your language.", startFrame: 420, endFrame: 600 },
    { text: "From script to final video in minutes.", startFrame: 600, endFrame: 780 },
    { text: "Supporting Vietnamese, English, Chinese and more.", startFrame: 780, endFrame: 960 },
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

const TRUE_CRIME_DEFAULT: TrueCrimeProps = {
  title: "Vụ án mẫu — True Crime",
  scenes: [
    {
      sceneNumber: 1,
      title: "Bối cảnh vụ án",
      narration: "Đây là bối cảnh của vụ án...",
      durationInSeconds: 10,
      audioFile: "",
      phase: "BỐI CẢNH",
      evidence: "Lời khai nhân chứng...",
      evidenceLabel: "LỜI KHAI",
    },
    {
      sceneNumber: 2,
      title: "Diễn biến chính",
      narration: "Vụ việc diễn ra như sau...",
      durationInSeconds: 12,
      audioFile: "",
      phase: "DIỄN BIẾN",
    },
  ],
  subtitles: [],
  timelineEvents: [
    { time: "2024", label: "Bối cảnh", icon: "📍" },
    { time: "T3/2025", label: "Diễn biến", icon: "⚡" },
  ],
  totalDurationInSeconds: 32,
  backgroundColor: "#0a0a0a",
  subtitleColor: "#ffffff",
  accentColor: "#ef4444",
  fontFamily: "Inter, system-ui, sans-serif",
  language: "vi",
  fps: 30,
  width: 1920,
  height: 1080,
};

const REACTION_DEFAULT: ReactionProps = {
  title: "Review mẫu — Reaction",
  scenes: [
    {
      sceneNumber: 1,
      title: "Tổng quan",
      narration: "Hôm nay chúng ta review...",
      durationInSeconds: 10,
      audioFile: "",
      reactions: [
        { emoji: "😱", label: "Sốc", count: 1200, color: "#ef4444" },
        { emoji: "🔥", label: "Hot", count: 3400, color: "#f59e0b" },
        { emoji: "👏", label: "Hay", count: 2100, color: "#10b981" },
        { emoji: "😂", label: "Hài", count: 800, color: "#3b82f6" },
      ],
    },
  ],
  subtitles: [],
  totalDurationInSeconds: 19,
  backgroundColor: "#0a0a1e",
  subtitleColor: "#ffffff",
  accentColor: "#8b5cf6",
  fontFamily: "Inter, system-ui, sans-serif",
  language: "vi",
  fps: 30,
  width: 1920,
  height: 1080,
};

export const RemotionRoot: React.FC = () => {
  const ytFrames = Math.round(
    (DEFAULT_PROPS.totalDurationInSeconds + 4 + 5) * DEFAULT_PROPS.fps
  );
  const tcFrames = Math.round(
    (TRUE_CRIME_DEFAULT.totalDurationInSeconds + 5 + 5) * TRUE_CRIME_DEFAULT.fps
  );
  const rxFrames = Math.round(
    (REACTION_DEFAULT.totalDurationInSeconds + 4 + 5) * REACTION_DEFAULT.fps
  );

  return (
    <>
      <Composition
        id="YouTubeVideo"
        component={YouTubeVideo as React.FC}
        durationInFrames={ytFrames}
        fps={DEFAULT_PROPS.fps}
        width={DEFAULT_PROPS.width}
        height={DEFAULT_PROPS.height}
        defaultProps={DEFAULT_PROPS as unknown as Record<string, unknown>}
      />
      <Composition
        id="TrueCrimeVideo"
        component={TrueCrimeVideo as React.FC}
        durationInFrames={tcFrames}
        fps={TRUE_CRIME_DEFAULT.fps}
        width={TRUE_CRIME_DEFAULT.width}
        height={TRUE_CRIME_DEFAULT.height}
        defaultProps={TRUE_CRIME_DEFAULT as unknown as Record<string, unknown>}
      />
      <Composition
        id="ReactionVideo"
        component={ReactionVideo as React.FC}
        durationInFrames={rxFrames}
        fps={REACTION_DEFAULT.fps}
        width={REACTION_DEFAULT.width}
        height={REACTION_DEFAULT.height}
        defaultProps={REACTION_DEFAULT as unknown as Record<string, unknown>}
      />
    </>
  );
};
