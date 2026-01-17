import { useEffect, useRef, useState } from "react";
import Hls from "hls.js";

const MEDIA_SERVICE_URL =
  import.meta.env.VITE_MEDIA_SERVICE_URL ?? "http://localhost:8000";

export default function App() {
  const [streamKey, setStreamKey] = useState("demo-stream");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [backgroundFile, setBackgroundFile] = useState<File | null>(null);
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [playbackUrl, setPlaybackUrl] = useState<string | null>(null);
  const [text, setText] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    if (!playbackUrl || !videoRef.current) {
      return;
    }

    if (Hls.isSupported()) {
      const hls = new Hls();
      hls.loadSource(playbackUrl);
      hls.attachMedia(videoRef.current);
      return () => {
        hls.destroy();
      };
    }

    videoRef.current.src = playbackUrl;
  }, [playbackUrl]);

  const startStream = async () => {
    if (!avatarFile || !backgroundFile || !logoFile) {
      setStatus("Please select avatar, background, and logo files.");
      return;
    }

    const formData = new FormData();
    formData.append("streamKey", streamKey);
    formData.append("avatar", avatarFile);
    formData.append("background", backgroundFile);
    formData.append("logo", logoFile);

    const response = await fetch(`${MEDIA_SERVICE_URL}/streams/start`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      setStatus("Failed to start stream.");
      return;
    }

    const data = (await response.json()) as { playbackUrl: string };
    setPlaybackUrl(`${MEDIA_SERVICE_URL}${data.playbackUrl}`);
    setStatus("Stream started.");
  };

  const sendText = async () => {
    if (!text.trim()) {
      return;
    }

    const response = await fetch(`${MEDIA_SERVICE_URL}/streams/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ streamKey, text }),
    });

    if (!response.ok) {
      setStatus("Failed to send text.");
      return;
    }

    setStatus("Text queued for synthesis.");
    setText("");
  };

  const stopStream = async () => {
    const response = await fetch(`${MEDIA_SERVICE_URL}/streams/stop`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ streamKey }),
    });

    if (!response.ok) {
      setStatus("Failed to stop stream.");
      return;
    }

    setStatus("Stream stopped.");
    setPlaybackUrl(null);
  };

  return (
    <div className="app">
      <header>
        <h1>Visual Avatar AI Agent System</h1>
        <p>Upload assets, start the stream, then send live text.</p>
      </header>

      <section className="panel">
        <label>
          Stream Key
          <input
            type="text"
            value={streamKey}
            onChange={(event) => setStreamKey(event.target.value)}
          />
        </label>
        <label>
          Avatar Image
          <input
            type="file"
            accept="image/*"
            onChange={(event) =>
              setAvatarFile(event.target.files?.[0] ?? null)
            }
          />
        </label>
        <label>
          Background Video
          <input
            type="file"
            accept="video/*"
            onChange={(event) =>
              setBackgroundFile(event.target.files?.[0] ?? null)
            }
          />
        </label>
        <label>
          Logo Image
          <input
            type="file"
            accept="image/*"
            onChange={(event) => setLogoFile(event.target.files?.[0] ?? null)}
          />
        </label>
        <div className="actions">
          <button onClick={startStream}>Start Stream</button>
          <button onClick={stopStream} className="secondary">
            Stop Stream
          </button>
        </div>
        {status && <p className="status">{status}</p>}
      </section>

      <section className="panel">
        <h2>Live Text</h2>
        <div className="actions">
          <input
            type="text"
            placeholder="Enter text to synthesize"
            value={text}
            onChange={(event) => setText(event.target.value)}
          />
          <button onClick={sendText}>Send</button>
        </div>
      </section>

      <section className="panel">
        <h2>Playback</h2>
        <video ref={videoRef} controls autoPlay muted />
      </section>
    </div>
  );
}
