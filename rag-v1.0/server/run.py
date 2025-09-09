import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json

# Add parent directory to import ai.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ai import rag_query

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])  # Allow React frontend
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Store active conversations
conversations = {}

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    query_text = data['query']
    result = rag_query(query_text)
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "RAG server is running"})

# WebSocket events for real-time communication
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to RAG server', 'session_id': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    if request.sid in conversations:
        del conversations[request.sid]

@socketio.on('send_query')
def handle_query(data):
    session_id = request.sid
    query_text = data.get('query', '')
    
    if not query_text.strip():
        emit('error', {'message': 'Query cannot be empty'})
        return
    
    print(f"Received query from {session_id}: {query_text}")
    
    # Store conversation
    if session_id not in conversations:
        conversations[session_id] = []
    
    conversations[session_id].append({
        'type': 'user',
        'message': query_text,
        'timestamp': str(os.times())
    })
    
    # Emit query received confirmation
    emit('query_received', {'query': query_text, 'status': 'processing'})
    
    try:
        # Process with RAG
        result = rag_query(query_text)
        
        # Store bot response
        conversations[session_id].append({
            'type': 'bot',
            'message': result,
            'timestamp': str(os.times())
        })
        
        # Send response back
        emit('query_response', {
            'query': query_text,
            'response': result,
            'status': 'completed'
        })
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        print(f"Error: {error_msg}")
        emit('error', {'message': error_msg, 'query': query_text})

@socketio.on('get_conversation')
def handle_get_conversation():
    session_id = request.sid
    conversation = conversations.get(session_id, [])
    emit('conversation_history', {'conversation': conversation})

if __name__ == '__main__':
    print("Server running on http://127.0.0.1:5000")
    print("WebSocket enabled for real-time communication")
    socketio.run(app, debug=False, host='127.0.0.1', port=5000)  # Disable debug to avoid restart issues
