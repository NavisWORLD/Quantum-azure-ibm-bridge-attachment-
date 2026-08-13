# QBT Language Compatibility Matrix

QBT does not claim that one repository can maintain bespoke provider implementations for every programming language ever created. Instead, it provides stable universal interfaces that make essentially any modern language interoperable with the same QBT contract.

## Compatibility layers

| Ecosystem | Recommended path | Repository support |
|---|---|---|
| Python | Native SDK | First-class implementation + CI |
| Rust | Native SDK | First-class implementation + CI |
| C | Native C ABI | Header + linked smoke test |
| C++ | C ABI + C++ wrapper | Header + linked smoke test |
| JavaScript | HTTP/JSON | Reference client + end-to-end CI |
| TypeScript | HTTP/JSON | Type declarations + JS runtime |
| Go | HTTP/JSON | Typed stdlib client + end-to-end CI |
| Java | HTTP/JSON | JDK HttpClient adapter + CI |
| Kotlin | JVM adapter | Uses the Java adapter directly |
| C# | HTTP/JSON or P/Invoke | .NET adapter + CI |
| F# / VB.NET | HTTP/JSON or P/Invoke | Same .NET contract |
| Swift | HTTP/JSON or C ABI | Native Swift client + macOS CI |
| Objective-C | C ABI | Directly includes `qbt.h` |
| PHP | HTTP/JSON | Reference client + CI |
| Ruby | HTTP/JSON | Reference client + CI |
| Perl | HTTP/JSON | Reference client + CI |
| Zig / Nim / D | C ABI | Standard C interop |
| Fortran | C ABI | `ISO_C_BINDING` compatible |
| Julia | HTTP/JSON or C ABI | `HTTP`/`Downloads` or `ccall` |
| R | HTTP/JSON | Any standard HTTP + JSON package |
| Dart / Flutter | HTTP/JSON | Standard `http`-style client |
| Lua | HTTP/JSON or C ABI | Any HTTP/JSON or FFI package |
| Haskell | HTTP/JSON or C ABI | Standard HTTP/FFI ecosystem |
| Scala / Clojure | JVM adapter | Uses Java adapter/HTTP contract |
| Elixir / Erlang | HTTP/JSON | Standard HTTP client |
| OCaml | HTTP/JSON or C ABI | Standard HTTP/C FFI |
| MATLAB / Octave | HTTP/JSON or C ABI | Web request or native library load |
| Bash / shell | HTTP/JSON | `curl` |
| PowerShell | HTTP/JSON | `Invoke-RestMethod` |

## Operating systems

The compatibility contract is platform-neutral. CI is designed to validate the universal sidecar on Linux, Windows, and macOS. Native C ABI artifacts are produced by Cargo for the target platform.

Typical Rust artifact names are:

- Linux: `libqbt_ffi.so`
- macOS: `libqbt_ffi.dylib`
- Windows: `qbt_ffi.dll` plus the platform import library produced by the Rust toolchain

## Why this is stronger than hundreds of duplicated SDKs

Provider SDKs and cloud authentication flows change over time. Duplicating IBM/Azure logic in dozens of languages would create inconsistent security and scientific behavior. QBT centralizes provider execution in the tested native core and freezes the downstream contract as JSON Schema + OpenAPI + C ABI.

That means adding a new host language usually requires only a small transport or FFI adapter. It does not require reimplementing entropy math, provenance hashing, fail-soft behavior, provider credentials, or control-state semantics.

## Universal fallback

If a language is not listed here, it is still supported when it can do either of these:

1. send an HTTP request and parse JSON
2. call a C-compatible dynamic/static library

Those two interfaces are the compatibility guarantee.
