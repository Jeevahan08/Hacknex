const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface HealthResponse {
  status: string;
  demo_mode: boolean;
  backend: string;
  database: string;
  provider: string;
  provider_connected: boolean;
  timestamp: number;
}

export interface ConfigResponse {
  demo_mode: boolean;
  default_source_language: string;
  default_target_languages: string[];
  min_translation_tokens: number;
  max_partial_wait_ms: number;
  silence_commit_ms: number;
  stability_threshold: number;
  llm_enabled: boolean;
  llm_mode: string;
  enable_tts: boolean;
  models: Record<string, string>;
}

export const apiService = {
  async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE}/api/v1/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return res.json();
  },

  async getConfig(): Promise<ConfigResponse> {
    const res = await fetch(`${API_BASE}/api/v1/config`);
    if (!res.ok) throw new Error(`Config fetch failed: ${res.statusText}`);
    return res.json();
  },

  async getModels() {
    const res = await fetch(`${API_BASE}/api/v1/models`);
    if (!res.ok) throw new Error(`Models fetch failed: ${res.statusText}`);
    return res.json();
  },

  async getLanguages() {
    const res = await fetch(`${API_BASE}/api/v1/languages`);
    if (!res.ok) throw new Error(`Languages fetch failed: ${res.statusText}`);
    return res.json();
  },

  async translateText(payload: {
    source_language: string;
    target_languages: string[];
    text: string;
    mode?: string;
  }) {
    const res = await fetch(`${API_BASE}/api/v1/translate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`Translation request failed: ${res.statusText}`);
    return res.json();
  },

  async synthesizeTTS(payload: {
    text: string;
    language: string;
    speaker?: string;
    pace?: number;
    pitch?: number;
  }) {
    const res = await fetch(`${API_BASE}/api/v1/tts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`TTS synthesis failed: ${res.statusText}`);
    return res.json();
  },

  async getGlossary() {
    const res = await fetch(`${API_BASE}/api/v1/glossary`);
    if (!res.ok) throw new Error(`Glossary fetch failed: ${res.statusText}`);
    return res.json();
  },

  async addGlossaryTerm(item: { term: string; action: string; replacement?: string; target_language?: string }) {
    const res = await fetch(`${API_BASE}/api/v1/glossary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(item)
    });
    if (!res.ok) throw new Error(`Add glossary term failed: ${res.statusText}`);
    return res.json();
  },

  async deleteGlossaryTerm(termId: number) {
    const res = await fetch(`${API_BASE}/api/v1/glossary/${termId}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error(`Delete glossary term failed: ${res.statusText}`);
    return res.json();
  },

  async getBenchmark() {
    const res = await fetch(`${API_BASE}/api/v1/benchmark`);
    if (!res.ok) throw new Error(`Benchmark fetch failed: ${res.statusText}`);
    return res.json();
  },

  async runBenchmark(payload: { source_language: string; target_languages: string[]; mode: string }) {
    const res = await fetch(`${API_BASE}/api/v1/benchmark/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`Benchmark run failed: ${res.statusText}`);
    return res.json();
  },

  async createSession(payload: { source_language: string; target_languages: string[]; mode: string }) {
    const res = await fetch(`${API_BASE}/api/v1/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`Create session failed: ${res.statusText}`);
    return res.json();
  },

  async listSessions() {
    const res = await fetch(`${API_BASE}/api/v1/sessions`);
    if (!res.ok) throw new Error(`List sessions failed: ${res.statusText}`);
    return res.json();
  }
};
