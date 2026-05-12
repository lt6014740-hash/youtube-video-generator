from pydantic import BaseModel, Field


class ScriptScene(BaseModel):
    scene_number: int
    title: str
    narration: str
    visual_description: str
    duration_seconds: float = 10.0


class VideoScript(BaseModel):
    title: str
    description: str
    language: str
    scenes: list[ScriptScene]
    tags: list[str] = []
    total_duration_seconds: float = 0.0


class GenerateScriptRequest(BaseModel):
    topic: str = Field(..., description="Topic or idea for the video")
    language: str = Field(default="en", description="Target language code (en, vi, zh, ja, ko)")
    duration: str = Field(
        default="short",
        description="Video duration: short (1-3 min), medium (3-8 min), long (8-15 min)",
    )
    style: str = Field(
        default="educational",
        description="Video style: educational, storytelling, tutorial, news, entertainment",
    )
    additional_instructions: str = Field(
        default="",
        description="Extra instructions for script generation",
    )


class GenerateScriptResponse(BaseModel):
    script: VideoScript
    script_file: str


class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    language: str = Field(default="en", description="Language code")
    voice: str = Field(default="", description="Voice name (optional, auto-selected by language)")
    speed: float = Field(default=1.0, description="Speech speed multiplier")


class TTSResponse(BaseModel):
    audio_file: str
    duration_seconds: float


class GenerateVideoRequest(BaseModel):
    script: VideoScript
    audio_files: list[str] = Field(
        default_factory=list,
        description="Audio file paths for each scene",
    )
    background_color: str = Field(default="#1a1a2e", description="Background color")
    subtitle_color: str = Field(default="#ffffff", description="Subtitle text color")
    accent_color: str = Field(default="#e94560", description="Accent color for highlights")
    font_family: str = Field(default="Inter", description="Font family for text")


class GenerateVideoResponse(BaseModel):
    video_file: str
    duration_seconds: float
    resolution: str


class PipelineRequest(BaseModel):
    topic: str
    language: str = "en"
    duration: str = "short"
    style: str = "educational"
    additional_instructions: str = ""
    background_color: str = "#1a1a2e"
    subtitle_color: str = "#ffffff"
    accent_color: str = "#e94560"


class PipelineResponse(BaseModel):
    script: VideoScript
    audio_files: list[str]
    video_file: str
    subtitle_file: str
