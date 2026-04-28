/**
 * SafeTravel - Backend API Client
 */

const API_BASE = 'http://localhost:5000';

const Api = {
  /**
   * Check if backend is running
   */
  async healthCheck() {
    try {
      const res = await fetch(`${API_BASE}/api/health`, { signal: AbortSignal.timeout(3000) });
      return await res.json();
    } catch (e) {
      return { status: 'error', model_loaded: false };
    }
  },

  /**
   * Main safety prediction
   */
  async predict(params) {
    const res = await fetch(`${API_BASE}/api/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `API error: ${res.status}`);
    }
    
    return await res.json();
  },

  /**
   * Get best times to visit
   */
  async getBestTime(params) {
    const res = await fetch(`${API_BASE}/api/best-time`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return await res.json();
  },

  /**
   * Compare activities at same place
   */
  async compareActivities(params) {
    const res = await fetch(`${API_BASE}/api/compare-activities`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return await res.json();
  },

  /**
   * Get model training info
   */
  async getModelInfo() {
    const res = await fetch(`${API_BASE}/api/model-info`);
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return await res.json();
  }
};
