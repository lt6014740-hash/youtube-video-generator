import logging
import os
import uuid

import edge_tts

from .config import settings

logger = logging.getLogger(__name__)

EDGE_TTS_VOICES = {
    "en": "en-US-AriaNeural",
    "vi": "vi-VN-HoaiMyNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "es": "es-ES-ElviraNeural",
    "th": "th-TH-PremwadeeNeural",
    "id": "id-ID-GadisNeural",
}

EDGE_TTS_MALE_VOICES = {
    "en": "en-US-GuyNeural",
    "vi": "vi-VN-NamMinhNeural",
    "zh": "zh-CN-YunxiNeural",
    "ja": "ja-JP-KeitaNeural",
    "ko": "ko-KR-InJoonNeural",
    "fr": "fr-FR-HenriNeural",
    "de": "de-DE-ConradNeural",
    "es": "es-ES-AlvaroNeural",
    "th": "th-TH-NiwatNeural",
    "id": "id-ID-ArdiNeural",
}


async def synthesize_edge_tts(
    text: str,
    language: str = "en",
    voice: str = "",
    speed: float = 1.0,
    output_path: str = "",
) -> tuple[str, float]:
    if not voice:
        voice = EDGE_TTS_VOICES.get(language, "en-US-AriaNeural")

    if not output_path:
        output_path = os.path.join(settings.audio_dir, f"{uuid.uuid4()}.mp3")

    rate_str = f"{int((speed - 1) * 100):+d}%"

    communicate = edge_tts.Communicate(text, voice, rate=rate_str)
    await communicate.save(output_path)

    duration = await _get_audio_duration(output_path)
    logger.info(f"Edge-TTS: Generated audio ({duration:.1f}s) -> {output_path}")

    return output_path, duration


async def synthesize_f5_tts(
    text: str,
    language: str = "en",
    ref_audio: str = "",
    ref_text: str = "",
    output_path: str = "",
) -> tuple[str, float]:
    try:
        from f5_tts.api import F5TTS
    except ImportError:
        raise ImportError(
            "F5-TTS is not installed. Install with: pip install f5-tts\n"
            "Or use edge-tts engine by setting TTS_ENGINE=edge-tts"
        )

    if not output_path:
        output_path = os.path.join(settings.audio_dir, f"{uuid.uuid4()}.wav")

    if not ref_audio:
        ref_audio = settings.f5_ref_audio
    if not ref_text:
        ref_text = settings.f5_ref_text

    if not ref_audio:
        raise ValueError(
            "F5-TTS requires a reference audio file. "
            "Set F5_REF_AUDIO environment variable or provide ref_audio parameter."
        )

    model = F5TTS(model=settings.f5_model)
    wav, sr, _ = model.infer(
        ref_file=ref_audio,
        ref_text=ref_text,
        gen_text=text,
        file_wave=output_path,
    )

    duration = len(wav) / sr
    logger.info(f"F5-TTS: Generated audio ({duration:.1f}s) -> {output_path}")

    return output_path, duration


async def synthesize(
    text: str,
    language: str = "en",
    voice: str = "",
    speed: float = 1.0,
    output_path: str = "",
) -> tuple[str, float]:
    if settings.tts_engine == "f5-tts":
        return await synthesize_f5_tts(
            text=text,
            language=language,
            output_path=output_path,
        )
    else:
        return await synthesize_edge_tts(
            text=text,
            language=language,
            voice=voice,
            speed=speed,
            output_path=output_path,
        )


async def _get_audio_duration(file_path: str) -> float:
    try:
        from mutagen.mp3 import MP3

        audio = MP3(file_path)
        return audio.info.length
    except ImportError:
        pass

    try:
        import subprocess

        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                file_path,
            ],
            capture_output=True,
            text=True,
        )
        return float(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError):
        return 10.0
