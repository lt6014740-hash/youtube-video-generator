import os

from .schemas import VideoScript


def seconds_to_srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(script: VideoScript, output_path: str) -> str:
    lines = []
    current_time = 0.0

    for i, scene in enumerate(script.scenes, 1):
        words = scene.narration.split()
        chunk_size = 12
        chunks = []
        for j in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[j : j + chunk_size]))

        if not chunks:
            chunks = [scene.narration]

        chunk_duration = scene.duration_seconds / len(chunks)

        for chunk in chunks:
            start_time = seconds_to_srt_time(current_time)
            end_time = seconds_to_srt_time(current_time + chunk_duration)
            lines.append(f"{len(lines) // 3 + 1}")
            lines.append(f"{start_time} --> {end_time}")
            lines.append(chunk)
            lines.append("")
            current_time += chunk_duration

    srt_content = "\n".join(lines)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    return output_path


def generate_subtitle_data(script: VideoScript) -> list[dict]:
    subtitles = []
    current_time = 0.0

    for scene in script.scenes:
        words = scene.narration.split()
        chunk_size = 10
        chunks = []
        for j in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[j : j + chunk_size]))

        if not chunks:
            chunks = [scene.narration]

        chunk_duration = scene.duration_seconds / len(chunks)

        for chunk in chunks:
            subtitles.append(
                {
                    "text": chunk,
                    "startFrame": int(current_time * 30),
                    "endFrame": int((current_time + chunk_duration) * 30),
                }
            )
            current_time += chunk_duration

    return subtitles
