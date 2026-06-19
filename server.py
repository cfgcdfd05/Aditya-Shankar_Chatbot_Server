from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import ollama
import json

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/health')
def health():
    return jsonify({"status": "ok", "model": "deepseek-r1:70b"})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    
    def generate():
        try:
            stream = ollama.chat(
                model='deepseek-r1:70b',
                messages=messages,
                stream=True
            )
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    # Yield as SSE format
                    yield f"data: {json.dumps({'content': content})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Bind to 0.0.0.0 to allow LAN access
    app.run(host='0.0.0.0', port=5000, debug=True)
