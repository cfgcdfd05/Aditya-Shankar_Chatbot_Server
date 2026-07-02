from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import ollama
import json
import threading
import subprocess
import time

def ensure_ollama_running():
    try:
        ollama.list()  # cheap check — succeeds if daemon is up
    except Exception:
        print("Starting ollama serve...")
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)  # give it time to bind

ensure_ollama_running()

# Global lock to ensure only one request uses the GPU at a time
gpu_lock = threading.Lock()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Lab access password
PASSWORD = "cdfd"

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/health')
def health():
    return jsonify({"status": "ok", "model": "deepseek-r1:70b"})

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    if data and data.get('password') == PASSWORD:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid password. Authorized personnel only."}), 401

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    
    # Secure the chat endpoint
    if not data or data.get('password') != PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401
        
    messages = data.get('messages', [])
    
    def generate():
        try:
            if gpu_lock.locked():
                yield f"data: {json.dumps({'reasoning': '⏳ Another user is currently using the GPU. You are in the queue, please wait...\\n\\n'})}\n\n"
            
            with gpu_lock:
                stream = ollama.chat(
                    model='deepseek-r1:70b',
                    messages=messages,
                    stream=True,
                    keep_alive=-1,
                    options={'num_ctx': 1500} # Keep < 2000 to fit GPU KV cache
                )
                for chunk in stream:
                    if 'message' in chunk:
                        msg = chunk['message']
                        content = msg.get('content', '')
                        reasoning = msg.get('reasoning', '')
                        if not reasoning and 'thinking' in msg:
                            reasoning = msg.get('thinking', '')
                        
                        if content or reasoning:
                            yield f"data: {json.dumps({'content': content, 'reasoning': reasoning})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Bind to 0.0.0.0 for LAN access and use threaded=True for multiple concurrent users
    # debug=False since this is reachable by other devices on the LAN
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)