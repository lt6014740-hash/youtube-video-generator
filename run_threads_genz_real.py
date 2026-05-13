#!/usr/bin/env python3
"""
Threads Scroll Video — Gen Z Viet Nam (Du lieu thuc te)
Thu thap tu Threads search "gen z" ngay 12/5/2026.
Tu danh gia len kich ban.
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


# ===== DU LIEU THUC TE TU THREADS SEARCH "GEN Z" - 12/5/2026 =====
POSTS = [
    {
        "username": "gen_z_can_gi",
        "timeAgo": "3 giờ",
        "content": (
            "Vãi cả chưởng tôi đang đọc cái gì thế này 😭\n\n"
            "Công an TP Cần Thơ bắt giữ nghi phạm 21 tuổi "
            "sát hại người yêu đang mang thai."
        ),
        "likes": 2400,
        "comments": 187,
        "reposts": 356,
        "hasReplies": True,
        "avatarEmoji": "🥀",
        "avatarColor": "#e94560",
        "narration": (
            "Ủa cái gì vậy nè, vụ này ở Cần Thơ ám ảnh cực! "
            "2 ngàn 4 likes, gần 200 bình luận luôn á."
        ),
    },
    {
        "username": "_genzdautuchung_",
        "timeAgo": "5 giờ",
        "content": (
            "GEN Z ĐẦU TƯ CHỨNG 📊\n"
            "Phân tích mẫu hình đỉnh kim cương trong chứng khoán.\n"
            "Lực mua dần mất ưu thế, bên bán kiểm soát thị trường."
        ),
        "likes": 93,
        "comments": 7,
        "reposts": 9,
        "hasReplies": True,
        "avatarEmoji": "📊",
        "avatarColor": "#3b82f6",
        "narration": (
            "Gen Z giờ chơi chứng luôn rồi nhé! Phân tích kỹ thuật gì đâu pro lắm. "
            "Đầu tư thông minh chứ hông phải đánh bạc đâu nha."
        ),
    },
    {
        "username": "gen.zbaddie",
        "timeAgo": "6 giờ",
        "content": (
            "Gen Z be like: Lương 8 triệu nhưng skincare routine 15 bước 💀\n\n"
            "Đùa chứ Gen Z bây giờ biết chăm sóc bản thân hơn "
            "các thế hệ trước nhiều!"
        ),
        "likes": 3200,
        "comments": 245,
        "reposts": 567,
        "hasReplies": True,
        "avatarEmoji": "💅",
        "avatarColor": "#a855f7",
        "narration": (
            "Lương 8 triệu mà skincare 15 bước, đúng chuẩn Gen Z! "
            "3 ngàn 2 likes, bài này viral dữ luôn á mọi người."
        ),
    },
    {
        "username": "toilanhatle",
        "timeAgo": "4 giờ",
        "content": (
            "Trend Doodle AI đang phủ sóng Threads 🎨\n"
            "Dùng ChatGPT để doodle ảnh, cute phết!\n"
            "Ai cũng tạo được tranh vẽ tay siêu xinh."
        ),
        "likes": 890,
        "comments": 67,
        "reposts": 123,
        "hasReplies": True,
        "avatarEmoji": "🎨",
        "avatarColor": "#f59e0b",
        "narration": (
            "Trend Doodle AI đang phủ sóng nè, cute phết luôn! "
            "Gen Z dùng AI vẽ tranh, ai cũng tạo được luôn á."
        ),
    },
    {
        "username": "sixtulu.2k6",
        "timeAgo": "2 giờ",
        "content": (
            "Mọi người ơi phân vân giữa FPT và Bách Khoa 😭\n"
            "Điểm học bạ 27-28, ngành CNTT chọn trường nào?\n"
            "Cho mình xin ý kiến với!"
        ),
        "likes": 456,
        "comments": 189,
        "reposts": 23,
        "hasReplies": True,
        "avatarEmoji": "📚",
        "avatarColor": "#06b6d4",
        "narration": (
            "2k6 phân vân FPT hay Bách Khoa, 189 bình luận tư vấn kìa! "
            "Threads giờ thành nơi chọn trường luôn rồi nha."
        ),
    },
    {
        "username": "bell.hats.vn",
        "timeAgo": "8 giờ",
        "content": (
            "Nón lá lụa làng Chuông handmade 🎀\n"
            "1 tuần đăng Threads: 62.000 views, 2.000 likes 💕\n"
            "Gen Z kế thừa nghề truyền thống 30 năm!"
        ),
        "likes": 2100,
        "comments": 156,
        "reposts": 89,
        "hasReplies": True,
        "avatarEmoji": "👒",
        "avatarColor": "#ec4899",
        "narration": (
            "Gái Gen Z 22 tuổi khôi phục nón lá lụa làng Chuông, 62 ngàn views! "
            "Cháy quá, truyền thống mà vẫn cực kỳ cool."
        ),
    },
    {
        "username": "suchisthesach",
        "timeAgo": "15 giờ",
        "content": (
            "Be selfish. Leave at 5pm. Take all your PTO.\n"
            "Ignore work calls on the weekend.\n"
            "Always look out for yourself, FIRST."
        ),
        "likes": 1800,
        "comments": 18,
        "reposts": 147,
        "hasReplies": True,
        "avatarEmoji": "💪",
        "avatarColor": "#f97316",
        "narration": (
            "Về đúng 5 giờ, nghỉ hết phép, đừng nghe điện công việc cuối tuần. "
            "Gen Z không sống để làm, mà làm để sống nha!"
        ),
    },
]


async def generate_audio(posts: list[dict]) -> tuple[list[str], list[float]]:
    public_audio_dir = VIDEO_DIR / "public" / "audio"
    public_audio_dir.mkdir(parents=True, exist_ok=True)
    audio_files: list[str] = []
    durations: list[float] = []
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
    print("THREADS SCROLL VIDEO — Gen Z Viet Nam (Du lieu thuc)")
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
            "avatarEmoji": post.get("avatarEmoji", ""),
            "avatarColor": post.get("avatarColor", "#444"),
            "audioFile": audio_files[i],
            "durationInSeconds": dur,
        })

    total_duration = sum(p["durationInSeconds"] for p in posts_data)

    props = {
        "posts": posts_data,
        "totalDurationInSeconds": total_duration,
        "backgroundMusic": "audio/background-music.mp3",
        "backgroundMusicVolume": 0.15,
        "fps": 30,
        "width": 1920,
        "height": 1080,
    }

    props_file = str(OUTPUT_DIR / "video_props_genz_real.json")
    with open(props_file, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    output_file = str(OUTPUT_DIR / "threads_genz_real.mp4")
    print(f"\nRendering -> {output_file}")
    print(f"So bai dang: {len(posts_data)}")
    print(f"Tong thoi luong: {total_duration:.1f}s")

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

    print(f"\nVideo hoan thanh: {output_file}")
    print(f"So bai dang: {len(posts_data)}")
    print(f"Tong thoi luong: {total_duration:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
