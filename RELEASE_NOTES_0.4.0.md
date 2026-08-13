# QBT 0.4.0 — Packaged Applications

QBT 0.4.0 converts the universal bridge into installable application distributions.

## Included

- Windows one-click `.exe` installer
- macOS `.dmg` containing `QBT Desktop.app`
- native Kotlin Android client
- native SwiftUI iPhone/iPad client
- Linux native `qbt-rs` binary archive
- automated release checksums
- packaged GitHub Release asset pipeline

## Security

QBT remains BYOK. No IBM Quantum, Azure Quantum, Apple, Android signing, or other private credentials are committed to or packaged in the repository. Mobile clients store only the endpoint/token a user chooses locally. Non-loopback QBT sidecars must use bearer authentication, and live provider submission remains an explicit operator opt-in.

## Apple / Android signing

The GitHub Release contains installable Android sideload output plus an unsigned Android release build, an iOS simulator app, and an unsigned device-target iOS app. Physical iPhone/TestFlight/App Store distribution requires the owner's Apple certificate and provisioning profile. Play Store distribution requires the owner's persistent Android signing key.
