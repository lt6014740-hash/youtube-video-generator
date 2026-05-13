#!/usr/bin/env python3
"""
Generate a video from trending Threads posts (12/5/2026).
Uses Edge-TTS with male Vietnamese voice (vi-VN-NamMinhNeural).
Includes background images and original Threads quotes.
"""

import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.app.schemas import ScriptScene, VideoScript
from backend.app.subtitle_generator import generate_srt, generate_subtitle_data
from backend.app.tts_service import synthesize_edge_tts

OUTPUT_DIR = Path(__file__).parent / "output"
VIDEO_DIR = Path(__file__).parent / "video"

MALE_VOICE = "vi-VN-NamMinhNeural"


def create_script() -> VideoScript:
    scenes = [
        ScriptScene(
            scene_number=1,
            title="Lạm phát Mỹ tăng cao nhất từ 2023",
            narration=(
                "Theo dữ liệu mới công bố, chỉ số giá tiêu dùng tại Mỹ "
                "tăng 3,8% trong tháng 4 so với cùng kỳ năm trước, "
                "mức cao nhất kể từ tháng 5 năm 2023. "
                "Nhiều chuyên gia cảnh báo rằng con số này "
                "có thể còn tiếp tục tăng trong thời gian tới, "
                "ảnh hưởng đến chi tiêu và đời sống người dân."
            ),
            visual_description="CPI inflation chart rising sharply",
            duration_seconds=14.0,
        ),
        ScriptScene(
            scene_number=2,
            title="AI đẩy giá chip tăng vọt",
            narration=(
                "Sàn giao dịch CME Group thông báo sẽ sớm cho phép "
                "nhà đầu tư đặt cược vào giá chip máy tính. "
                "Nguyên nhân là do nhu cầu trí tuệ nhân tạo "
                "đã đẩy chi phí sản xuất chip tăng chóng mặt. "
                "Đây là bước đi chưa từng có trong lịch sử "
                "thị trường tài chính toàn cầu."
            ),
            visual_description="CME Group trading floor with AI chip graphics",
            duration_seconds=13.0,
        ),
        ScriptScene(
            scene_number=3,
            title="iOS 27 nâng cấp Camera toàn diện",
            narration=(
                "Theo nguồn tin từ 9 to 5 Mac, hệ điều hành iOS 27 "
                "sẽ mang đến ứng dụng Camera được nâng cấp toàn diện "
                "với khả năng tùy chỉnh hoàn toàn theo ý người dùng. "
                "Đây được coi là thay đổi lớn nhất về camera "
                "trên iPhone kể từ khi Apple giới thiệu Camera Control "
                "trên dòng iPhone 16."
            ),
            visual_description="iPhone camera interface with customizable controls",
            duration_seconds=13.0,
        ),
        ScriptScene(
            scene_number=4,
            title="Bầu cử giữa kỳ Mỹ 2026 nóng lên",
            narration=(
                "Ủy ban Quốc gia Đảng Cộng hòa tuyên bố "
                "triển khai nhân sự giám sát bầu cử "
                "tại ít nhất 17 bang trên toàn nước Mỹ, "
                "bao gồm các quan sát viên và giám sát viên phòng phiếu. "
                "Bài đăng này đã thu hút hơn 230 lượt thích "
                "và hàng trăm bình luận trên Threads."
            ),
            visual_description="US election monitoring operations in multiple states",
            duration_seconds=13.0,
        ),
        ScriptScene(
            scene_number=5,
            title="Xu hướng 'Sống ích kỷ' gây bão",
            narration=(
                "Một bài đăng kêu gọi mọi người hãy ích kỷ hơn "
                "trong công việc đã nhận được gần 2 nghìn lượt thích "
                "trên Threads hôm nay. Nội dung khuyên rằng: "
                "hãy về đúng giờ, nghỉ phép đầy đủ, "
                "không nghe điện thoại công việc cuối tuần, "
                "và luôn đặt bản thân lên hàng đầu. "
                "Bài viết châm ngòi cuộc tranh luận sôi nổi "
                "về cân bằng công việc và cuộc sống."
            ),
            visual_description="Work-life balance concept with clock and freedom",
            duration_seconds=15.0,
        ),
        ScriptScene(
            scene_number=6,
            title="Khủng hoảng giáo dục đại học",
            narration=(
                "Một cựu sinh viên trường Ivy League chia sẻ "
                "tạp chí cựu sinh viên với trang bìa là "
                "hướng dẫn tìm việc trong thị trường khó khăn. "
                "Bài đăng nhấn mạnh rằng giáo dục đại học Mỹ "
                "đang đối mặt khủng hoảng toàn diện: "
                "học phí tăng vọt, AI gây bất ổn thị trường việc làm, "
                "và chính sách cắt giảm tài trợ nghiên cứu."
            ),
            visual_description="University campus with crisis warning signs",
            duration_seconds=14.0,
        ),
    ]

    total_duration = sum(s.duration_seconds for s in scenes)

    return VideoScript(
        title="Hot trên Threads hôm nay 12/5/2026",
        description="Tổng hợp các bài đăng hot nhất trên Threads ngày 12 tháng 5 năm 2026",
        language="vi",
        scenes=scenes,
        tags=["threads", "trending", "tin tức", "hot", "2026"],
        total_duration_seconds=total_duration,
    )


