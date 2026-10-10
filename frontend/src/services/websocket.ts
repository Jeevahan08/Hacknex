import { WSConnectionStatus, WSMessage } from '../types/websocket';

const WS_BASE = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';

export class LiveWebSocketClient {
  private ws: WebSocket | null = null;
  private sessionId: string = '';
  private status: WSConnectionStatus = 'disconnected';
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectTimer: any = null;
  private messageHandlers: Array<(msg: WSMessage) => void> = [];
  private statusHandlers: Array<(status: WSConnectionStatus) => void> = [];
  private intentionalClose: boolean = false;

  connect(sessionId: string) {
    this.sessionId = sessionId;
    this.intentionalClose = false;
    this.setStatus('connecting');

    const url = `${WS_BASE}/ws/v1/live/${sessionId}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.setStatus('connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        this.notifyMessage(msg);
      } catch (err) {
        console.error('Failed to parse WebSocket JSON message:', err);
      }
    };

    this.ws.onclose = () => {
      if (!this.intentionalClose) {
        this.scheduleReconnect();
      } else {
        this.setStatus('disconnected');
      }
    };

    this.ws.onerror = (err) => {
      console.warn('WebSocket encountered error:', err);
      this.setStatus('error');
    };
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.setStatus('error');
      return;
    }

    this.setStatus('reconnecting');
    const delay = Math.min(8000, 1000 * Math.pow(2, this.reconnectAttempts));
    this.reconnectAttempts++;

    clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      if (!this.intentionalClose && this.sessionId) {
        this.connect(this.sessionId);
      }
    }, delay);
  }

  send(msg: object) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(msg));
    }
  }

  disconnect() {
    this.intentionalClose = true;
    clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.setStatus('disconnected');
  }

  private setStatus(status: WSConnectionStatus) {
    this.status = status;
    this.statusHandlers.forEach((handler) => handler(status));
  }

  private notifyMessage(msg: WSMessage) {
    this.messageHandlers.forEach((handler) => handler(msg));
  }

  onMessage(callback: (msg: WSMessage) => void) {
    this.messageHandlers.push(callback);
    return () => {
      this.messageHandlers = this.messageHandlers.filter((cb) => cb !== callback);
    };
  }

  onStatusChange(callback: (status: WSConnectionStatus) => void) {
    this.statusHandlers.push(callback);
    callback(this.status);
    return () => {
      this.statusHandlers = this.statusHandlers.filter((cb) => cb !== callback);
    };
  }

  getStatus(): WSConnectionStatus {
    return this.status;
  }
}

export const liveWsClient = new LiveWebSocketClient();
