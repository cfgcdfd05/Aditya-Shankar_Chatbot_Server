# LLM Chat

A self-contained, locally-hosted web chat interface that streams responses from a local Ollama model (`deepseek-r1:70b`). Built specifically for LAN access with a clean dark theme and lightweight vanilla technologies.

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/) installed and running on the host machine.
- The `deepseek-r1:70b` model pulled in Ollama.

To ensure you have the model, run:
```bash
ollama pull deepseek-r1:70b
```

## Setup

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   python server.py
   ```

## Accessing the Chat

- **On the host PC**: Open your browser and go to `http://localhost:5000` or `http://127.0.0.1:5000`
- **From other PCs on the same network**:
  1. Find the host machine's IP address. On Windows, open Command Prompt and run `ipconfig`. Look for the "IPv4 Address" (e.g., `192.168.1.10`).
  2. Open a browser on the client PC and navigate to `http://<your-ip>:5000`

## Authentication

When accessing the web interface, you will be prompted for a password.

- **Password**: `cdfd`

The authentication state is saved in the browser's `sessionStorage`. This means you will only need to re-enter it if you close the tab and open a new one (refreshing the page does not require logging in again).

## Features

- **Local Network Ready**: Flask is bound to `0.0.0.0` making it automatically accessible to other devices on the LAN.
- **Real-time Token Streaming**: Responses are streamed token-by-token over Server-Sent Events (SSE) so you don't have to wait for the entire generation.
- **Reasoning Blocks**: Support for formatting DeepSeek's `<think>` tags into collapsible reasoning blocks to keep the chat interface clean.
- **Pure Vanilla Stack**: Just HTML, inline CSS, and vanilla JavaScript without bundlers or frameworks.
- **In-Memory History**: A multi-turn conversation context is maintained within the browser session and automatically resets on page reload.
- **Model Stays Loaded**: `keep_alive` is set to stay resident in VRAM indefinitely, so there's no reload delay between requests (only on first-ever query after server start).