# QBT 0.4.0 Packaged Application Checklist

This checklist is only marked complete when the corresponding GitHub Actions build or published GitHub Release has produced the expected artifact.

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
- [x] SHA-256 checksums are generated
- [x] GitHub Release `v0.4.0` is published from `main`
- [x] GitHub Release contains Windows, macOS, Android, iOS, Linux, and checksum assets

## Published assets

Release `v0.4.0`, titled `QBT 0.4.0 - Packaged Applications`, is published from main commit `93f1cf79e4594c05a096d87836b4fa544697bcdb`.

- `QBT-Windows-Setup-0.4.0.exe`
- `QBT-macOS-0.4.0.dmg`
- `QBT-Android-sideload-0.4.0.apk`
- `QBT-Android-unsigned-release-0.4.0.apk`
- `QBT-iOS-simulator-0.4.0.zip`
- `QBT-iOS-unsigned-device-0.4.0.zip`
- `qbt-rs-linux-x86_64-0.4.0.tar.gz`
- `SHA256SUMS.txt`

## Verification record

Release-branch Packaged Applications run `31673085726` completed successfully on product head `a34990e88087123b42156c4d5e2a15e8aaf3dec4`. Windows, macOS, Android, iOS, and Linux packaging jobs all completed successfully, and the core QBT compatibility workflows were green on the same product head.

After merge, main Packaged Applications run `31673486092` rebuilt Windows, macOS, Android, iOS, and Linux successfully. Release job `94363655112` downloaded the artifacts, generated SHA-256 checksums, and published GitHub Release `v0.4.0` successfully.

## Signing boundary

Apple physical-device/TestFlight/App Store distribution requires a real Apple development/distribution identity and provisioning profile. Android Play Store distribution requires a persistent project signing key. Those private identities are never fabricated or committed to this public repository. The public release therefore includes an iOS simulator build plus an unsigned device-target build, and both an installable Android sideload build and an unsigned Android release build for owner-controlled signing.
