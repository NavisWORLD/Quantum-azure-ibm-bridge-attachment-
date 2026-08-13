# QBT Universal Protocol 1.0

QBT has two universal compatibility surfaces:

1. JSON over HTTP through the local QBT sidecar.
2. A stable C ABI provided by the native Rust `qbt-ffi` crate.

The Python and Rust implementations remain first-class native SDKs. Other languages can use a typed adapter, call the HTTP contract directly, or call the C ABI.

## HTTP sidecar

Start locally:

```bash
qbt serve --host 127.0.0.1 --port 8766
```

The sidecar binds to loopback by default. It refuses a non-loopback bind unless `QBT_SIDECAR_TOKEN` is configured. Provider credentials are never returned by the API.

Endpoints:

- `GET /health`
- `GET /v1/status?provider=simulator|ibm|azure`
- `POST /v1/sample`
- `POST /v1/normalize`

Sample request:

```json
{"provider":"simulator","shots":1024,"seed":42}
```

Normalize request:

```json
{
  "provider":"external",
  "backend":"my-backend",
  "mode":"hardware",
  "counts":{"0":512,"1":512},
  "shots":1024,
  "job_id":"optional-provider-job-id",
  "metadata":{}
}
```

`QBT_ALLOW_ORIGIN` can opt into an explicit browser CORS origin. CORS is disabled by default.

## Canonical data contract

`spec/qbt-state.schema.json` defines `QuantumState`.

`spec/qbt-control-packet.schema.json` defines `ControlPacket`.

The four-element normalized vector is:

1. normalized Shannon entropy
2. hardware-source flag
3. logarithmic shot reliability
4. quality confidence

Every value is bounded to `[0, 1]`.

## C ABI

The Rust FFI crate exports:

- `qbt_version`
- `qbt_simulator_packet`
- `qbt_normalize_counts_json`
- `qbt_free_string`

See `rust/qbt-ffi/include/qbt.h`.

Any language with C FFI support can embed this interface without Python.

## Compatibility principle

A language-specific wrapper must not invent a new QBT state format. It consumes or produces the canonical JSON/C ABI contract so all languages remain interoperable.
