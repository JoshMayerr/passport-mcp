export interface Identity {
  id: string;
  name: string;
  createdAt: number;
}

export interface Message {
  type: string;
  payload: unknown;
}
