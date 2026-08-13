export type ExecutionMode = "hardware" | "simulator" | "archive" | "fallback";

export interface Quality {
  quality_class: string;
  confidence: number | null;
}

export interface QuantumState {
  qbt_version: "1.0";
  provider: string;
  backend: string;
  execution_mode: ExecutionMode;
  timestamp: string;
  job_id: string | null;
  shots: number;
  entropy: number;
  normalized_vector: [number, number, number, number];
  result_digest: string;
  provenance: Record<string, unknown>;
  quality: Quality;
}

export interface ControlPacket {
  qbt_version: "1.0";
  active_sources: number;
  quantum_mix: number;
  states: QuantumState[];
  provider_errors: Record<string, string>;
}

export interface SampleResponse {
  connection: Record<string, unknown>;
  packet: ControlPacket;
}

export interface SampleOptions {
  provider?: "simulator" | "ibm" | "azure";
  shots?: number;
  seed?: number;
}

export class QbtClient {
  constructor(baseUrl?: string, token?: string);
  health(): Promise<Record<string, unknown>>;
  status(provider?: string, seed?: number): Promise<Record<string, unknown>>;
  sample(options?: SampleOptions): Promise<SampleResponse>;
  normalize(payload: Record<string, unknown>): Promise<{ state: QuantumState }>;
}
