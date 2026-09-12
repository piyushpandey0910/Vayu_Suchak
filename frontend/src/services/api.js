const API_BASE = '/api';

async function handleResponse(response) {
  if (response.status === 429) {
    const data = await response.json().catch(() => ({}));
    const err = new Error(data.message || "You're sending requests too quickly — please wait a moment.");
    err.isRateLimit = true;
    err.status = 429;
    throw err;
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const err = new Error(data.detail || data.message || `Request failed with status ${response.status}`);
    err.status = response.status;
    throw err;
  }

  return response.json();
}

export const api = {
  async getCurrentAQI(city = 'Kanpur') {
    const res = await fetch(`${API_BASE}/aqi/current?city=${encodeURIComponent(city)}`);
    return handleResponse(res);
  },

  async getForecast(city = 'Kanpur', horizon = '24h') {
    let url = `${API_BASE}/aqi/forecast?city=${encodeURIComponent(city)}`;
    if (horizon === '6h') url += '&hours=6';
    else if (horizon === '12h') url += '&hours=12';
    else if (horizon === '24h') url += '&hours=24';
    else if (horizon === '7d' || horizon === '7days') url += '&days=7';
    else url += '&hours=24';

    const res = await fetch(url);
    return handleResponse(res);
  },

  async getHistory(city = 'Kanpur', range = '7d') {
    const res = await fetch(`${API_BASE}/aqi/history?city=${encodeURIComponent(city)}&range=${encodeURIComponent(range)}`);
    return handleResponse(res);
  },

  async getPollutants(city = 'Kanpur') {
    const res = await fetch(`${API_BASE}/aqi/pollutants?city=${encodeURIComponent(city)}`);
    return handleResponse(res);
  },

  async getHealthAdvisory(aqi) {
    const res = await fetch(`${API_BASE}/health-advisory?aqi=${encodeURIComponent(aqi)}`);
    return handleResponse(res);
  },

  async postAIChat(message, city = 'Kanpur', currentAqi = 100, pollutants = null) {
    const res = await fetch(`${API_BASE}/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        city,
        current_aqi: currentAqi,
        pollutants,
      }),
    });
    return handleResponse(res);
  },

  async searchLocations(query = '') {
    const res = await fetch(`${API_BASE}/locations/search?q=${encodeURIComponent(query)}`);
    return handleResponse(res);
  }
};
