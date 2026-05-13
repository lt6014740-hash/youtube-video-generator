import React from "react";
import {
  AbsoluteFill,
  Sequence,
} from "remotion";
import { OutroCard } from "./components/OutroCard";
import { ReactionScene } from "./components/ReactionScene";
import { Subtitles } from "./components/Subtitles";
import { TitleCard } from "./components/TitleCard";
import type { ReactionProps } from "./types";

const TITLE_DURATION_SECONDS = 4;
const OUTRO_DURATION_SECONDS = 5;

export const ReactionVideo: React.FC<ReactionProps> = ({
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
    <AbsoluteFill style={{ backgroundColor: "#0a0a1e" }}>
      {/* Title Card */}
      <Sequence from={0} durationInFrames={titleDurationFrames}>
        <TitleCard
          title={title}
          backgroundColor="#0a0a1e"
          accentColor={accentColor}
          subtitleColor={subtitleColor}
          fontFamily={fontFamily}
          language={language}
        />
      </Sequence>

      {/* Reaction Scenes */}
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
            <ReactionScene
              scene={scene}
              sceneIndex={index}
              totalScenes={scenes.length}
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
          backgroundColor="#0a0a1e"
          accentColor={accentColor}
          subtitleColor={subtitleColor}
          fontFamily={fontFamily}
          language={language}
        />
      </Sequence>
    </AbsoluteFill>
  );
};
