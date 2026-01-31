import os
from flask import Flask, render_template, request, Response, stream_with_context
from flask_cors import CORS
from rime.client import AIClient
from rime.utils import load_config
from rich.console import Console

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
CORS(app)
console = Console()

# Initialize client_config globally (or load it within the route)
client_config = None

def get_client():
    global client_config
    if client_config is None:
        client_config = load_config(console)
    if client_config:
        return AIClient(client_config)
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    
    client = get_client()
    if not client:
        return {"error": "Configuration not found"}, 500

    def generate():
        try:
            generator = client.chat_completion(messages)
            for chunk in generator:
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/plain')

def start_server(host='127.0.0.1', port=5000):
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    start_server()
