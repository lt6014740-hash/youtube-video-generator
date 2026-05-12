import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useVideoConfig,
} from "remotion";
import { OutroCard } from "./components/OutroCard";
import { Scene } from "./components/Scene";
import { Subtitles } from "./components/Subtitles";
import { TitleCard } from "./components/TitleCard";
import type { VideoProps } from "./types";

const TITLE_DURATION_SECONDS = 4;
const OUTRO_DURATION_SECONDS = 5;

export const YouTubeVideo: React.FC<VideoProps> = ({
  title,
  scenes,
  subtitles,
  totalDurationInSeconds,
  backgroundColor,
  subtitleColor,
  accentColor,
  fontFamily,
  language,
  fps,
}) => {
  const effectiveFps = fps || 30;
  const titleDurationFrames = TITLE_DURATION_SECONDS * effectiveFps;
  const outroDurationFrames = OUTRO_DURATION_SECONDS * effectiveFps;

  let currentFrame = titleDurationFrames;

  return (
    <AbsoluteFill style={{ backgroundColor }}>
      {/* Title Card */}
      <Sequence from={0} durationInFrames={titleDurationFrames}>
        <TitleCard
          title={title}
          backgroundColor={backgroundColor}
          accentColor={accentColor}
          subtitleColor={subtitleColor}
          fontFamily={fontFamily}
          language={language}
        />
      </Sequence>

      {/* Scenes */}
      {scenes.map((scene, index) => {
        const sceneDurationFrames = Math.round(scene.durationInSeconds * effectiveFps);
        const from = currentFrame;
        currentFrame += sceneDurationFrames;

        return (
          <Sequence
            key={scene.sceneNumber}
            from={from}
            durationInFrames={sceneDurationFrames}
          >
            <Scene
              scene={scene}
              sceneIndex={index}
              backgroundColor={backgroundColor}
              accentColor={accentColor}
              fontFamily={fontFamily}
              subtitleColor={subtitleColor}
            />
          </Sequence>
        );
      })}

      {/* Subtitles overlay (spans all scenes) */}
      <Sequence from={titleDurationFrames}>
        <Subtitles
          subtitles={subtitles}
          color={subtitleColor}
          accentColor={accentColor}
          fontFamily={fontFamily}
        />
      </Sequence>

      {/* Outro Card */}
      <Sequence from={currentFrame} durationInFrames={outroDurationFrames}>
        <OutroCard
          backgroundColor={backgroundColor}
          accentColor={accentColor}
          subtitleColor={subtitleColor}
          fontFamily={fontFamily}
          language={language}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
