# YouTube Video Generator - Architecture

## Overview
A tool to automatically generate multilingual YouTube videos using AI.

## Pipeline
```
Topic/Idea → DeepSeek (Script) → F5-TTS (Audio) → Remotion (Video) → YouTube-ready MP4
```

## Components

### 1. Backend (Python/FastAPI)
- **Script Generator**: DeepSeek API integration for multilingual script generation
- **TTS Service**: F5-TTS integration for text-to-speech (with edge-tts fallback)
- **API Endpoints**: REST API for the pipeline

### 2. Video Engine (Remotion/TypeScript)
- **Compositions**: YouTube video templates (16:9, 1920x1080)
- **Components**: Subtitles, backgrounds, scenes, transitions
- **Renderer**: Server-side rendering to MP4

### 3. Pipeline CLI (Python)
- Orchestrates the full flow: Script → TTS → Video
- Configuration via YAML/JSON
- Batch processing support

## Supported Languages
Vietnamese, English, Chinese, Japanese, Korean (extensible)

## Tech Stack
- Python 3.11+ (FastAPI, F5-TTS, httpx)
- Node.js 18+ (Remotion, React, TypeScript)
- DeepSeek API (script generation)
