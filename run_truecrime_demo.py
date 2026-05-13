#!/usr/bin/env python3
"""
Demo: True Crime video — Vụ án lừa đảo tiền điện tử lớn nhất Việt Nam.
Uses Edge-TTS male voice + TrueCrimeVideo Remotion composition.
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
        "title": "Bối cảnh: Sàn giao dịch BitConnect",
        "narration": (
            "Năm 2016, sàn giao dịch tiền điện tử BitConnect ra đời, "
            "hứa hẹn mức lợi nhuận lên đến 40% mỗi tháng thông qua "
            "công nghệ bot giao dịch tự động. Hàng triệu nhà đầu tư "
            "trên toàn thế giới, bao gồm nhiều người Việt Nam, "
            "đã đổ tiền vào nền tảng này với hy vọng đổi đời."
        ),
        "phase": "BỐI CẢNH",
        "imageFile": "images/court_bg.jpg",
        "evidence": "BitConnect cam kết lợi nhuận 40%/tháng — một dấu hiệu rõ ràng của mô hình Ponzi",
        "evidenceLabel": "DẤU HIỆU",
        "duration": 16.0,
    },
    {
        "title": "Diễn biến: Dòng tiền 2,4 tỷ USD",
        "narration": (
            "Trong hai năm hoạt động, BitConnect đã huy động được "
            "hơn 2,4 tỷ đô la từ các nhà đầu tư. "
            "Hệ thống hoạt động theo mô hình đa cấp, "
            "người giới thiệu nhận hoa hồng từ các tầng dưới. "
            "Nhiều đại lý tại Việt Nam tổ chức hội thảo quy mô lớn "
            "để chiêu mộ nạn nhân mới."
        ),
        "phase": "DIỄN BIẾN",
        "imageFile": "images/crime_scene.jpg",
        "evidence": "2,4 tỷ USD huy động từ nhà đầu tư toàn cầu — mô hình đa cấp kinh điển",
        "evidenceLabel": "QUY MÔ",
        "duration": 15.0,
    },
    {
        "title": "Sụp đổ: Sàn đóng cửa một sớm một chiều",
        "narration": (
            "Tháng 1 năm 2018, BitConnect bất ngờ thông báo đóng cửa "
            "sàn giao dịch cho vay. Đồng BCC từ mức 430 đô la "
            "rơi xuống dưới 1 đô la chỉ trong vài giờ. "
            "Hàng triệu nhà đầu tư mất trắng, "
            "nhiều người mất toàn bộ tiền tiết kiệm."
        ),
        "phase": "DIỄN BIẾN",
        "imageFile": "images/prison.jpg",
        "evidence": "Đồng BCC giảm từ $430 xuống dưới $1 trong vài giờ — nhà đầu tư mất trắng",
        "evidenceLabel": "HẬU QUẢ",
        "duration": 14.0,
    },
    {
        "title": "Phiên tòa: Bản án 38 năm tù",
        "narration": (
            "Năm 2024, người sáng lập BitConnect, Satish Kumbhani, "
            "bị tòa án Hoa Kỳ tuyên phạt 38 năm tù giam "
            "vì tội lừa đảo và rửa tiền. "
            "Đây là một trong những bản án nặng nhất "
            "trong lịch sử lừa đảo tiền điện tử."
        ),
        "phase": "PHÁN QUYẾT",
        "imageFile": "images/gavel.jpg",
        "evidence": "38 năm tù — bản án nặng nhất trong lịch sử lừa đảo crypto",
        "evidenceLabel": "PHÁN QUYẾT",
        "duration": 13.0,
    },
    {
        "title": "Bài học: Nhận diện lừa đảo tiền điện tử",
        "narration": (
            "Vụ BitConnect để lại bài học đắt giá: "
            "Không có khoản đầu tư nào đảm bảo lợi nhuận cao mà không có rủi ro. "
            "Hãy cảnh giác với các dấu hiệu như "
            "cam kết lợi nhuận cố định, mô hình giới thiệu nhiều tầng, "
            "và áp lực mua ngay kẻo hết. "
            "Luôn kiểm tra thông tin trước khi đầu tư."
        ),
        "phase": "BÀI HỌC",
        "imageFile": "images/justice.jpg",
        "evidence": "Dấu hiệu nhận diện: lợi nhuận phi thực tế, mô hình đa cấp, áp lực thời gian",
        "evidenceLabel": "CẢNH BÁO",
        "duration": 16.0,
    },
]

TIMELINE_EVENTS = [
    {"time": "2016", "label": "BitConnect ra đời", "icon": "📍"},
    {"time": "2016–2018", "label": "Huy động $2.4B", "icon": "💰"},
    {"time": "01/2018", "label": "Sàn sụp đổ", "icon": "💥"},
    {"time": "2024", "label": "Phiên tòa", "icon": "⚖️"},
    {"time": "Hiện tại", "label": "Bài học rút ra", "icon": "📖"},
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
        title="Vụ Lừa Đảo BitConnect — 2.4 Tỷ USD Bay Hơi",
        description="Phân tích vụ án lừa đảo tiền điện tử lớn nhất lịch sử",
        language="vi",
        scenes=scenes,
        tags=["true crime", "lừa đảo", "bitconnect", "crypto", "pháp luật"],
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
    print("TRUE CRIME VIDEO — Vụ lừa đảo BitConnect")
    print("=" * 60)

    script = create_script()
    audio_files = await generate_audio(script)

    subtitle_file = str(OUTPUT_DIR / "subtitles_truecrime.srt")
    generate_srt(script, subtitle_file)
    subtitles = generate_subtitle_data(script)

    scenes_data = []
    for i, (scene, cfg) in enumerate(zip(script.scenes, SCENES_CONFIG)):
        scenes_data.append({
            "sceneNumber": scene.scene_number,
            "title": scene.title,
            "narration": scene.narration,
            "durationInSeconds": scene.duration_seconds,
            "audioFile": audio_files[i] if i < len(audio_files) else "",
            "imageFile": cfg.get("imageFile", ""),
            "phase": cfg.get("phase", ""),
            "evidence": cfg.get("evidence", ""),
            "evidenceLabel": cfg.get("evidenceLabel", ""),
        })

    total_duration = sum(s.duration_seconds for s in script.scenes)

    props = {
        "title": script.title,
        "scenes": scenes_data,
        "subtitles": subtitles,
        "timelineEvents": TIMELINE_EVENTS,
        "totalDurationInSeconds": total_duration,
        "backgroundColor": "#0a0a0a",
        "subtitleColor": "#ffffff",
        "accentColor": "#ef4444",
        "fontFamily": "Inter, system-ui, sans-serif",
        "language": "vi",
        "fps": 30,
        "width": 1920,
        "height": 1080,
    }

    props_file = str(OUTPUT_DIR / "video_props_truecrime.json")
    with open(props_file, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    output_file = str(OUTPUT_DIR / "truecrime_bitconnect.mp4")
    print(f"\nRendering → {output_file}")

    result = subprocess.run(
        [
            "npx", "remotion", "render",
            "TrueCrimeVideo",
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
