# QBT Language Bindings

QBT uses one canonical data contract and multiple transport/embedding paths instead of duplicating provider logic independently in every language.

## First-class native SDKs

- Python: `src/qbt_bridge/`
- Rust: `rust/qbt-bridge/`

## Universal HTTP/JSON path

Run:

```bash
qbt serve --host 127.0.0.1 --port 8766
```

Then any language that can perform HTTP and parse JSON can use:

- `GET /health`
- `GET /v1/status`
- `POST /v1/sample`
- `POST /v1/normalize`

Typed/reference adapters in this repository cover JavaScript/TypeScript, Go, JVM/Java/Kotlin, C#/.NET, Swift, PHP, Ruby, and Perl.

## Universal native FFI path

Build:

```bash
cargo build -p qbt-ffi --release
```

Headers:

- C: `rust/qbt-ffi/include/qbt.h`
- C++: `rust/qbt-ffi/include/qbt.hpp`

A stable C ABI makes the native QBT core callable from C, C++, Objective-C, Zig, Nim, D, Fortran `ISO_C_BINDING`, Julia `ccall`, Swift, .NET P/Invoke, JVM/JNA or JNI, and other FFI-capable runtimes.

## Contract rule

Every binding must preserve the schemas under `spec/`. Do not fork the meaning of `QuantumState`, `ControlPacket`, execution modes, normalized vectors, provenance, or error reporting per language.

## Credentials

Bindings never contain IBM/Azure credentials. The QBT process/provider owns user-supplied credentials. HTTP and FFI responses contain normalized state and provenance, never raw API keys.
