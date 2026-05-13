import React from "react";
import {
  AbsoluteFill,
  Sequence,
} from "remotion";
import { OutroCard } from "./components/OutroCard";
import { Subtitles } from "./components/Subtitles";
import { TitleCard } from "./components/TitleCard";
import { TrueCrimeScene } from "./components/TrueCrimeScene";
import type { TrueCrimeProps } from "./types";

const TITLE_DURATION_SECONDS = 5;
const OUTRO_DURATION_SECONDS = 5;

export const TrueCrimeVideo: React.FC<TrueCrimeProps> = ({
  title,
  scenes,
  subtitles,
  timelineEvents,
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
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
      {/* Title Card */}
      <Sequence from={0} durationInFrames={titleDurationFrames}>
        <TitleCard
          title={title}
          backgroundColor="#0a0a0a"
          accentColor={accentColor}
          subtitleColor={subtitleColor}
          fontFamily={fontFamily}
          language={language}
        />
      </Sequence>

      {/* True Crime Scenes */}
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
            <TrueCrimeScene
              scene={scene}
              sceneIndex={index}
              totalScenes={scenes.length}
              timelineEvents={timelineEvents}
              accentColor={accentColor}
              fontFamily={fontFamily}
            />
          </Sequence>
        );
      })}

      {/* Subtitles overlay */}
      <Sequence from={titleDurationFrames}>
        <Subtitles
          subtitles={subtitles}
          color={subtitleColor}
          accentColor={accentColor}
          fontFamily={fontFamily}
        />
      </Sequence>

      {/* Outro */}
      <Sequence from={currentFrame} durationInFrames={outroDurationFrames}>
        <OutroCard
          backgroundColor="#0a0a0a"
          accentColor={accentColor}
          subtitleColor={subtitleColor}
          fontFamily={fontFamily}
          language={language}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
