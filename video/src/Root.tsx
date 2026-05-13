import React from "react";
import { Composition } from "remotion";
import { HistoricalVideo } from "./HistoricalVideo";
import { ReactionVideo } from "./ReactionVideo";
import { ThreadsScrollVideo } from "./ThreadsScrollVideo";
import { TrueCrimeVideo } from "./TrueCrimeVideo";
import { YouTubeVideo } from "./YouTubeVideo";
import type { HistoricalProps, ReactionProps, ThreadsScrollProps, TrueCrimeProps, VideoProps } from "./types";

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

const HISTORICAL_DEFAULT: HistoricalProps = {
  title: "Phe \u0110\u1ed3ng Minh \u0111\u00e3 chi\u1ebfn th\u1eafng Ph\u00e1t x\u00edt \u0110\u1ee9c nh\u01b0 th\u1ebf n\u00e0o?",
  scenes: [
    {
      sceneNumber: 1,
      title: "B\u1ed1i c\u1ea3nh Th\u1ebf chi\u1ebfn II",
      narration: "N\u0103m 1939, chi\u1ebfn tranh th\u1ebf gi\u1edbi b\u00f9ng n\u1ed5...",
      durationInSeconds: 8,
      audioFile: "",
      year: "1939",
      icon: "\u2694\ufe0f",
      bgColor: "#1a3a5c",
    },
    {
      sceneNumber: 2,
      title: "Tr\u1eadn Normandy",
      narration: "Ng\u00e0y 6/6/1944, D-Day b\u1eaft \u0111\u1ea7u...",
      durationInSeconds: 8,
      audioFile: "",
      year: "1944",
      icon: "\ud83c\udfc4",
      bgColor: "#2d4a3e",
    },
  ],
  totalDurationInSeconds: 16,
  channelName: "Ki\u1ebfn Th\u1ee9c Hay",
  fps: 30,
  width: 720,
  height: 1280,
};

const THREADS_SCROLL_DEFAULT: ThreadsScrollProps = {
  posts: [
    {
      username: "user1",
      timeAgo: "2 giờ",
      content: "Bài đăng mẫu trên Threads",
      likes: 100,
      comments: 10,
      reposts: 5,
      avatarEmoji: "🐸",
      avatarColor: "#4a9",
      durationInSeconds: 6,
    },
  ],
  totalDurationInSeconds: 6,
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
  const tsFrames = Math.round(
    THREADS_SCROLL_DEFAULT.totalDurationInSeconds * THREADS_SCROLL_DEFAULT.fps
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
      <Composition
        id="HistoricalVideo"
        component={HistoricalVideo as React.FC}
        durationInFrames={Math.round(
          HISTORICAL_DEFAULT.totalDurationInSeconds * HISTORICAL_DEFAULT.fps
        )}
        fps={HISTORICAL_DEFAULT.fps}
        width={HISTORICAL_DEFAULT.width}
        height={HISTORICAL_DEFAULT.height}
        defaultProps={HISTORICAL_DEFAULT as unknown as Record<string, unknown>}
        calculateMetadata={async ({ props }) => {
          const p = props as unknown as HistoricalProps;
          const totalSeconds =
            p.totalDurationInSeconds ||
            p.scenes.reduce((s, sc) => s + sc.durationInSeconds, 0);
          return {
            durationInFrames: Math.round(totalSeconds * (p.fps || 30)),
            fps: p.fps || 30,
            width: p.width || 720,
            height: p.height || 1280,
          };
        }}
      />
      <Composition
        id="ThreadsScrollVideo"
        component={ThreadsScrollVideo as React.FC}
        durationInFrames={tsFrames}
        fps={THREADS_SCROLL_DEFAULT.fps}
        width={THREADS_SCROLL_DEFAULT.width}
        height={THREADS_SCROLL_DEFAULT.height}
        defaultProps={THREADS_SCROLL_DEFAULT as unknown as Record<string, unknown>}
        calculateMetadata={async ({ props }) => {
          const p = props as unknown as ThreadsScrollProps;
          const totalSeconds = p.totalDurationInSeconds || p.posts.reduce((s, post) => s + post.durationInSeconds, 0);
          return {
            durationInFrames: Math.round(totalSeconds * (p.fps || 30)),
            fps: p.fps || 30,
            width: p.width || 1920,
            height: p.height || 1080,
          };
        }}
      />
    </>
  );
};
