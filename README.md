# Visual Avatar AI Agent System

> 🚧 **Work in Progress**
> This project is actively under development. Core avatar synthesis and live video streaming components are being implemented using **100% open-source technologies**.

---

## EcoSim AI: Modeling Simple Ecosystem Interactions

This repository now includes a small, educational predator–prey simulation that models **Rabbits** and **Foxes** over 10 generations using simple agent-like rules and a fixed random seed. The results are stored in `results.csv`, and the narrative summary is in `report.md`.

### How to Run

```bash
python simulation.py
```

Running the script regenerates `results.csv` and prints the table to stdout. The report is written to align with the CSV values.

### Assumptions

* Prey grow by a base rate each generation.
* Predators gain population only by consuming prey.
* Predators lose a fixed share each generation through natural deaths.
* Mild randomness (±5%) is applied to births and predation, with a fixed seed for stability.

### Tweak Parameters

Open `simulation.py` and edit the `SimulationParams` dataclass to change starting populations, growth rates, predation rates, or the random seed.

## Overview

The Visual Avatar AI Agent System is a production-oriented AI application designed to support **interactive, avatar-based AI experiences**. The system is architected with a clear separation between frontend interaction, backend orchestration, and media processing, making it suitable for scalable and real-time AI applications.

The long-term goal of the project is to synthesize a **live, streamable visual avatar** from text input, a single avatar image, background video, and an overlay logo, enabling realistic motion, gestures, and lip-sync in near real time.

---

## Current Capabilities

* Agent-oriented application structure
* Frontend interface built with Vite, TypeScript, and Tailwind CSS
* Backend orchestration using Convex for state management and API routing
* Modular architecture prepared for real-time streaming and media synthesis
* Clean project organization suitable for extension into production systems

---

## Planned Features

* Text-driven avatar animation using open-source TTS and lip-sync models
* Video composition pipeline (avatar + background video + overlay logo)
* Custom streaming API to output live video (HLS / RTMP)
* Real-time text input via socket-based communication
* Full documentation and deployment instructions

---

## Architecture Overview

The system is designed with a **control-plane / data-plane** separation:

* **Frontend**: User interaction, asset upload, stream control, and playback
* **Backend (Convex)**: Agent orchestration, configuration management, and event routing
* **Media Service (Planned)**: Dedicated service for audio synthesis, avatar animation, video composition, and live streaming output

This separation allows the media pipeline to evolve independently while keeping the application scalable and maintainable.

---

## Project Structure

```
visual-avatar-ai-agent/
├── src/                 # Frontend application
├── convex/              # Backend logic and orchestration
├── media_service/       # (Planned) Media synthesis & streaming service
├── public/              # Static assets
├── README.md
└── package.json
```

---

## Tech Stack

* **Frontend**: Vite, TypeScript, Tailwind CSS
* **Backend**: Convex (serverless functions, real-time data)
* **AI / Media (Planned)**: Open-source TTS, lip-sync, animation, and ffmpeg-based streaming
* **Streaming (Planned)**: HLS / RTMP using open-source tooling only

---

## Development

Install dependencies and start the development environment:

```bash
npm install
npm run dev
```

---

## Notes

* This project intentionally avoids proprietary or paid APIs.
* All planned media synthesis and streaming components will rely on open-source technologies.
* The repository will evolve incrementally as the media pipeline is implemented.

---

## License

This project uses open-source tooling and is intended for research, learning, and production experimentation.

