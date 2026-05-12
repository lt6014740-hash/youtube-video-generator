#!/usr/bin/env python3
"""
Generate a Vietnamese news video without DeepSeek API.
Uses a manually written script about today's notable events in Vietnam.
"""

import asyncio
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.app.schemas import ScriptScene, VideoScript
from backend.app.subtitle_generator import generate_srt, generate_subtitle_data
from backend.app.tts_service import synthesize_edge_tts

OUTPUT_DIR = Path(__file__).parent / "output"
VIDEO_DIR = Path(__file__).parent / "video"


def create_script() -> VideoScript:
    scenes = [
        ScriptScene(
            scene_number=1,
            title="Đại hội MTTQ Việt Nam",
            narration=(
                "Ngày 12 tháng 5 năm 2026, Đại hội đại biểu toàn quốc "
                "Mặt trận Tổ quốc Việt Nam lần thứ 11, nhiệm kỳ 2026 đến 2031 "
                "khai mạc trọng thể tại Hà Nội. Đây là sự kiện chính trị xã hội "
                "quan trọng, đánh dấu bước phát triển mới trong việc "
                "phát huy sức mạnh đại đoàn kết toàn dân tộc."
            ),
            visual_description="Hội trường lớn với cờ đỏ sao vàng",
            duration_seconds=12.0,
        ),
        ScriptScene(
            scene_number=2,
            title="Giá vàng tăng mạnh",
            narration=(
                "Giá vàng hôm nay bật tăng mạnh tới 1,8 triệu đồng mỗi lượng, "
                "đưa giá vàng miếng SJC quay lại mốc 167 triệu đồng mỗi lượng "
                "ở chiều bán ra. Trong khi đó, giá vàng thế giới "
                "vẫn duy trì trên mốc 4.700 đô la Mỹ mỗi ounce, "
                "cho thấy xu hướng tăng giá vẫn tiếp diễn."
            ),
            visual_description="Biểu đồ giá vàng tăng mạnh",
            duration_seconds=12.0,
        ),
        ScriptScene(
            scene_number=3,
            title="Doanh nghiệp UAV Việt Nam",
            narration=(
                "Ba doanh nghiệp công nghệ máy bay không người lái Việt Nam "
                "đang tham gia triển lãm XPONENTIAL 2026 tại Detroit, Hoa Kỳ. "
                "Đây là lần tham gia lớn nhất của Việt Nam "
                "tại triển lãm hàng đầu thế giới về công nghệ tự hành, "
                "khẳng định vị thế ngày càng lớn của Việt Nam "
                "trên bản đồ công nghệ toàn cầu."
            ),
            visual_description="Triển lãm công nghệ drone hiện đại",
            duration_seconds=12.0,
        ),
        ScriptScene(
            scene_number=4,
            title="An ninh mạng cho doanh nghiệp",
            narration=(
                "Chính phủ kêu gọi các doanh nghiệp vừa và nhỏ "
                "tăng cường an ninh mạng trong quá trình chuyển đổi số. "
                "Với hơn 800 nghìn doanh nghiệp đang hoạt động, "
                "Việt Nam đặt mục tiêu hỗ trợ ít nhất 500 nghìn doanh nghiệp "
                "ứng dụng công nghệ số và trí tuệ nhân tạo "
                "trong giai đoạn 2026 đến 2030."
            ),
            visual_description="Biểu tượng bảo mật mạng và dữ liệu số",
            duration_seconds=12.0,
        ),
        ScriptScene(
            scene_number=5,
            title="Việt Nam và ASEAN",
            narration=(
                "Thủ tướng Chính phủ phê duyệt Chương trình hành động "
                "thực hiện Kế hoạch chiến lược Cộng đồng Kinh tế ASEAN "
                "tại Việt Nam giai đoạn 2026 đến 2035. "
                "Chương trình nhằm nâng cao vai trò, vị thế "
                "của Việt Nam trong khối ASEAN, "
                "hướng tới tầm nhìn cộng đồng ASEAN 2045."
            ),
            visual_description="Cờ các nước ASEAN và hội nghị quốc tế",
            duration_seconds=12.0,
        ),
    ]

    total_duration = sum(s.duration_seconds for s in scenes)

    return VideoScript(
        title="Tin tức Việt Nam hôm nay 12/5/2026",
        description="Cập nhật 5 sự kiện nổi bật nhất trong ngày 12 tháng 5 năm 2026",
        language="vi",
        scenes=scenes,
        tags=["tin tức", "Việt Nam", "thời sự", "2026"],
        total_duration_seconds=total_duration,
    )


