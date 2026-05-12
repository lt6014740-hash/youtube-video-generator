import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    tts_engine: str = "edge-tts"  # "edge-tts" or "f5-tts"

    # F5-TTS settings
    f5_model: str = "F5TTS_v1_Base"
    f5_ref_audio: str = ""
    f5_ref_text: str = ""

    # Output settings
    output_dir: str = str(Path(__file__).parent.parent.parent / "output")
    audio_dir: str = str(Path(__file__).parent.parent.parent / "output" / "audio")
    scripts_dir: str = str(Path(__file__).parent.parent.parent / "output" / "scripts")

    # Video settings
    video_width: int = 1920
    video_height: int = 1080
    video_fps: int = 30

    class Config:
        env_file = ".env"
        env_prefix = ""


settings = Settings()

os.makedirs(settings.output_dir, exist_ok=True)
os.makedirs(settings.audio_dir, exist_ok=True)
os.makedirs(settings.scripts_dir, exist_ok=True)
