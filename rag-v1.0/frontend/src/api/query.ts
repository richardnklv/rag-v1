import { io, Socket } from 'socket.io-client';

interface RagResponse {
  query: string;
  expanded_queries: string[];
  answer: string;
  search_results: any;
  context_used: string[];
  sources: string[];
  source_attribution: any[];
  error?: string;
}

interface QueryRequest {
  query: string;
}

const API_BASE_URL = 'http://127.0.0.1:5000';

class RagApiClient {
  private socket: Socket | null = null;
  private listeners: Map<string, Function[]> = new Map();

  constructor() {
    this.initializeSocket();
  }

  private initializeSocket() {
    this.socket = io(API_BASE_URL, {
      transports: ['websocket', 'polling']
    });

    this.socket.on('connect', () => {
      console.log('Connected to RAG server');
      this.emit('connected', { connected: true });
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from RAG server');
      this.emit('disconnected', { connected: false });
    });

    this.socket.on('connected', (data: any) => {
      console.log('Server confirmation:', data);
      this.emit('server_connected', data);
    });

    this.socket.on('query_received', (data: any) => {
      this.emit('query_received', data);
    });

    this.socket.on('query_response', (data: any) => {
      this.emit('query_response', data);
    });

    this.socket.on('error', (data: any) => {
      this.emit('error', data);
    });

    this.socket.on('conversation_history', (data: any) => {
      this.emit('conversation_history', data);
    });
  }

  // Event listener management
  public on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  public off(event: string, callback: Function) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      const index = eventListeners.indexOf(callback);
      if (index > -1) {
        eventListeners.splice(index, 1);
      }
    }
  }

  private emit(event: string, data: any) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(callback => callback(data));
    }
  }

  // Send query via WebSocket
  public sendQuerySocket(query: string): void {
    if (this.socket?.connected) {
      this.socket.emit('send_query', { query });
    } else {
      this.emit('error', { message: 'Not connected to server' });
    }
  }

  // Get conversation history
  public getConversationHistory(): void {
    if (this.socket?.connected) {
      this.socket.emit('get_conversation');
    }
  }

  // HTTP fallback method
  public async queryRag(query: string): Promise<RagResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query } as QueryRequest),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status} - ${response.statusText}`);
      }

      const data: RagResponse = await response.json();
      return data;
    } catch (error) {
      if (error instanceof Error && error.message.includes('fetch')) {
        throw new Error('Unable to connect to server. Make sure the Flask server is running on http://127.0.0.1:5000');
      }
      throw error;
    }
  }

  // Check server health
  public async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  // Connection status
  public isConnected(): boolean {
    return this.socket?.connected || false;
  }

  // Disconnect
  public disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
    }
  }
}

// Export singleton instance
export const ragApiClient = new RagApiClient();

// Export legacy function for compatibility
export const queryRag = ragApiClient.queryRag.bind(ragApiClient);
