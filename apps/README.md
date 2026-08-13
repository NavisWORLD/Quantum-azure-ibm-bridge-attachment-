# QBT Applications

QBT 0.4.0 adds application shells around the same provider-neutral QBT contract.

- `desktop/` contains the packaged Python/Tk desktop control application used for Windows and macOS builds.
- `android/` contains the native Kotlin Android client.
- `ios/` contains the native SwiftUI iPhone/iPad client.

The mobile applications are HTTP/JSON clients for a QBT sidecar you control. They do not embed IBM Quantum or Azure Quantum credentials.

See `../DISTRIBUTION.md` for build, installation, networking, signing, and release details.
