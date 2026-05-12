---
name: testing-video-generator
description: Test the YouTube Video Generator end-to-end. Use when verifying Remotion video rendering, TTS audio generation, or backend API changes.
---

# Testing YouTube Video Generator

## Prerequisites

1. Install dependencies:
   ```bash
   cd backend && pip install -e .
   cd video && npm install
   ```

2. Start services:
   ```bash
   # Terminal 1: Backend API
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
   
   # Terminal 2: Remotion Studio
   cd video && npx remotion studio --port 3000
   ```

## Devin Secrets Needed

- `DEEPSEEK_API_KEY` — Required for script generation. Without it, only Remotion preview and TTS can be tested.

## Test Flows

### 1. Remotion Studio Preview (GUI — no API key needed)

Open http://localhost:3000 in browser. The default composition "YouTubeVideo" should load.

**What to verify:**
- Left sidebar shows composition: 1920x1080, 30 FPS, Duration 00:50.00
- Frame 0-120: Title Card — "Welcome to AI Video Generator" with accent lines and gradient background
- Frame 120-420: Scene 1 — SCENE 1 badge, icon, title "Introduction", visual description
- Frame 420+: Scene 2+ — Different badge numbers, icons, titles, gradient colors
- Subtitles appear as overlay with glassmorphism background and accent left border
- Last 5 seconds: Outro Card — "Thanks for watching!" with Subscribe and Like & Share buttons
- Play video to verify smooth animations (~30 FPS)
- Check browser console for errors (expect none; React DevTools info is OK)

**Timeline layout:**
- 6 sequences visible: Title (4s) → Scene 1 → Scene 2 → Scene 3 → Subtitles overlay → Outro (5s)

### 2. Backend API (Shell — no API key needed)

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status": "ok", "tts_engine": "edge-tts", "deepseek_configured": false}

# Edge-TTS audio generation (multiple languages)
curl -X POST http://localhost:8000/api/generate-tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "language": "en"}'
# Expected: {"audio_file": "<path>.mp3", "duration_seconds": <number>}

# Script generation error handling (without API key)
curl -X POST http://localhost:8000/api/generate-script \
  -H "Content-Type: application/json" \
  -d '{"topic": "test", "language": "en", "duration": "short"}'
# Expected: {"detail": "DeepSeek API key is not configured..."}
```

### 3. Full Pipeline (requires DEEPSEEK_API_KEY)

```bash
python pipeline.py --topic "Your Topic" --language en --duration short
```

This generates script → audio → video end-to-end. Output goes to `output/` directory.

## Lint & Typecheck

```bash
cd backend && ruff check app/
cd video && npx tsc --noEmit
```

## Tips

- Edge-TTS is free and works without any API key. It supports 10 languages with neural voices.
- Remotion Studio preview works entirely without backend — it uses default props defined in `video/src/Root.tsx`.
- The Remotion timeline scrubber is the best way to verify individual components (title, scenes, subtitles, outro) render correctly at specific frames.
- If Remotion Studio shows a blank canvas at frame 0, scrub to frame 30+ to see the title spring animation complete.
- Scene backgrounds use different gradient colors per scene index — verify by scrubbing between scenes.
