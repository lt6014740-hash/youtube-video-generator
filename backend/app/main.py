import json
import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .schemas import (
    GenerateScriptRequest,
    GenerateScriptResponse,
    GenerateVideoRequest,
    GenerateVideoResponse,
    PipelineRequest,
    PipelineResponse,
    TTSRequest,
    TTSResponse,
)
from .script_generator import generate_script
from .subtitle_generator import generate_srt
from .tts_service import synthesize
from .video_renderer import render_video

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Video Generator API",
    description="AI-powered multilingual YouTube video generator",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists(settings.output_dir):
    app.mount("/output", StaticFiles(directory=settings.output_dir), name="output")


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "tts_engine": settings.tts_engine,
        "deepseek_configured": bool(settings.deepseek_api_key),
    }


@app.post("/api/generate-script", response_model=GenerateScriptResponse)
async def api_generate_script(request: GenerateScriptRequest):
    try:
        script = await generate_script(request)

        script_file = os.path.join(
            settings.scripts_dir,
            f"script_{script.language}_{len(os.listdir(settings.scripts_dir))}.json",
        )
        with open(script_file, "w", encoding="utf-8") as f:
            json.dump(script.model_dump(), f, ensure_ascii=False, indent=2)

        return GenerateScriptResponse(script=script, script_file=script_file)
    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-tts", response_model=TTSResponse)
async def api_generate_tts(request: TTSRequest):
    try:
        audio_file, duration = await synthesize(
            text=request.text,
            language=request.language,
            voice=request.voice,
            speed=request.speed,
        )
        return TTSResponse(audio_file=audio_file, duration_seconds=duration)
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-video", response_model=GenerateVideoResponse)
async def api_generate_video(request: GenerateVideoRequest):
    try:
        video_file, duration = await render_video(
            script=request.script,
            audio_files=request.audio_files,
            request=request,
        )
        return GenerateVideoResponse(
            video_file=video_file,
            duration_seconds=duration,
            resolution=f"{settings.video_width}x{settings.video_height}",
        )
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pipeline", response_model=PipelineResponse)
async def api_pipeline(request: PipelineRequest):
    try:
        logger.info(f"Starting pipeline for topic: {request.topic}")

        # Step 1: Generate script
        logger.info("Step 1: Generating script with DeepSeek...")
        script_request = GenerateScriptRequest(
            topic=request.topic,
            language=request.language,
            duration=request.duration,
            style=request.style,
            additional_instructions=request.additional_instructions,
        )
        script = await generate_script(script_request)
        logger.info(f"Script generated: {script.title} ({len(script.scenes)} scenes)")

        # Step 2: Generate TTS for each scene
        logger.info("Step 2: Generating audio with TTS...")
        audio_files = []
        for i, scene in enumerate(script.scenes):
            logger.info(f"  Generating audio for scene {i + 1}/{len(script.scenes)}...")
            audio_file, duration = await synthesize(
                text=scene.narration,
                language=script.language,
            )
            audio_files.append(audio_file)
            scene.duration_seconds = max(scene.duration_seconds, duration)

        # Step 3: Generate subtitles
        logger.info("Step 3: Generating subtitles...")
        subtitle_file = os.path.join(settings.output_dir, "subtitles.srt")
        generate_srt(script, subtitle_file)

        # Step 4: Render video
        logger.info("Step 4: Rendering video with Remotion...")
        video_request = GenerateVideoRequest(
            script=script,
            audio_files=audio_files,
            background_color=request.background_color,
            subtitle_color=request.subtitle_color,
            accent_color=request.accent_color,
        )
        video_file, _ = await render_video(script, audio_files, video_request)

        logger.info(f"Pipeline complete! Video: {video_file}")

        return PipelineResponse(
            script=script,
            audio_files=audio_files,
            video_file=video_file,
            subtitle_file=subtitle_file,
        )
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(settings.output_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)
