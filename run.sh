#!/bin/bash
# ============================================================
# YouTube Video Generator — 1 lenh duy nhat
# Cai dat + Tao audio + Render video tu dong
# ============================================================
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "============================================================"
echo "  YouTube Video Generator — Setup & Render"
echo "============================================================"

# --- 1. Kiem tra Python ---
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Khong tim thay python3. Hay cai Python 3.10+ truoc."
    exit 1
fi

# --- 2. Kiem tra Node.js ---
if ! command -v node &>/dev/null; then
    echo "[ERROR] Khong tim thay node. Hay cai Node.js 18+ truoc."
    exit 1
fi

# --- 3. Cai dat Python backend ---
echo ""
echo "[1/4] Cai dat Python backend..."
cd "$ROOT_DIR/backend"
pip install -e . --quiet 2>&1 | tail -3
cd "$ROOT_DIR"

# --- 4. Cai dat Node.js video engine ---
echo "[2/4] Cai dat Remotion video engine..."
cd "$ROOT_DIR/video"
npm install --silent 2>&1 | tail -3
cd "$ROOT_DIR"

# --- 5. Kiem tra nhac nen ---
BGM_FILE="$ROOT_DIR/video/public/audio/background-music.mp3"
if [ ! -f "$BGM_FILE" ]; then
    echo ""
    echo "[WARN] Khong tim thay nhac nen tai: video/public/audio/background-music.mp3"
    echo "       Video se render KHONG co nhac nen."
    echo "       De them nhac nen, copy file MP3 vao: video/public/audio/background-music.mp3"
    echo ""
fi

# --- 6. Tao audio + Render video ---
echo "[3/4] Tao audio TTS + Render video..."
python3 "$ROOT_DIR/run_threads_genz_real.py"

# --- 7. Ket qua ---
OUTPUT_FILE="$ROOT_DIR/output/threads_genz_real.mp4"
if [ -f "$OUTPUT_FILE" ]; then
    SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    DURATION=$(ffprobe -i "$OUTPUT_FILE" -show_entries format=duration -v quiet -of csv="p=0" 2>/dev/null || echo "?")
    echo ""
    echo "============================================================"
    echo "  VIDEO HOAN THANH!"
    echo "  File: $OUTPUT_FILE"
    echo "  Kich thuoc: $SIZE"
    echo "  Thoi luong: ${DURATION}s"
    echo "============================================================"
else
    echo "[ERROR] Render that bai. Khong tim thay file output."
    exit 1
fi
