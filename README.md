# Visual Avatar AI Agent System

> 🚧 **Work in Progress**
> This project is actively under development. Core avatar synthesis and live video streaming components are being implemented using **100% open-source technologies**.

## Overview

The Visual Avatar AI Agent System is a production-oriented AI application designed to support **interactive, avatar-based AI experiences**. It separates a **control plane** (Convex + frontend) from a **data plane** (media pipeline) to support near real-time avatar streaming.

The long-term goal is to synthesize a **live, streamable visual avatar** from text input, a single avatar image, background video, and an overlay logo, enabling realistic motion, gestures, and lip-sync in near real time.

## Architecture

- **Frontend (Vite + React)**: Uploads assets, starts a stream, sends live text, and plays HLS.
- **Control Plane (Convex)**: Stores stream metadata and forwards text to the media service.
- **Media Service (FastAPI)**: Generates TTS, composites frames, and outputs HLS segments via ffmpeg.

## Quickstart (local)

### 1) Start the media service

```bash
cd media_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2) Start the frontend

```bash
npm install
npm run dev:frontend
```

Open the app at `http://localhost:5173` and provide:

- Avatar image (PNG/JPG)
- Background video (MP4)
- Logo (PNG)

Then start the stream and send text. The HLS stream will load in the embedded video player.

## Docker (media service)

```bash
docker build -t visual-avatar-media-service ./media_service
docker run -p 8000:8000 -e PIPER_MODEL=/models/en_US-amy-medium.onnx \
  -v $(pwd)/models:/models \
  visual-avatar-media-service
```

## Open-source pipeline

- **TTS**: Piper (recommended) or `espeak-ng` fallback.
- **Compositing + HLS**: ffmpeg.
- **Lip-sync**: Modular hook for future Wav2Lip integration (planned).

## Project Structure

```
visual-avatar-ai-agent/
├── media_service/        # FastAPI media pipeline
├── src/                  # Frontend application
├── README.md
└── package.json
```

## Development Notes

- The media service writes HLS output to `media_service/output/{streamKey}`.
- TTS will fail unless you install Piper or `espeak-ng` locally.
- The lip-sync stage is currently a placeholder; Wav2Lip integration is next.

## License

This project uses open-source tooling and is intended for research, learning, and production experimentation.
