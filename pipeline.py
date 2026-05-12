#!/usr/bin/env python3
"""
YouTube Video Generator Pipeline CLI

Usage:
    python pipeline.py --topic "Your topic" --language en --duration short
    python pipeline.py --topic "Hướng dẫn Python" --language vi --duration medium
    python pipeline.py --topic "AI入門" --language ja --duration short
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.app.config import settings
from backend.app.schemas import GenerateScriptRequest, VideoScript
from backend.app.script_generator import generate_script
from backend.app.subtitle_generator import generate_srt, generate_subtitle_data
from backend.app.tts_service import synthesize

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent
VIDEO_DIR = PROJECT_ROOT / "video"
OUTPUT_DIR = PROJECT_ROOT / "output"


async def step_generate_script(
    topic: str,
    language: str,
    duration: str,
    style: str,
    additional_instructions: str = "",
) -> VideoScript:
    logger.info("=" * 60)
    logger.info("STEP 1: Generating script with DeepSeek AI")
    logger.info("=" * 60)

    request = GenerateScriptRequest(
        topic=topic,
        language=language,
        duration=duration,
        style=style,
        additional_instructions=additional_instructions,
    )

    script = await generate_script(request)

    script_file = OUTPUT_DIR / "scripts" / f"script_{language}.json"
    script_file.parent.mkdir(parents=True, exist_ok=True)
    with open(script_file, "w", encoding="utf-8") as f:
        json.dump(script.model_dump(), f, ensure_ascii=False, indent=2)

    logger.info(f"Title: {script.title}")
    logger.info(f"Scenes: {len(script.scenes)}")
    logger.info(f"Total duration: {script.total_duration_seconds}s")
    logger.info(f"Script saved: {script_file}")

    return script


async def step_generate_audio(script: VideoScript) -> list[str]:
    logger.info("=" * 60)
    logger.info("STEP 2: Generating audio with TTS")
    logger.info(f"Engine: {settings.tts_engine}")
    logger.info("=" * 60)

    audio_files = []
    for i, scene in enumerate(script.scenes):
        logger.info(f"  Scene {i + 1}/{len(script.scenes)}: {scene.title}")
        audio_file, duration = await synthesize(
            text=scene.narration,
            language=script.language,
        )
        audio_files.append(audio_file)
        scene.duration_seconds = max(scene.duration_seconds, duration)
        logger.info(f"    Audio: {audio_file} ({duration:.1f}s)")

    return audio_files


def step_generate_subtitles(script: VideoScript) -> str:
    logger.info("=" * 60)
    logger.info("STEP 3: Generating subtitles")
    logger.info("=" * 60)

    subtitle_file = str(OUTPUT_DIR / "subtitles.srt")
    generate_srt(script, subtitle_file)
    logger.info(f"Subtitles saved: {subtitle_file}")

    return subtitle_file


def step_render_video(
    script: VideoScript,
    audio_files: list[str],
    background_color: str = "#1a1a2e",
    subtitle_color: str = "#ffffff",
    accent_color: str = "#e94560",
) -> str:
    logger.info("=" * 60)
    logger.info("STEP 4: Rendering video with Remotion")
    logger.info("=" * 60)

    subtitles = generate_subtitle_data(script)

    scenes_data = []
    for i, scene in enumerate(script.scenes):
        scenes_data.append(
            {
                "sceneNumber": scene.scene_number,
                "title": scene.title,
                "narration": scene.narration,
                "visualDescription": scene.visual_description,
                "durationInSeconds": scene.duration_seconds,
                "audioFile": audio_files[i] if i < len(audio_files) else "",
            }
        )

    total_duration = sum(s.duration_seconds for s in script.scenes)

    props = {
        "title": script.title,
        "scenes": scenes_data,
        "subtitles": subtitles,
        "totalDurationInSeconds": total_duration,
        "backgroundColor": background_color,
        "subtitleColor": subtitle_color,
        "accentColor": accent_color,
        "fontFamily": "Inter, system-ui, sans-serif",
        "language": script.language,
        "fps": settings.video_fps,
        "width": settings.video_width,
        "height": settings.video_height,
    }

    props_file = str(OUTPUT_DIR / "video_props.json")
    with open(props_file, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    output_file = str(OUTPUT_DIR / f"video_{script.language}.mp4")

    logger.info(f"Props: {props_file}")
    logger.info(f"Output: {output_file}")
    logger.info("Running Remotion render...")

    result = subprocess.run(
        [
            "npx",
            "remotion",
            "render",
            "YouTubeVideo",
            "--props",
            props_file,
            "--output",
            output_file,
            "--codec",
            "h264",
        ],
        cwd=str(VIDEO_DIR),
        capture_output=True,
        text=True,
        timeout=600,
    )

    if result.returncode != 0:
        logger.error(f"Render error: {result.stderr}")
        raise RuntimeError(f"Video rendering failed: {result.stderr}")

    logger.info(f"Video rendered: {output_file}")
    return output_file


async def run_pipeline(args: argparse.Namespace) -> None:
    logger.info("=" * 60)
    logger.info("YouTube Video Generator Pipeline")
    logger.info("=" * 60)
    logger.info(f"Topic: {args.topic}")
    logger.info(f"Language: {args.language}")
    logger.info(f"Duration: {args.duration}")
    logger.info(f"Style: {args.style}")
    logger.info("")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Generate script
    script = await step_generate_script(
        topic=args.topic,
        language=args.language,
        duration=args.duration,
        style=args.style,
        additional_instructions=args.instructions,
    )

    # Step 2: Generate audio
    audio_files = await step_generate_audio(script)

    # Step 3: Generate subtitles
    subtitle_file = step_generate_subtitles(script)

    # Step 4: Render video (optional - requires Remotion setup)
    if args.skip_video:
        logger.info("Skipping video rendering (--skip-video)")
        video_file = ""
    else:
        try:
            video_file = step_render_video(
                script,
                audio_files,
                background_color=args.bg_color,
                subtitle_color=args.sub_color,
                accent_color=args.accent_color,
            )
        except Exception as e:
            logger.warning(f"Video rendering failed: {e}")
            logger.warning("You can re-render later with the props file in output/")
            video_file = ""

    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Script: output/scripts/script_{args.language}.json")
    logger.info(f"Audio files: {len(audio_files)} files in output/audio/")
    logger.info(f"Subtitles: {subtitle_file}")
    if video_file:
        logger.info(f"Video: {video_file}")
    logger.info("")
    logger.info("Upload to YouTube and enjoy! 🎬")


def main():
    parser = argparse.ArgumentParser(
        description="AI-powered YouTube Video Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py --topic "Python Tutorial for Beginners" --language en
  python pipeline.py --topic "Hướng dẫn lập trình Python" --language vi --duration medium
  python pipeline.py --topic "AI入門ガイド" --language ja --style educational
  python pipeline.py --topic "한국어 학습" --language ko --skip-video
        """,
    )

    parser.add_argument("--topic", required=True, help="Video topic or idea")
    parser.add_argument(
        "--language",
        default="en",
        choices=["en", "vi", "zh", "ja", "ko", "fr", "de", "es", "th", "id"],
        help="Target language (default: en)",
    )
    parser.add_argument(
        "--duration",
        default="short",
        choices=["short", "medium", "long"],
        help="Video duration (default: short)",
    )
    parser.add_argument(
        "--style",
        default="educational",
        choices=["educational", "storytelling", "tutorial", "news", "entertainment"],
        help="Video style (default: educational)",
    )
    parser.add_argument("--instructions", default="", help="Additional instructions for AI")
    parser.add_argument("--skip-video", action="store_true", help="Skip video rendering")
    parser.add_argument("--bg-color", default="#1a1a2e", help="Background color")
    parser.add_argument("--sub-color", default="#ffffff", help="Subtitle color")
    parser.add_argument("--accent-color", default="#e94560", help="Accent color")

    args = parser.parse_args()

    if not os.environ.get("DEEPSEEK_API_KEY") and not settings.deepseek_api_key:
        print("Error: DEEPSEEK_API_KEY environment variable is required.")
        print("Get your API key at: https://platform.deepseek.com/api_keys")
        sys.exit(1)

    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()
