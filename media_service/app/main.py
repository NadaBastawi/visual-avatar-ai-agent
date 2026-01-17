import asyncio
import math
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

STREAM_KEY_RE = re.compile(r"^[a-zA-Z0-9_-]{3,64}$")
BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = BASE_DIR / "output"
UPLOAD_ROOT = BASE_DIR / "uploads"
MAX_UPLOAD_BYTES = 50 * 1024 * 1024
MAX_TEXT_CHARS = 500

app = FastAPI(title="Media Service", version="0.1.0")
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/live", StaticFiles(directory=OUTPUT_ROOT), name="live")


class StreamTextRequest(BaseModel):
    streamKey: str
    text: str


class StreamStopRequest(BaseModel):
    streamKey: str


@dataclass
class StreamSession:
    stream_key: str
    avatar_path: Path
    background_path: Path
    logo_path: Path
    output_dir: Path
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    task: Optional[asyncio.Task] = None
    segment_index: int = 0
    active: bool = True

    async def start(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        await self._write_placeholder()
        self.task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        self.active = False
        await self.queue.put(None)
        if self.task:
            await self.task

    async def enqueue_text(self, text: str) -> None:
        await self.queue.put(text)

    async def _worker(self) -> None:
        while self.active:
            text = await self.queue.get()
            if text is None:
                break
            await asyncio.to_thread(self._render_text_segment, text)

    async def _write_placeholder(self) -> None:
        placeholder_audio = await asyncio.to_thread(create_silence_audio, 1.0)
        try:
            await asyncio.to_thread(
                render_hls_segment,
                self.background_path,
                self.avatar_path,
                self.logo_path,
                placeholder_audio,
                self.output_dir,
                self.segment_index,
            )
            self.segment_index += 1
        finally:
            placeholder_audio.unlink(missing_ok=True)

    def _render_text_segment(self, text: str) -> None:
        audio_path = synthesize_tts(text)
        try:
            render_hls_segment(
                self.background_path,
                self.avatar_path,
                self.logo_path,
                audio_path,
                self.output_dir,
                self.segment_index,
            )
            duration = get_audio_duration(audio_path)
            self.segment_index += max(1, math.ceil(duration / 2))
        finally:
            audio_path.unlink(missing_ok=True)


sessions: Dict[str, StreamSession] = {}


def validate_stream_key(stream_key: str) -> None:
    if not STREAM_KEY_RE.match(stream_key):
        raise HTTPException(status_code=400, detail="Invalid streamKey format")


def save_upload(upload: UploadFile, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    size = 0
    with target_path.open("wb") as buffer:
        while True:
            chunk = upload.file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="Upload too large")
            buffer.write(chunk)


def synthesize_tts(text: str) -> Path:
    if len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=400, detail="Text too long")

    output_path = Path(tempfile.mkstemp(suffix=".wav")[1])
    piper_bin = shutil.which("piper")
    piper_model = os.environ.get("PIPER_MODEL")
    if piper_bin and piper_model:
        process = subprocess.run(
            [piper_bin, "--model", piper_model, "--output_file", str(output_path)],
            input=text,
            text=True,
            capture_output=True,
            check=False,
        )
        if process.returncode != 0:
            raise RuntimeError(process.stderr or "Piper TTS failed")
        return output_path

    espeak_bin = shutil.which("espeak-ng") or shutil.which("espeak")
    if espeak_bin:
        process = subprocess.run(
            [espeak_bin, "-w", str(output_path), text],
            capture_output=True,
            check=False,
        )
        if process.returncode != 0:
            raise RuntimeError(process.stderr or "espeak TTS failed")
        return output_path

    raise HTTPException(
        status_code=500,
        detail="No TTS engine available. Install piper or espeak-ng.",
    )


def create_silence_audio(duration: float) -> Path:
    output_path = Path(tempfile.mkstemp(suffix=".wav")[1])
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"anullsrc=r=44100:cl=mono",
            "-t",
            str(duration),
            str(output_path),
        ],
        capture_output=True,
        check=True,
    )
    return output_path