# Image files in video/public/images/ and original Threads quotes
SCENE_IMAGES = [
    "images/scene1_inflation.jpg",
    "images/scene2_ai_chip.jpg",
    "images/scene3_iphone.jpg",
    "images/scene4_election.jpg",
    "images/scene5_worklife.jpg",
    "images/scene6_education.jpg",
]

SCENE_QUOTES = [
    {
        "quote": "The consumer price index rose at an annualized rate of 3.8% in April. This is the highest rate since May 2023 — and probably much lower than it's about to be.",
        "author": "annazarves",
    },
    {
        "quote": "Traders will soon be able to bet on computer chip prices as AI drives costs skyward",
        "author": "cnbcinternational",
    },
    {
        "quote": "iOS 27's upgraded Camera app will be 'fully customizable,' per report",
        "author": "9to5mac",
    },
    {
        "quote": "The Republican National Committee announced it is deploying staff — including 'poll watchers' — to at least 17 states ahead of the 2026 midterms.",
        "author": "marc.e.elias",
    },
    {
        "quote": "Be selfish. Leave at 5pm. Take all your PTO. Ignore work calls on the weekend. Always look out for yourself, FIRST.",
        "author": "suchisthesach",
    },
    {
        "quote": "College education is in complete crisis: soaring tuition, AI instability, donor psychosis, Trump's wrecking ball through grant funding — all detonating at once.",
        "author": "sierracascadia",
    },
]


