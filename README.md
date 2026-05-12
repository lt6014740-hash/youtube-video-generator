# YouTube Video Generator

AI-powered multilingual YouTube video generator using **DeepSeek AI**, **F5-TTS/Edge-TTS**, and **Remotion**.

## Features

- **AI Script Generation** — DeepSeek generates engaging video scripts in any language
- **Multi-Language TTS** — Support for Vietnamese, English, Chinese, Japanese, Korean, and more
- **Professional Video Rendering** — Remotion creates YouTube-optimized videos (1920x1080)
- **Animated Subtitles** — Auto-generated captions with smooth animations
- **Pipeline CLI** — One command from topic to finished video
- **REST API** — FastAPI backend for integration

## Supported Languages

| Code | Language   | TTS Engine |
|------|-----------|------------|
| `en` | English   | Edge-TTS / F5-TTS |
| `vi` | Vietnamese| Edge-TTS / F5-TTS |
| `zh` | Chinese   | Edge-TTS / F5-TTS |
| `ja` | Japanese  | Edge-TTS / F5-TTS |
| `ko` | Korean    | Edge-TTS / F5-TTS |
| `fr` | French    | Edge-TTS |
| `de` | German    | Edge-TTS |
| `es` | Spanish   | Edge-TTS |
| `th` | Thai      | Edge-TTS |
| `id` | Indonesian| Edge-TTS |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- FFmpeg
- DeepSeek API key ([Get one here](https://platform.deepseek.com/api_keys))

### Installation

```bash
# Clone the repository
git clone https://github.com/congtuyen202/youtube-video-generator.git
cd youtube-video-generator

# Setup environment
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY

# Install Python dependencies
cd backend
pip install -e .
cd ..

# Install Node.js dependencies (for video rendering)
cd video
npm install
cd ..
```

### Usage

#### CLI Pipeline (Recommended)

```bash
# Generate a short English video
python pipeline.py --topic "Introduction to Machine Learning" --language en

# Generate a Vietnamese video
python pipeline.py --topic "Hướng dẫn lập trình Python cho người mới" --language vi --duration medium

# Generate a Japanese video
python pipeline.py --topic "AI入門ガイド" --language ja --style educational

# Generate script and audio only (skip video rendering)
python pipeline.py --topic "Your Topic" --language en --skip-video
```

#### API Server

```bash
# Start the API server
cd backend
uvicorn app.main:app --reload --port 8000

# API endpoints:
# POST /api/generate-script  — Generate video script
# POST /api/generate-tts     — Convert text to speech
# POST /api/generate-video   — Render video
# POST /api/pipeline         — Run full pipeline
# GET  /health               — Health check
```

#### Remotion Studio (Preview)

```bash
cd video
npm run dev
# Open http://localhost:3000 to preview video compositions
```

## Architecture

```
Topic/Idea → DeepSeek (Script) → TTS (Audio) → Remotion (Video) → YouTube MP4
```

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Script Generator | DeepSeek API | AI-powered script writing |
| TTS Engine | Edge-TTS / F5-TTS | Text-to-speech conversion |
| Video Engine | Remotion (React) | Programmatic video rendering |
| API Server | FastAPI | REST API endpoints |
| CLI | Python argparse | Command-line interface |

## Configuration

### TTS Engines

**Edge-TTS** (Default, Free):
- Microsoft Edge neural voices
- No GPU required
- Fast and reliable
- Set `TTS_ENGINE=edge-tts` in `.env`

**F5-TTS** (Advanced, GPU Recommended):
- High-quality voice cloning
- Requires reference audio
- GPU recommended for performance
- Set `TTS_ENGINE=f5-tts` in `.env`
- Install: `pip install f5-tts`

### Video Customization

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--bg-color` | `#1a1a2e` | Background color |
| `--sub-color` | `#ffffff` | Subtitle color |
| `--accent-color` | `#e94560` | Accent/highlight color |
| `--duration` | `short` | Video length (short/medium/long) |
| `--style` | `educational` | Content style |

## Output

After running the pipeline, you'll find in the `output/` directory:

- `scripts/` — Generated scripts (JSON)
- `audio/` — TTS audio files (MP3/WAV)
- `subtitles.srt` — Subtitle file for YouTube
- `video_*.mp4` — Rendered video file

## Development

```bash
# Run backend lint
cd backend && ruff check . && cd ..

# Run video typecheck
cd video && npm run typecheck && cd ..
```

## License

MIT
