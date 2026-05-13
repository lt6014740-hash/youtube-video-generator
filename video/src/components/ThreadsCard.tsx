import React from "react";
import {
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { ThreadsPostData } from "../types";

interface ThreadsCardProps {
  post: ThreadsPostData;
  delay?: number;
}

export const ThreadsCard: React.FC<ThreadsCardProps> = ({
  post,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const appear = spring({
    frame,
    fps,
    config: { damping: 18, stiffness: 90 },
    delay,
  });

  const slideY = interpolate(appear, [0, 1], [60, 0]);

  return (
    <div
      style={{
        background: "#181818",
        borderRadius: 20,
        padding: "20px 24px",
        width: "100%",
        maxWidth: 560,
        opacity: appear,
        transform: `translateY(${slideY}px)`,
        boxShadow: "0 4px 24px rgba(0,0,0,0.3)",
        position: "relative",
      }}
    >
      {/* Header: avatar + username + time + Threads logo */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          marginBottom: 14,
        }}
      >
        {/* Avatar */}
        <div style={{ position: "relative" }}>
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: "50%",
              background: post.avatarColor || "#444",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 22,
              overflow: "hidden",
            }}
          >
            {post.avatarImage ? (
              <Img
                src={staticFile(post.avatarImage)}
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
            ) : (
              <span>{post.avatarEmoji || "👤"}</span>
            )}
          </div>
          {/* Follow button */}
          <div
            style={{
              position: "absolute",
              bottom: -4,
              right: -4,
              width: 20,
              height: 20,
              borderRadius: "50%",
              background: "#fff",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 14,
              fontWeight: 900,
              color: "#000",
              border: "2px solid #181818",
            }}
          >
            +
          </div>
        </div>

        {/* Username + time */}
        <div style={{ flex: 1 }}>
          <span
            style={{
              color: "#ffffff",
              fontSize: 17,
              fontWeight: 700,
              fontFamily: "Inter, system-ui, sans-serif",
            }}
          >
            {post.username}
          </span>
          <span
            style={{
              color: "#666",
              fontSize: 15,
              fontWeight: 500,
              fontFamily: "Inter, system-ui, sans-serif",
              marginLeft: 8,
            }}
          >
            {post.timeAgo}
          </span>
        </div>

        {/* Threads logo */}
        <div
          style={{
            fontSize: 22,
            color: "#888",
          }}
        >
          ⓧ
        </div>
      </div>

      {/* Post content */}
      <div
        style={{
          color: "#e8e8e8",
          fontSize: 18,
          fontFamily: "Inter, system-ui, sans-serif",
          fontWeight: 400,
          lineHeight: 1.5,
          marginBottom: 16,
          whiteSpace: "pre-wrap",
        }}
      >
        {post.content}
      </div>

      {/* Post image (if any) */}
      {post.postImage && (
        <div
          style={{
            borderRadius: 14,
            overflow: "hidden",
            marginBottom: 16,
            maxHeight: 280,
          }}
        >
          <Img
            src={staticFile(post.postImage)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
        </div>
      )}

      {/* Action bar: like, comment, repost, share */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 20,
        }}
      >
        <ActionIcon icon="♡" count={post.likes} />
        <ActionIcon icon="💬" count={post.comments} />
        <ActionIcon icon="🔄" count={post.reposts} />
        <ActionIcon icon="➤" />
      </div>

      {/* "Hiển thị phản hồi" link (if has replies) */}
      {post.hasReplies && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            marginTop: 12,
            paddingTop: 10,
            borderTop: "1px solid #333",
          }}
        >
          <div
            style={{
              display: "flex",
              gap: -4,
            }}
          >
            <span style={{ fontSize: 14 }}>🐸</span>
            <span style={{ fontSize: 14 }}>⬇️</span>
          </div>
          <span
            style={{
              color: "#666",
              fontSize: 14,
              fontFamily: "Inter, system-ui, sans-serif",
            }}
          >
            Hiển thị phản hồi
          </span>
        </div>
      )}
    </div>
  );
};

const ActionIcon: React.FC<{ icon: string; count?: number }> = ({
  icon,
  count,
}) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: 6,
    }}
  >
    <span style={{ fontSize: 20, color: "#aaa" }}>{icon}</span>
    {count !== undefined && count > 0 && (
      <span
        style={{
          color: "#888",
          fontSize: 15,
          fontFamily: "Inter, system-ui, sans-serif",
          fontWeight: 500,
        }}
      >
        {count >= 1000 ? `${(count / 1000).toFixed(1)}K` : count}
      </span>
    )}
  </div>
);
