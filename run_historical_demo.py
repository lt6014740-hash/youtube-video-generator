#!/usr/bin/env python3
"""
Historical / Educational Video — Template 2
Chu de: Phe Dong Minh da chien thang Phat xit Duc nhu the nao?
Format: 720x1280 (9:16 vertical — YouTube Shorts)
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


# ===== KICH BAN: PHE DONG MINH DA CHIEN THANG PHAT XIT DUC NHU THE NAO? =====
SCENES = [
    {
        "sceneNumber": 1,
        "title": "Phe Đồng Minh đã chiến\nthắng Phát xít Đức\nnhư thế nào?",
        "narration": (
            "Phe Đồng Minh đã chiến thắng Phát xít Đức như thế nào? "
            "Cùng tìm hiểu cuộc chiến khốc liệt nhất lịch sử nhân loại!"
        ),
        "year": "1939-1945",
        "icon": "⚔️",
        "bgColor": "#1a1a2e",
    },
    {
        "sceneNumber": 2,
        "title": "Hitler trỗi dậy\nvà bành trướng",
        "narration": (
            "Năm 1939, Hitler xâm lược Ba Lan, châm ngòi Thế chiến thứ hai. "
            "Đức Quốc Xã nhanh chóng chiếm Pháp, Bỉ, Hà Lan chỉ trong vài tuần. "
            "Cả châu Âu chìm trong bóng tối của chủ nghĩa phát xít."
        ),
        "year": "1939",
        "icon": "🇩🇪",
        "bgColor": "#4a2c2a",
        "facts": [
            "01/09/1939: Đức xâm lược Ba Lan",
            "Pháp thất thủ chỉ sau 6 tuần",
            "Chiến tranh chớp nhoáng Blitzkrieg",
        ],
    },
    {
        "sceneNumber": 3,
        "title": "Liên Xô tham chiến\nMặt trận phía Đông",
        "narration": (
            "Tháng 6 năm 1941, Hitler phát động chiến dịch Barbarossa tấn công Liên Xô. "
            "Nhưng mùa đông khắc nghiệt và sức kháng cự mãnh liệt của Hồng quân "
            "đã biến nước Nga thành mồ chôn quân Đức."
        ),
        "year": "1941",
        "icon": "❄️",
        "bgColor": "#2d4a3e",
        "facts": [
            "Chiến dịch Barbarossa: 4 triệu quân Đức",
            "Trận Stalingrad: bước ngoặt lịch sử",
            "Mùa đông Nga khiến quân Đức kiệt quệ",
        ],
    },
    {
        "sceneNumber": 4,
        "title": "Mỹ tham chiến\nsau trận Trân Châu Cảng",
        "narration": (
            "Ngày 7 tháng 12 năm 1941, Nhật Bản tấn công Trân Châu Cảng. "
            "Mỹ chính thức tham chiến, mang theo sức mạnh công nghiệp và quân sự khổng lồ. "
            "Phe Đồng Minh giờ đây có thêm một siêu cường."
        ),
        "year": "1941",
        "icon": "🇺🇸",
        "bgColor": "#1a3a5c",
        "facts": [
            "07/12/1941: Trân Châu Cảng bị tấn công",
            "Mỹ sản xuất 300.000 máy bay trong chiến tranh",
            "Viện trợ Lend-Lease cho Anh và Liên Xô",
        ],
    },
    {
        "sceneNumber": 5,
        "title": "Ý đầu hàng\nPhe Trục sụp đổ",
        "narration": (
            "Năm 1943, quân Đồng Minh đổ bộ vào Ý. "
            "Mussolini bị lật đổ, Ý đầu hàng và quay sang chống Đức. "
            "Phe Trục bắt đầu tan rã từ bên trong."
        ),
        "year": "1943",
        "icon": "🇮🇹",
        "bgColor": "#3d2d5c",
        "facts": [
            "07/1943: Đồng Minh đổ bộ Sicily",
            "Mussolini bị bắt và lật đổ",
            "Ý ký đình chiến với Đồng Minh",
        ],
    },
    {
        "sceneNumber": 6,
        "title": "D-Day: Đổ bộ Normandy\nNgày dài nhất",
        "narration": (
            "Ngày 6 tháng 6 năm 1944, hơn 150 ngàn quân Đồng Minh đổ bộ lên bờ biển Normandy. "
            "Đây là cuộc đổ bộ lớn nhất lịch sử, mở ra mặt trận phía Tây, "
            "ép Đức phải chiến đấu trên hai mặt trận."
        ),
        "year": "06/1944",
        "icon": "🏖️",
        "bgColor": "#2d4a3e",
        "facts": [
            "156.000 quân đổ bộ ngày đầu tiên",
            "5 bãi biển: Utah, Omaha, Gold, Juno, Sword",
            "Giải phóng Paris tháng 8/1944",
        ],
    },
    {
        "sceneNumber": 7,
        "title": "Hồng quân tiến về Berlin\nĐức bị kẹp hai mặt",
        "narration": (
            "Từ phía Đông, Hồng quân Liên Xô tiến như vũ bão về Berlin. "
            "Từ phía Tây, quân Đồng Minh vượt sông Rhine vào lãnh thổ Đức. "
            "Hitler bị kẹp giữa hai gọng kìm, không còn đường thoát."
        ),
        "year": "1945",
        "icon": "🔥",
        "bgColor": "#5c3d1a",
        "facts": [
            "Hồng quân: 6 triệu quân tiến về Berlin",
            "Đồng Minh vượt sông Rhine tháng 3/1945",
            "Đức bị tấn công từ mọi hướng",
        ],
    },
    {
        "sceneNumber": 8,
        "title": "Hitler tự sát\nĐức đầu hàng vô điều kiện",
        "narration": (
            "Ngày 30 tháng 4 năm 1945, Hitler tự sát trong hầm ngầm ở Berlin. "
            "Ngày 8 tháng 5, Đức Quốc Xã đầu hàng vô điều kiện. "
            "Thế chiến thứ hai tại châu Âu chính thức kết thúc!"
        ),
        "year": "08/05/1945",
        "icon": "🏳️",
        "bgColor": "#1a4a4a",
        "facts": [
            "30/04/1945: Hitler tự sát",
            "08/05/1945: Ngày Chiến thắng châu Âu (V-E Day)",
            "Hơn 60 triệu người thiệt mạng trong Thế chiến II",
        ],
    },
]


async def generate_audio(scenes: list[dict]) -> tuple[list[str], list[float]]:
    public_audio_dir = VIDEO_DIR / "public" / "audio"
    public_audio_dir.mkdir(parents=True, exist_ok=True)
    audio_files: list[str] = []
    durations: list[float] = []
    for i, scene in enumerate(scenes):
        print(f"  Audio scene {i+1}/{len(scenes)}: {scene['title'][:30]}...")
        audio_file, duration = await synthesize_edge_tts(
            text=scene["narration"],
            language="vi",
            voice=MALE_VOICE,
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
    print("  HISTORICAL VIDEO — Phe Dong Minh vs Phat xit Duc")
    print("  Template: HistoricalVideo (720x1280 — YouTube Shorts)")
    print("=" * 60)

    audio_files, durations = await generate_audio(SCENES)

    scenes_data = []
    for i, scene in enumerate(SCENES):
        dur = max(durations[i] + 1.5, 6.0)
        scenes_data.append({
            "sceneNumber": scene["sceneNumber"],
            "title": scene["title"],
            "narration": scene["narration"],
            "durationInSeconds": dur,
            "audioFile": audio_files[i],
            "year": scene.get("year", ""),
            "icon": scene.get("icon", ""),
            "bgColor": scene.get("bgColor", ""),
            "facts": scene.get("facts", []),
        })

    total_duration = sum(s["durationInSeconds"] for s in scenes_data)

    bgm_path = VIDEO_DIR / "public" / "audio" / "background-music.mp3"
    has_bgm = bgm_path.exists()

    props = {
        "title": "Phe \u0110\u1ed3ng Minh \u0111\u00e3 chi\u1ebfn th\u1eafng Ph\u00e1t x\u00edt \u0110\u1ee9c nh\u01b0 th\u1ebf n\u00e0o?",
        "scenes": scenes_data,
        "totalDurationInSeconds": total_duration,
        "channelName": "Ki\u1ebfn Th\u1ee9c Hay",
        "fps": 30,
        "width": 720,
        "height": 1280,
    }

    if has_bgm:
        props["backgroundMusic"] = "audio/background-music.mp3"
        props["backgroundMusicVolume"] = 0.12

    props_file = str(OUTPUT_DIR / "video_props_historical.json")
    with open(props_file, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    output_file = str(OUTPUT_DIR / "historical_ww2.mp4")
    print(f"\nRendering -> {output_file}")
    print(f"So scene: {len(scenes_data)}")
    print(f"Tong thoi luong: {total_duration:.1f}s")
    print(f"Background music: {'Co' if has_bgm else 'Khong'}")

    result = subprocess.run(
        [
            "npx", "remotion", "render",
            "HistoricalVideo",
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

    print(f"\n{'=' * 60}")
    print(f"  VIDEO HOAN THANH!")
    print(f"  File: {output_file}")
    print(f"  So scene: {len(scenes_data)}")
    print(f"  Thoi luong: {total_duration:.1f}s")
    print(f"  Format: 720x1280 (9:16 YouTube Shorts)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