def get_audio_duration(audio_path: Path) -> float:
    process = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(process.stdout.strip())


def render_hls_segment(
    background_path: Path,
    avatar_path: Path,
    logo_path: Path,
    audio_path: Path,
    output_dir: Path,
    start_number: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    segment_pattern = output_dir / "segment_%05d.ts"
    playlist_path = output_dir / "index.m3u8"

    duration = get_audio_duration(audio_path)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            str(background_path),
            "-loop",
            "1",
            "-i",
            str(avatar_path),
            "-loop",
            "1",
            "-i",
            str(logo_path),
            "-i",
            str(audio_path),
            "-filter_complex",
            "[0:v]scale=1280:720[bg];"
            "[1:v]scale=500:-1[av];"
            "[2:v]scale=200:-1[lg];"
            "[bg][av]overlay=(W-w)/2:H-h-40[tmp];"
            "[tmp][lg]overlay=20:20[v]",
            "-map",
            "[v]",
            "-map",
            "3:a",
            "-shortest",
            "-t",
            str(duration),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-c:a",
            "aac",
            "-f",
            "hls",
            "-hls_time",
            "2",
            "-hls_list_size",
            "0",
            "-hls_flags",
            "append_list+omit_endlist",
            "-start_number",
            str(start_number),
            "-hls_segment_filename",
            str(segment_pattern),
            str(playlist_path),
        ],
        capture_output=True,
        check=True,
    )


@app.post("/streams/start")
async def start_stream(
    streamKey: str = Form(...),
    avatar: UploadFile = File(...),
    background: UploadFile = File(...),
    logo: UploadFile = File(...),
):
    validate_stream_key(streamKey)
    stream_dir = UPLOAD_ROOT / streamKey
    if streamKey in sessions:
        await sessions[streamKey].stop()
        sessions.pop(streamKey, None)
        shutil.rmtree(OUTPUT_ROOT / streamKey, ignore_errors=True)

    save_upload(avatar, stream_dir / "avatar.png")
    save_upload(background, stream_dir / "background.mp4")
    save_upload(logo, stream_dir / "logo.png")

    session = StreamSession(
        stream_key=streamKey,
        avatar_path=stream_dir / "avatar.png",
        background_path=stream_dir / "background.mp4",
        logo_path=stream_dir / "logo.png",
        output_dir=OUTPUT_ROOT / streamKey,
    )
    sessions[streamKey] = session
    await session.start()
    return {"streamKey": streamKey, "playbackUrl": f"/live/{streamKey}/index.m3u8"}


@app.post("/streams/text")
async def stream_text(payload: StreamTextRequest):
    validate_stream_key(payload.streamKey)
    session = sessions.get(payload.streamKey)
    if not session:
        raise HTTPException(status_code=404, detail="Stream not found")
    await session.enqueue_text(payload.text)
    return {"status": "queued"}


@app.post("/streams/stop")
async def stop_stream(payload: StreamStopRequest):
    validate_stream_key(payload.streamKey)
    session = sessions.pop(payload.streamKey, None)
    if not session:
        raise HTTPException(status_code=404, detail="Stream not found")
    await session.stop()
    return {"status": "stopped"}


@app.websocket("/ws/{stream_key}")
async def stream_ws(websocket: WebSocket, stream_key: str):
    validate_stream_key(stream_key)
    session = sessions.get(stream_key)
    if not session:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            await session.enqueue_text(message)
            await websocket.send_json({"status": "queued"})
    except Exception:
        await websocket.close()


@app.get("/live/{stream_key}/index.m3u8")
async def get_playlist(stream_key: str):
    validate_stream_key(stream_key)
    playlist_path = OUTPUT_ROOT / stream_key / "index.m3u8"
    if not playlist_path.exists():
        raise HTTPException(status_code=404, detail="Playlist not found")
    return FileResponse(playlist_path)
