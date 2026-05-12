export interface SceneData {
  sceneNumber: number;
  title: string;
  narration: string;
  visualDescription: string;
  durationInSeconds: number;
  audioFile: string;
}

export interface SubtitleData {
  text: string;
  startFrame: number;
  endFrame: number;
}

export interface VideoProps {
  title: string;
  scenes: SceneData[];
  subtitles: SubtitleData[];
  totalDurationInSeconds: number;
  backgroundColor: string;
  subtitleColor: string;
  accentColor: string;
  fontFamily: string;
  language: string;
  fps: number;
  width: number;
  height: number;
}
