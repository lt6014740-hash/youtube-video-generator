import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

interface OutroCardProps {
  backgroundColor: string;
  accentColor: string;
  subtitleColor: string;
  fontFamily: string;
  language: string;
}

const OUTRO_TEXT: Record<string, { thanks: string; subscribe: string; like: string }> = {
  en: { thanks: "Thanks for watching!", subscribe: "Subscribe", like: "Like & Share" },
  vi: { thanks: "Cảm ơn bạn đã xem!", subscribe: "Đăng ký", like: "Thích & Chia sẻ" },
  zh: { thanks: "感谢观看！", subscribe: "订阅", like: "点赞分享" },
  ja: { thanks: "ご視聴ありがとう！", subscribe: "チャンネル登録", like: "いいね＆シェア" },
  ko: { thanks: "시청해 주셔서 감사합니다!", subscribe: "구독", like: "좋아요 & 공유" },
};

export const OutroCard: React.FC<OutroCardProps> = ({
  backgroundColor,
  accentColor,
  subtitleColor,
  fontFamily,
  language,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const texts = OUTRO_TEXT[language] || OUTRO_TEXT.en;

  const titleSpring = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 60 },
    delay: 5,
  });

  const button1Spring = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 80 },
    delay: 20,
  });

  const button2Spring = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 80 },
    delay: 30,
  });

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, ${backgroundColor} 0%, #000000 100%)`,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        gap: 50,
      }}
    >
      <h1
        style={{
          color: subtitleColor,
          fontSize: 64,
          fontFamily,
          fontWeight: 800,
          opacity: titleSpring,
          transform: `scale(${titleSpring})`,
          textShadow: `0 4px 20px ${accentColor}40`,
        }}
      >
        {texts.thanks}
      </h1>

      <div style={{ display: "flex", gap: 40 }}>
        <div
          style={{
            background: accentColor,
            borderRadius: 16,
            padding: "20px 50px",
            opacity: button1Spring,
            transform: `translateY(${interpolate(button1Spring, [0, 1], [30, 0])}px)`,
          }}
        >
          <span
            style={{
              color: "#fff",
              fontSize: 32,
              fontFamily,
              fontWeight: 700,
            }}
          >
            🔔 {texts.subscribe}
          </span>
        </div>

        <div
          style={{
            background: "rgba(255,255,255,0.1)",
            border: `2px solid ${accentColor}`,
            borderRadius: 16,
            padding: "20px 50px",
            opacity: button2Spring,
            transform: `translateY(${interpolate(button2Spring, [0, 1], [30, 0])}px)`,
          }}
        >
          <span
            style={{
              color: subtitleColor,
              fontSize: 32,
              fontFamily,
              fontWeight: 700,
            }}
          >
            👍 {texts.like}
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
