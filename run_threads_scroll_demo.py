#!/usr/bin/env python3
"""
Demo: Threads Scroll video — kiểu @hotthread999 trên TikTok.
Hiển thị các bài đăng Threads dark mode trên nền caro pastel.
"""

import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.app.tts_service import synthesize_edge_tts

OUTPUT_DIR = Path(__file__).parent / "output"
VIDEO_DIR = Path(__file__).parent / "video"
MALE_VOICE = "vi-VN-NamMinhNeural"


POSTS = [
    {
        "username": "ho082000",
        "timeAgo": "4 giờ",
        "content": "-Một app thì toàn xàm lờ\n-còn một ápp thì toàn lồn",
        "likes": 663,
        "comments": 43,
        "reposts": 89,
        "hasReplies": False,
        "avatarEmoji": "🐸",
        "avatarColor": "#4a9955",
        "narration": "Người dùng ho không tám hai nghìn bình luận: "
                     "Một app thì toàn xàm lờ, còn một app thì toàn lồn. "
                     "Bài đăng nhận được 663 lượt thích và 43 bình luận.",
    },
    {
        "username": "tnphong1510",
        "timeAgo": "2 giờ",
        "content": "Thật không để t tải:)",
        "likes": 4,
        "comments": 2,
        "reposts": 0,
        "hasReplies": True,
        "avatarEmoji": "🐮",
        "avatarColor": "#c4782e",
        "narration": "Người dùng tê-en-phong 1510 viết: "
                     "Thật không để tui tải. Kèm theo mặt cười.",
    },
    {
        "username": "bongtyet_.celine",
        "timeAgo": "2 giờ",
        "content": "app X đọc tin tức ok mò",
        "likes": 3,
        "comments": 0,
        "reposts": 0,
        "hasReplies": False,
        "avatarEmoji": "🐱",
        "avatarColor": "#888",
        "narration": "Người dùng bông tuyết celine nhận xét: "
                     "App X đọc tin tức ok mò. "
                     "Ý kiến cho rằng X phù hợp hơn để đọc tin.",
    },
    {
        "username": "phamtan_07",
        "timeAgo": "46 phút",
        "content": "Bộ đôi hủy diệt",
        "likes": 0,
        "comments": 0,
        "reposts": 0,
        "hasReplies": False,
        "avatarEmoji": "🌅",
        "avatarColor": "#5577aa",
        "narration": "Phạm Tấn zero bảy gọi hai app này là "
                     "bộ đôi hủy diệt. Ngắn gọn nhưng nói lên tất cả.",
    },
    {
        "username": "radiance._k",
        "timeAgo": "38 phút",
        "content": "App bên trái trông cứ lạ lạ nhỉ, nó là app dùng để làm gì thế mọi người?",
        "likes": 0,
        "comments": 1,
        "reposts": 0,
        "hasReplies": True,
        "avatarEmoji": "🎨",
        "avatarColor": "#7755cc",
        "narration": "Radiance k hỏi: App bên trái trông cứ lạ lạ nhỉ, "
                     "nó là app dùng để làm gì thế mọi người? "
                     "Có vẻ như không phải ai cũng biết đến Threads.",
    },
    {
        "username": "viral_threads_vn",
        "timeAgo": "1 giờ",
        "content": "Threads ngày càng nhiều người Việt dùng rồi 🔥\nX thì vẫn là vua tin tức quốc tế\nMỗi app một thế mạnh!",
        "likes": 1200,
        "comments": 89,
        "reposts": 234,
        "hasReplies": True,
        "avatarEmoji": "🔥",
        "avatarColor": "#e94560",
        "narration": "Viral Threads Việt Nam tổng kết: "
                     "Threads ngày càng nhiều người Việt dùng rồi. "
                     "X thì vẫn là vua tin tức quốc tế. "
                     "Mỗi app một thế mạnh! "
                     "Bài đăng nhận 1.200 likes và 89 bình luận.",
    },
]


async def generate_audio(posts: list[dict]) -> list[str]:
    public_audio_dir = VIDEO_DIR / "public" / "audio"
    public_audio_dir.mkdir(parents=True, exist_ok=True)
    audio_files = []
    durations = []
    for i, post in enumerate(posts):
        print(f"  Audio post {i+1}/{len(posts)}: @{post['username']}")
        audio_file, duration = await synthesize_edge_tts(
            text=post["narration"], language="vi", voice=MALE_VOICE,
        )
        filename = Path(audio_file).name
        public_path = public_audio_dir / filename
        shutil.copy2(audio_file, public_path)
        audio_files.append(f"audio/{filename}")
        durations.append(duration)
        print(f"    -> {duration:.1f}s")
    return audio_files, durations


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("THREADS SCROLL VIDEO — Kiểu @hotthread999")
    print("=" * 60)

    audio_files, durations = await generate_audio(POSTS)

    posts_data = []
    for i, post in enumerate(POSTS):
        dur = max(durations[i] + 1.5, 5.0)
        posts_data.append({
            "username": post["username"],
            "timeAgo": post["timeAgo"],
            "content": post["content"],
            "likes": post.get("likes", 0),
            "comments": post.get("comments", 0),
            "reposts": post.get("reposts", 0),
            "hasReplies": post.get("hasReplies", False),
            "avatarEmoji": post.get("avatarEmoji", "👤"),
            "avatarColor": post.get("avatarColor", "#444"),
            "audioFile": audio_files[i],
            "durationInSeconds": dur,
        })

    total_duration = sum(p["durationInSeconds"] for p in posts_data)

    props = {
        "posts": posts_data,
        "totalDurationInSeconds": total_duration,
        "fps": 30,
        "width": 1920,
        "height": 1080,
    }

    props_file = str(OUTPUT_DIR / "video_props_threads_scroll.json")
    with open(props_file, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    output_file = str(OUTPUT_DIR / "threads_scroll_demo.mp4")
    print(f"\nRendering → {output_file}")

    result = subprocess.run(
        [
            "npx", "remotion", "render",
            "ThreadsScrollVideo",
            "--props", props_file,
            "--output", output_file,
            "--codec", "h264",
        ],
        cwd=str(VIDEO_DIR),
        capture_output=True, text=True, timeout=600,
    )

    if result.returncode != 0:
        print(f"STDERR: {result.stderr}")
        print(f"STDOUT: {result.stdout}")
        raise RuntimeError(f"Render failed: {result.stderr}")

    print(f"\nVideo hoàn thành: {output_file}")
    print(f"Số bài đăng: {len(posts_data)}")
    print(f"Tổng thời lượng: {total_duration:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
