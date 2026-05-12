import json
import logging
import os
import subprocess
import uuid
from pathlib import Path

from .config import settings
from .schemas import GenerateVideoRequest, VideoScript
from .subtitle_generator import generate_subtitle_data

logger = logging.getLogger(__name__)

VIDEO_DIR = Path(__file__).parent.parent.parent / "video"


def prepare_video_props(
    script: VideoScript,
    audio_files: list[str],
    request: GenerateVideoRequest,
) -> dict:
    scenes = []
    for i, scene in enumerate(script.scenes):
        scene_data = {
            "sceneNumber": scene.scene_number,
            "title": scene.title,
            "narration": scene.narration,
            "visualDescription": scene.visual_description,
            "durationInSeconds": scene.duration_seconds,
            "audioFile": audio_files[i] if i < len(audio_files) else "",
        }
        scenes.append(scene_data)

    subtitles = generate_subtitle_data(script)

    total_duration = sum(s.duration_seconds for s in script.scenes)

    return {
        "title": script.title,
        "scenes": scenes,
        "subtitles": subtitles,
        "totalDurationInSeconds": total_duration,
        "backgroundColor": request.background_color,
        "subtitleColor": request.subtitle_color,
        "accentColor": request.accent_color,
        "fontFamily": request.font_family,
        "language": script.language,
        "fps": settings.video_fps,
        "width": settings.video_width,
        "height": settings.video_height,
    }


async def render_video(
    script: VideoScript,
    audio_files: list[str],
    request: GenerateVideoRequest,
) -> tuple[str, float]:
    output_filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(settings.output_dir, output_filename)

    props = prepare_video_props(script, audio_files, request)

    props_file = os.path.join(settings.output_dir, f"props_{uuid.uuid4()}.json")
    with open(props_file, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)

    try:
        result = subprocess.run(
            [
                "npx",
                "remotion",
                "render",
                "YouTubeVideo",
                "--props",
                props_file,
                "--output",
                output_path,
                "--codec",
                "h264",
            ],
            cwd=str(VIDEO_DIR),
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            logger.error(f"Remotion render error: {result.stderr}")
            raise RuntimeError(f"Video rendering failed: {result.stderr}")

        logger.info(f"Video rendered successfully: {output_path}")

    finally:
        if os.path.exists(props_file):
            os.remove(props_file)

    total_duration = sum(s.duration_seconds for s in script.scenes)

    return output_path, total_duration
