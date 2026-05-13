#!/usr/bin/env python3
"""
Demo: Reaction / Review video — Review iPhone 17 từ cộng đồng.
Uses Edge-TTS male voice + ReactionVideo Remotion composition.
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


SCENES_CONFIG = [
    {
        "title": "iPhone 17 Pro Max — Đáng Mua Không?",
        "narration": (
            "iPhone 17 Pro Max vừa ra mắt đã gây bão cộng đồng mạng. "
            "Với thiết kế titan hoàn toàn mới, chip A19 Pro, "
            "và khả năng chụp ảnh 48 mega-pixel tetra-prism, "
            "đây là chiếc iPhone đắt nhất lịch sử Apple "
            "với giá khởi điểm 1.399 đô la."
        ),
        "imageFile": "images/review_phone.jpg",
        "reactions": [
            {"emoji": "😱", "label": "Sốc giá", "count": 12400, "color": "#ef4444"},
            {"emoji": "🔥", "label": "Muốn mua", "count": 34500, "color": "#f59e0b"},
            {"emoji": "👏", "label": "Xứng đáng", "count": 21000, "color": "#10b981"},
            {"emoji": "😂", "label": "Thận đâu", "count": 8900, "color": "#3b82f6"},
        ],
        "duration": 14.0,
    },
    {
        "title": "Camera: Bước nhảy vọt hay marketing?",
        "narration": (
            "Camera chính 48 mega-pixel với ống kính tiềm vọng tetra-prism "
            "cho khả năng zoom quang học 10x. "
            "Nhiều reviewer nhận xét chất lượng ảnh chụp đêm "
            "vượt trội so với Samsung Galaxy S26 Ultra. "
            "Tuy nhiên, một số ý kiến cho rằng sự khác biệt "
            "không đáng với mức giá chênh lệch."
        ),
        "imageFile": "images/review_camera.jpg",
        "reactions": [
            {"emoji": "📸", "label": "Quá đẹp", "count": 28000, "color": "#10b981"},
            {"emoji": "🤔", "label": "Bình thường", "count": 15000, "color": "#f59e0b"},
            {"emoji": "💸", "label": "Đắt quá", "count": 9500, "color": "#ef4444"},
        ],
        "ratings": [
            {"label": "Chất lượng ảnh ngày", "value": 9.5, "maxValue": 10, "color": "#10b981"},
            {"label": "Chụp đêm", "value": 9.2, "maxValue": 10, "color": "#3b82f6"},
            {"label": "Zoom 10x", "value": 8.8, "maxValue": 10, "color": "#f59e0b"},
            {"label": "Video 4K Cinematic", "value": 9.7, "maxValue": 10, "color": "#8b5cf6"},
        ],
        "quote": "Camera này biến mọi người thành nhiếp ảnh gia chuyên nghiệp — không cần kỹ thuật, chỉ cần bấm",
        "quoteAuthor": "techreviewer_vn",
        "duration": 16.0,
    },
    {
        "title": "Thiết kế: Titan siêu nhẹ, siêu bền",
        "narration": (
            "Khung titan cấp 5 giúp iPhone 17 Pro Max nhẹ hơn "
            "20 gam so với thế hệ trước, trong khi độ bền tăng 30%. "
            "Viền siêu mỏng và màn hình micro-LED 120Hz Pro Motion "
            "mang đến trải nghiệm visual ấn tượng. "
            "Cộng đồng chia làm hai phe: số đông khen ngợi, "
            "nhưng một số cho rằng thiết kế quá giống iPhone 16."
        ),
        "imageFile": "images/review_design.jpg",
        "reactions": [
            {"emoji": "✨", "label": "Đẳng cấp", "count": 31000, "color": "#8b5cf6"},
            {"emoji": "😐", "label": "Giống cũ", "count": 18000, "color": "#6b7280"},
            {"emoji": "💪", "label": "Bền quá", "count": 12000, "color": "#10b981"},
        ],
        "quote": "Cầm trên tay nhẹ bất ngờ. Nhưng nếu bỏ ốp ra thì nhìn y hệt iPhone 16 Pro Max",
        "quoteAuthor": "gadget_lover_sg",
        "duration": 15.0,
    },
    {
        "title": "Pin: Cuối cùng cũng đủ dùng 2 ngày",
        "narration": (
            "Viên pin 4.685 mili-ampe-giờ cùng chip A19 Pro tiết kiệm năng lượng "
            "cho thời lượng sử dụng lên đến 33 giờ phát video liên tục. "
            "Sạc nhanh 45W đầy pin trong 80 phút. "
            "Đa số người dùng phấn khích vì lần đầu tiên "
            "iPhone thực sự dùng được trọn 2 ngày không cần sạc."
        ),
        "imageFile": "images/review_battery.jpg",
        "reactions": [
            {"emoji": "🔋", "label": "Pin trâu", "count": 42000, "color": "#10b981"},
            {"emoji": "⚡", "label": "Sạc nhanh", "count": 25000, "color": "#f59e0b"},
            {"emoji": "👎", "label": "Vẫn thua", "count": 5000, "color": "#ef4444"},
        ],
        "ratings": [
            {"label": "Thời lượng pin", "value": 9.0, "maxValue": 10, "color": "#10b981"},
            {"label": "Tốc độ sạc", "value": 7.5, "maxValue": 10, "color": "#f59e0b"},
            {"label": "Sạc không dây", "value": 8.0, "maxValue": 10, "color": "#3b82f6"},
        ],
        "quote": "Lần đầu tiên đi du lịch 2 ngày không mang sạc. Về nhà pin vẫn còn 15%. Sốc thật sự!",
        "quoteAuthor": "daily_tech_tips",
        "duration": 15.0,
    },
    {
        "title": "Kết luận: Có nên lên đời?",
        "narration": (
            "Tổng kết, iPhone 17 Pro Max là bản nâng cấp đáng giá "
            "nếu bạn đang dùng iPhone 14 hoặc cũ hơn. "
            "Với camera, pin, và hiệu năng đều ở mức top, "
            "đây xứng đáng là chiếc smartphone tốt nhất năm 2026. "
            "Tuy nhiên, nếu bạn đang dùng iPhone 16 Pro Max, "
            "sự khác biệt chưa đủ lớn để chi 1.400 đô la."
        ),
        "imageFile": "images/review_verdict.jpg",
        "reactions": [
            {"emoji": "🏆", "label": "Số 1", "count": 38000, "color": "#f59e0b"},
            {"emoji": "💰", "label": "Đáng tiền", "count": 22000, "color": "#10b981"},
            {"emoji": "⏳", "label": "Đợi 18", "count": 15000, "color": "#3b82f6"},
            {"emoji": "🤷", "label": "16 đủ rồi", "count": 20000, "color": "#6b7280"},
        ],
        "ratings": [
            {"label": "Tổng thể", "value": 9.2, "maxValue": 10, "color": "#f59e0b"},
            {"label": "Đáng đồng tiền", "value": 7.8, "maxValue": 10, "color": "#10b981"},
            {"label": "Nên lên đời?", "value": 8.0, "maxValue": 10, "color": "#8b5cf6"},
        ],
        "quote": "Nếu đang dùng 14 trở xuống thì PHẢI mua. Dùng 16 Pro thì... đợi iPhone 18 cũng được",
        "quoteAuthor": "vn_smartphone_review",
        "duration": 15.0,
    },
]


def create_script() -> VideoScript:
    scenes = [
        ScriptScene(
            scene_number=i + 1,
            title=cfg["title"],
            narration=cfg["narration"],
            visual_description="",
            duration_seconds=cfg["duration"],
        )
        for i, cfg in enumerate(SCENES_CONFIG)
    ]
    total = sum(s.duration_seconds for s in scenes)
    return VideoScript(
        title="Review iPhone 17 Pro Max — Cộng Đồng Nói Gì?",
        description="Tổng hợp review và reaction từ cộng đồng về iPhone 17 Pro Max",
        language="vi",
        scenes=scenes,
        tags=["review", "iphone", "reaction", "tech", "2026"],
        total_duration_seconds=total,
    )


async def generate_audio(script: VideoScript) -> list[str]:
    public_audio_dir = VIDEO_DIR / "public" / "audio"
    public_audio_dir.mkdir(parents=True, exist_ok=True)
    audio_files = []
    for i, scene in enumerate(script.scenes):
        print(f"  Audio scene {i+1}/{len(script.scenes)}: {scene.title}")
        audio_file, duration = await synthesize_edge_tts(
            text=scene.narration, language="vi", voice=MALE_VOICE,
        )
        filename = Path(audio_file).name
        public_path = public_audio_dir / filename
        shutil.copy2(audio_file, public_path)
        audio_files.append(f"audio/{filename}")
        scene.duration_seconds = max(scene.duration_seconds, duration + 2.0)
        print(f"    -> {duration:.1f}s")
    return audio_files


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("REACTION VIDEO — Review iPhone 17 Pro Max")
    print("=" * 60)

    script = create_script()
    audio_files = await generate_audio(script)

    subtitle_file = str(OUTPUT_DIR / "subtitles_reaction.srt")
    generate_srt(script, subtitle_file)
    subtitles = generate_subtitle_data(script)

    scenes_data = []
    for i, (scene, cfg) in enumerate(zip(script.scenes, SCENES_CONFIG)):
        scene_data: dict = {
            "sceneNumber": scene.scene_number,
            "title": scene.title,
            "narration": scene.narration,
            "durationInSeconds": scene.duration_seconds,
            "audioFile": audio_files[i] if i < len(audio_files) else "",
            "imageFile": cfg.get("imageFile", ""),
        }
        if "reactions" in cfg:
            scene_data["reactions"] = cfg["reactions"]
        if "ratings" in cfg:
            scene_data["ratings"] = cfg["ratings"]
        if "quote" in cfg:
            scene_data["quote"] = cfg["quote"]
        if "quoteAuthor" in cfg:
            scene_data["quoteAuthor"] = cfg["quoteAuthor"]
        scenes_data.append(scene_data)

    total_duration = sum(s.duration_seconds for s in script.scenes)

    props = {
        "title": script.title,
        "scenes": scenes_data,
        "subtitles": subtitles,
        "totalDurationInSeconds": total_duration,
        "backgroundColor": "#0a0a1e",
        "subtitleColor": "#ffffff",
        "accentColor": "#8b5cf6",
        "fontFamily": "Inter, system-ui, sans-serif",
        "language": "vi",
        "fps": 30,
        "width": 1920,
        "height": 1080,
    }

    props_file = str(OUTPUT_DIR / "video_props_reaction.json")
    with open(props_file, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    output_file = str(OUTPUT_DIR / "reaction_iphone17.mp4")
    print(f"\nRendering → {output_file}")

    result = subprocess.run(
        [
            "npx", "remotion", "render",
            "ReactionVideo",
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


if __name__ == "__main__":
    asyncio.run(main())