async def generate_audio(script: VideoScript) -> list[str]:
    public_audio_dir = VIDEO_DIR / "public" / "audio"
    public_audio_dir.mkdir(parents=True, exist_ok=True)

    audio_files = []
    for i, scene in enumerate(script.scenes):
        print(f"  Tạo audio scene {i+1}/{len(script.scenes)}: {scene.title}")
        audio_file, duration = await synthesize_edge_tts(
            text=scene.narration,
            language="vi",
        )
        # Copy to video/public/audio/ for Remotion staticFile()
        filename = Path(audio_file).name
        public_path = public_audio_dir / filename
        shutil.copy2(audio_file, public_path)
        # Use relative path for staticFile()
        audio_files.append(f"audio/{filename}")
        scene.duration_seconds = max(scene.duration_seconds, duration + 2.0)
        print(f"    -> {public_path} ({duration:.1f}s)")
    return audio_files


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Create script
    print("=" * 60)
    print("BƯỚC 1: Tạo kịch bản tin tức Việt Nam")
    print("=" * 60)
    script = create_script()
    print(f"Tiêu đề: {script.title}")
    print(f"Số scene: {len(script.scenes)}")

    # Save script
    script_file = OUTPUT_DIR / "scripts" / "script_vi.json"
    script_file.parent.mkdir(parents=True, exist_ok=True)
    with open(script_file, "w", encoding="utf-8") as f:
        json.dump(script.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"Script lưu tại: {script_file}")

    # Step 2: Generate audio
    print("\n" + "=" * 60)
    print("BƯỚC 2: Tạo giọng đọc bằng Edge-TTS")
    print("=" * 60)
    audio_files = await generate_audio(script)

    # Step 3: Generate subtitles
    print("\n" + "=" * 60)
    print("BƯỚC 3: Tạo phụ đề")
    print("=" * 60)
    subtitle_file = str(OUTPUT_DIR / "subtitles.srt")
    generate_srt(script, subtitle_file)
    print(f"Phụ đề lưu tại: {subtitle_file}")

    # Step 4: Prepare Remotion props
    print("\n" + "=" * 60)
    print("BƯỚC 4: Chuẩn bị render video")
    print("=" * 60)
    subtitles = generate_subtitle_data(script)

    scenes_data = []
    for i, scene in enumerate(script.scenes):
        scenes_data.append({
            "sceneNumber": scene.scene_number,
            "title": scene.title,
            "narration": scene.narration,
            "visualDescription": scene.visual_description,
            "durationInSeconds": scene.duration_seconds,
            "audioFile": audio_files[i] if i < len(audio_files) else "",
        })

    total_duration = sum(s.duration_seconds for s in script.scenes)

    props = {
        "title": script.title,
        "scenes": scenes_data,
        "subtitles": subtitles,
        "totalDurationInSeconds": total_duration,
        "backgroundColor": "#0f0f23",
        "subtitleColor": "#ffffff",
        "accentColor": "#dc2626",
        "fontFamily": "Inter, system-ui, sans-serif",
        "language": "vi",
        "fps": 30,
        "width": 1920,
        "height": 1080,
    }

    props_file = str(OUTPUT_DIR / "video_props.json")
    with open(props_file, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)
    print(f"Props lưu tại: {props_file}")

    # Step 5: Render with Remotion
    print("\n" + "=" * 60)
    print("BƯỚC 5: Render video bằng Remotion")
    print("=" * 60)
    output_file = str(OUTPUT_DIR / "tin_tuc_vietnam_12_05_2026.mp4")
    print(f"Output: {output_file}")
    print("Đang render... (có thể mất vài phút)")

    import subprocess
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

    # Summary
    print("\n" + "=" * 60)
    print("HOÀN THÀNH!")
    print("=" * 60)
    print(f"Script: {script_file}")
    print(f"Audio: {len(audio_files)} files")
    print(f"Phụ đề: {subtitle_file}")
    print(f"Video: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
