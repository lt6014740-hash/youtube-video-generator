import json
import logging

import httpx

from .config import settings
from .schemas import GenerateScriptRequest, VideoScript

logger = logging.getLogger(__name__)

LANGUAGE_NAMES = {
    "en": "English",
    "vi": "Vietnamese",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "th": "Thai",
    "id": "Indonesian",
}

DURATION_GUIDE = {
    "short": {"scenes": "3-5", "total_seconds": "60-180", "per_scene": "20-40"},
    "medium": {"scenes": "5-10", "total_seconds": "180-480", "per_scene": "30-60"},
    "long": {"scenes": "10-20", "total_seconds": "480-900", "per_scene": "30-60"},
}


def build_system_prompt(request: GenerateScriptRequest) -> str:
    lang_name = LANGUAGE_NAMES.get(request.language, request.language)
    duration_info = DURATION_GUIDE.get(request.duration, DURATION_GUIDE["short"])

    return f"""You are a professional YouTube video script writer.
Write engaging, well-structured video scripts optimized for YouTube.

REQUIREMENTS:
- Write ALL narration text in {lang_name}
- Video style: {request.style}
- Number of scenes: {duration_info['scenes']}
- Total video duration: {duration_info['total_seconds']} seconds
- Each scene duration: {duration_info['per_scene']} seconds
- Write natural, conversational narration suitable for text-to-speech
- Include vivid visual descriptions for each scene (in English for the video engine)
- Make content engaging and suitable for YouTube audience

OUTPUT FORMAT: Return ONLY valid JSON with this exact structure:
{{
    "title": "Video title in {lang_name}",
    "description": "YouTube description in {lang_name}",
    "language": "{request.language}",
    "scenes": [
        {{
            "scene_number": 1,
            "title": "Scene title in {lang_name}",
            "narration": "Narration text in {lang_name} (what will be spoken)",
            "visual_description": "Description of visuals in English",
            "duration_seconds": 30
        }}
    ],
    "tags": ["tag1", "tag2", "tag3"],
    "total_duration_seconds": 120
}}"""


def build_user_prompt(request: GenerateScriptRequest) -> str:
    prompt = f"Create a YouTube video script about: {request.topic}"
    if request.additional_instructions:
        prompt += f"\n\nAdditional instructions: {request.additional_instructions}"
    return prompt


async def generate_script(request: GenerateScriptRequest) -> VideoScript:
    if not settings.deepseek_api_key:
        raise ValueError(
            "DeepSeek API key is not configured. Set DEEPSEEK_API_KEY environment variable."
        )

    system_prompt = build_system_prompt(request)
    user_prompt = build_user_prompt(request)

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.deepseek_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.deepseek_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 4096,
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        result = response.json()

    content = result["choices"][0]["message"]["content"]
    logger.info("DeepSeek response received, parsing script...")

    try:
        script_data = json.loads(content)
    except json.JSONDecodeError:
        import re

        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            script_data = json.loads(json_match.group())
        else:
            raise ValueError("Failed to parse script from DeepSeek response")

    script = VideoScript(**script_data)

    if script.total_duration_seconds == 0:
        script.total_duration_seconds = sum(s.duration_seconds for s in script.scenes)

    return script
