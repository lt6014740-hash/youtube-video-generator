export interface SceneData {
  sceneNumber: number;
  title: string;
  narration: string;
  visualDescription: string;
  durationInSeconds: number;
  audioFile: string;
  imageFile?: string;
  quote?: string;
  quoteAuthor?: string;
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

// --- True Crime types ---

export interface TrueCrimeSceneData {
  sceneNumber: number;
  title: string;
  narration: string;
  durationInSeconds: number;
  audioFile: string;
  imageFile?: string;
  phase?: string;
  evidence?: string;
  evidenceLabel?: string;
}

export interface TimelineEventData {
  time: string;
  label: string;
  icon?: string;
}

export interface TrueCrimeProps {
  title: string;
  scenes: TrueCrimeSceneData[];
  subtitles: SubtitleData[];
  timelineEvents: TimelineEventData[];
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

// --- Reaction / Review types ---

export interface ReactionEmojiData {
  emoji: string;
  label: string;
  count: number;
  color: string;
}

export interface RatingData {
  label: string;
  value: number;
  maxValue: number;
  color?: string;
}

export interface ReactionSceneData {
  sceneNumber: number;
  title: string;
  narration: string;
  durationInSeconds: number;
  audioFile: string;
  imageFile?: string;
  quote?: string;
  quoteAuthor?: string;
  reactions?: ReactionEmojiData[];
  ratings?: RatingData[];
}

export interface ReactionProps {
  title: string;
  scenes: ReactionSceneData[];
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

// --- Threads Scroll types ---

export interface ThreadsPostData {
  username: string;
  timeAgo: string;
  content: string;
  likes?: number;
  comments?: number;
  reposts?: number;
  hasReplies?: boolean;
  avatarEmoji?: string;
  avatarColor?: string;
  avatarImage?: string;
  postImage?: string;
  audioFile?: string;
  durationInSeconds: number;
}

export interface ThreadsScrollProps {
  posts: ThreadsPostData[];
  totalDurationInSeconds: number;
  fps: number;
  width: number;
  height: number;
}
