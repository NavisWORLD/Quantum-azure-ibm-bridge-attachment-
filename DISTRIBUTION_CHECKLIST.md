# QBT 0.4.0 Packaged Application Checklist

This checklist is only marked complete when the corresponding GitHub Actions build has produced the expected artifact on the release branch.

## Desktop

- [ ] Windows one-click installer builds as `QBT-Windows-Setup-0.4.0.exe`
- [ ] macOS app builds as `QBT Desktop.app`
- [ ] macOS disk image builds as `QBT-macOS-0.4.0.dmg`
- [ ] Linux native Rust CLI archive builds

## Mobile

- [ ] Native Kotlin Android app compiles
- [ ] Installable Android sideload APK is produced
- [ ] Android unsigned release APK is produced for owner signing
- [ ] Native SwiftUI iPhone/iPad app compiles for simulator
- [ ] Native SwiftUI iPhone/iPad app compiles for device target without signing
- [ ] iOS simulator app archive is produced
- [ ] iOS unsigned device app archive is produced for owner Apple signing

## Release

- [ ] All packaged application build jobs are green
- [ ] SHA-256 checksums are generated
- [ ] GitHub Release `v0.4.0` is published from `main`
- [ ] GitHub Release contains Windows, macOS, Android, iOS, Linux, and checksum assets

## Signing boundary

Apple physical-device/TestFlight/App Store distribution requires a real Apple development/distribution identity and provisioning profile. Android Play Store distribution requires a persistent project signing key. Those private identities are never fabricated or committed to this public repository.
