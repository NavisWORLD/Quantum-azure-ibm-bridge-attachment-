import { QbtClient } from "./qbt-client.mjs";

const baseUrl = process.argv[2] || "http://127.0.0.1:8766";
const client = new QbtClient(baseUrl);

const health = await client.health();
if (health.status !== "ok" || health.credentials_exposed !== false) {
  throw new Error("QBT health contract failed");
}

const sample = await client.sample({ provider: "simulator", shots: 128, seed: 7 });
if (sample.packet.active_sources !== 1) {
  throw new Error("QBT simulator did not return one active source");
}

const normalized = await client.normalize({
  provider: "javascript",
  backend: "smoke",
  mode: "simulator",
  counts: { 0: 64, 1: 64 },
  shots: 128,
});
if (Math.abs(normalized.state.entropy - 1.0) > 1e-12) {
  throw new Error("QBT normalization mismatch");
}

console.log("JavaScript/TypeScript QBT smoke: OK");