async def generate_audio(script: VideoScript) -> list[str]:
    public_audio_dir = VIDEO_DIR / "public" / "audio"
    public_audio_dir.mkdir(parents=True, exist_ok=True)

    audio_files = []
    for i, scene in enumerate(script.scenes):
        print(f"  Tạo audio scene {i+1}/{len(script.scenes)}: {scene.title}")
        audio_file, duration = await synthesize_edge_tts(
            text=scene.narration,
            language="vi",
            voice=MALE_VOICE,
        )
        filename = Path(audio_file).name
        public_path = public_audio_dir / filename
        shutil.copy2(audio_file, public_path)
        audio_files.append(f"audio/{filename}")
        scene.duration_seconds = max(scene.duration_seconds, duration + 2.0)
        print(f"    -> {public_path} ({duration:.1f}s)")
    return audio_files


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("BƯỚC 1: Tạo kịch bản từ Threads trending")
    print("=" * 60)
    script = create_script()
    print(f"Tiêu đề: {script.title}")
    print(f"Số scene: {len(script.scenes)}")

    script_file = OUTPUT_DIR / "scripts" / "script_threads.json"
    script_file.parent.mkdir(parents=True, exist_ok=True)
    with open(script_file, "w", encoding="utf-8") as f:
        json.dump(script.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"Script lưu tại: {script_file}")

    print("\n" + "=" * 60)
    print(f"BƯỚC 2: Tạo giọng đọc NAM ({MALE_VOICE})")
    print("=" * 60)
    audio_files = await generate_audio(script)

    print("\n" + "=" * 60)
    print("BƯỚC 3: Tạo phụ đề")
    print("=" * 60)
    subtitle_file = str(OUTPUT_DIR / "subtitles_threads.srt")
    generate_srt(script, subtitle_file)
    print(f"Phụ đề lưu tại: {subtitle_file}")

    print("\n" + "=" * 60)
    print("BƯỚC 4: Chuẩn bị render video (có hình ảnh + trích dẫn)")
    print("=" * 60)
    subtitles = generate_subtitle_data(script)

    scenes_data = []
    for i, scene in enumerate(script.scenes):
        scene_data = {
            "sceneNumber": scene.scene_number,
            "title": scene.title,
            "narration": scene.narration,
            "visualDescription": scene.visual_description,
            "durationInSeconds": scene.duration_seconds,
            "audioFile": audio_files[i] if i < len(audio_files) else "",
        }
        if i < len(SCENE_IMAGES):
            scene_data["imageFile"] = SCENE_IMAGES[i]
        if i < len(SCENE_QUOTES):
            scene_data["quote"] = SCENE_QUOTES[i]["quote"]
            scene_data["quoteAuthor"] = SCENE_QUOTES[i]["author"]
        scenes_data.append(scene_data)

    total_duration = sum(s.duration_seconds for s in script.scenes)

    props = {
        "title": script.title,
        "scenes": scenes_data,
        "subtitles": subtitles,
        "totalDurationInSeconds": total_duration,
        "backgroundColor": "#0a0a1a",
        "subtitleColor": "#ffffff",
        "accentColor": "#8b5cf6",
        "fontFamily": "Inter, system-ui, sans-serif",
        "language": "vi",
        "fps": 30,
        "width": 1920,
        "height": 1080,
    }

    props_file = str(OUTPUT_DIR / "video_props_threads.json")
    with open(props_file, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)
    print(f"Props lưu tại: {props_file}")

    print("\n" + "=" * 60)
    print("BƯỚC 5: Render video bằng Remotion")
    print("=" * 60)
    output_file = str(OUTPUT_DIR / "threads_hot_12_05_2026.mp4")
    print(f"Output: {output_file}")
    print("Đang render... (có thể mất vài phút)")

    result = subprocess.run(
        [
            "npx", "remotion", "render",
            "YouTubeVideo",
            "--props", props_file,
            "--output", output_file,
            "--codec", "h264",
        ],
        cwd=str(VIDEO_DIR),
        capture_output=True,
        text=True,
        timeout=600,
    )

    if result.returncode != 0:
        print(f"STDERR: {result.stderr}")
        print(f"STDOUT: {result.stdout}")
        raise RuntimeError(f"Render thất bại: {result.stderr}")

    print(f"\nVideo đã tạo thành công: {output_file}")

    print("\n" + "=" * 60)
    print("HOÀN THÀNH!")
    print("=" * 60)
    print(f"Script: {script_file}")
    print(f"Audio: {len(audio_files)} files ({MALE_VOICE})")
    print(f"Phụ đề: {subtitle_file}")
    print(f"Video: {output_file}")
    print(f"Hình ảnh: {len(SCENE_IMAGES)} ảnh minh họa")
    print(f"Trích dẫn: {len(SCENE_QUOTES)} trích dẫn từ Threads")


if __name__ == "__main__":
    asyncio.run(main())
