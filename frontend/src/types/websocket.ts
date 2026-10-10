export type WSConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'reconnecting' | 'error';

export interface WSMessage<T = any> {
  type: string;
  data?: T;
  [key: string]: any;
}
