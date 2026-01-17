# Media Service

<!--
PLAN
- Build a FastAPI service that manages stream sessions keyed by streamKey.
- Implement start/text/stop HTTP endpoints plus a WebSocket for realtime text.
- On start, validate inputs, store uploads, and create per-stream output dirs.
- On text, queue messages per stream and render short HLS segments by:
  - generating TTS audio (Piper preferred; fallback to espeak-ng)
  - compositing avatar + background + logo with ffmpeg
  - appending segments to an HLS playlist for live playback
- Keep the pipeline modular to swap in a Wav2Lip/full-body animator later.
- Provide docker-compose + deployment instructions at repo root.
-->

## Overview

This FastAPI service acts as the **data-plane** for the Visual Avatar AI Agent System. It accepts text, avatar assets, background video, and a logo, then generates HLS segments for live playback using open-source tooling (ffmpeg + optional Piper TTS).

## Requirements

- Python 3.11+
- `ffmpeg` installed and available in `PATH`
- **Optional (recommended)**: Piper TTS binary and a compatible model
- **Optional**: `espeak-ng` as a fallback TTS engine

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Endpoints

- `POST /streams/start` (multipart form)
  - `streamKey` (string)
  - `avatar` (file)
  - `background` (file)
  - `logo` (file)
- `POST /streams/text` (JSON)
  - `{ "streamKey": "abc", "text": "hello" }`
- `POST /streams/stop` (JSON)
  - `{ "streamKey": "abc" }`
- `GET /live/{streamKey}/index.m3u8`
- `WS /ws/{streamKey}`

## Notes

- HLS output is written to `media_service/output/{streamKey}`.
- The pipeline currently uses a **static avatar overlay** and is structured so Wav2Lip/full-body motion can be integrated later.
