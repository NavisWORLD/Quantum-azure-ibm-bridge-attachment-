export class QbtClient {
  constructor(baseUrl = "http://127.0.0.1:8766", token = "") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.token = token;
  }

  async request(path, options = {}) {
    const headers = new Headers(options.headers || {});
    headers.set("Accept", "application/json");
    if (options.body) headers.set("Content-Type", "application/json");
    if (this.token) headers.set("Authorization", `Bearer ${this.token}`);
    const response = await fetch(`${this.baseUrl}${path}`, { ...options, headers });
    const text = await response.text();
    let payload;
    try {
      payload = JSON.parse(text);
    } catch {
      throw new Error(`QBT returned non-JSON response: ${text}`);
    }
    if (!response.ok) {
      throw new Error(payload.error || `QBT HTTP ${response.status}`);
    }
    return payload;
  }

  health() {
    return this.request("/health");
  }

  status(provider = "simulator", seed = 42) {
    return this.request(
      `/v1/status?provider=${encodeURIComponent(provider)}&seed=${encodeURIComponent(seed)}`,
    );
  }

  sample({ provider = "simulator", shots = 1024, seed = 42 } = {}) {
    return this.request("/v1/sample", {
      method: "POST",
      body: JSON.stringify({ provider, shots, seed }),
    });
  }

  normalize(payload) {
    return this.request("/v1/normalize", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }
}
