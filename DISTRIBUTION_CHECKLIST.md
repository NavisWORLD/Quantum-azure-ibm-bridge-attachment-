# QBT 0.4.0 Packaged Application Checklist

This checklist is only marked complete when the corresponding GitHub Actions build has produced the expected artifact on the release branch.

## Desktop

- [x] Windows one-click installer builds as `QBT-Windows-Setup-0.4.0.exe`
- [x] macOS app builds as `QBT Desktop.app`
- [x] macOS disk image builds as `QBT-macOS-0.4.0.dmg`
- [x] Linux native Rust CLI archive builds

## Mobile

- [x] Native Kotlin Android app compiles
- [x] Installable Android sideload APK is produced
- [x] Android unsigned release APK is produced for owner signing
- [x] Native SwiftUI iPhone/iPad app compiles for simulator
- [x] Native SwiftUI iPhone/iPad app compiles for device target without signing
- [x] iOS simulator app archive is produced
- [x] iOS unsigned device app archive is produced for owner Apple signing

## Release

- [x] All packaged application build jobs are green
- [ ] SHA-256 checksums are generated
- [ ] GitHub Release `v0.4.0` is published from `main`
- [ ] GitHub Release contains Windows, macOS, Android, iOS, Linux, and checksum assets

## Verification record

Packaged Applications run `31673085726` completed successfully on release-branch head `a34990e88087123b42156c4d5e2a15e8aaf3dec4`. Windows, macOS, Android, iOS, and Linux packaging jobs all completed successfully. Core CI, Language Bindings, Platform Compatibility, Swift Compatibility, and PowerShell Compatibility were also green on the same head.

## Signing boundary

Apple physical-device/TestFlight/App Store distribution requires a real Apple development/distribution identity and provisioning profile. Android Play Store distribution requires a persistent project signing key. Those private identities are never fabricated or committed to this public repository.
