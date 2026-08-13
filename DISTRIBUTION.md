# QBT 0.4.0 Distribution Guide

QBT 0.4.0 adds packaged desktop installers, native mobile clients, and an automated GitHub Release pipeline.

## Published artifacts

- `QBT-Windows-Setup-0.4.0.exe` — one-click Windows installer containing QBT Desktop and the native Rust `qbt-rs` CLI.
- `QBT-macOS-0.4.0.dmg` — macOS disk image containing `QBT Desktop.app`, `qbt-rs`, README, distribution guide, and license.
- `QBT-Android-sideload-0.4.0.apk` — installable Android build signed with the standard Android debug signing flow for direct testing/sideloading.
- `QBT-Android-unsigned-release-0.4.0.apk` — release-variant Android APK for an owner/team to sign with its persistent Play/distribution key.
- `QBT-iOS-simulator-0.4.0.zip` — compiled SwiftUI iPhone/iPad simulator application.
- `QBT-iOS-unsigned-device-0.4.0.zip` — compiled iPhone/iPad device application built without signing, ready for an Apple developer/team signing step.
- `qbt-rs-linux-x86_64-0.4.0.tar.gz` — native Linux Rust CLI.
- `SHA256SUMS.txt` — checksums for all release artifacts.

## Windows

Run `QBT-Windows-Setup-0.4.0.exe`. The installer places QBT Desktop and `qbt-rs.exe` under the user's Program Files-compatible application location and creates Start Menu shortcuts. No IBM/Azure keys are bundled.

## macOS

Open `QBT-macOS-0.4.0.dmg`, then drag or copy `QBT Desktop.app` to Applications. CI uses ad-hoc signing only because Developer ID signing/notarization requires the repository owner's Apple signing identity. Gatekeeper may therefore require right-click → Open for the public unsigned build. A production-distributed notarized build can use the same source/workflow once Apple signing secrets are configured.

## Android

The sideload APK is installable for direct testing. The unsigned release APK is intended for permanent signing with the project owner's Android/Play signing key. The app is a native Kotlin Android client and stores endpoint/token settings in app-private SharedPreferences.

## iPhone / iPad

The repository contains a native SwiftUI application and CI compiles both simulator and device targets. Apple requires a development/distribution certificate and provisioning profile to install on a physical device or distribute via TestFlight/App Store. Public CI deliberately does not invent or embed an Apple identity. Use the unsigned device artifact as the input to your Apple signing/export pipeline.

## Mobile connection model

Mobile apps are clients for the QBT HTTP/JSON sidecar. They do not contain provider credentials. For LAN use:

```bash
export QBT_SIDECAR_TOKEN='use-a-long-random-token'
qbt serve --host 0.0.0.0 --port 8766
```

Enter the machine's LAN or HTTPS URL and the same bearer token in the app. Live IBM/Azure submission through the sidecar is still disabled unless the operator explicitly enables it.

## Reproducible release build

`.github/workflows/distribution.yml` validates all application targets on pull requests. When the `v0.4.0` release marker reaches `main`, the same workflow builds every artifact and publishes/updates the `v0.4.0` GitHub Release with SHA-256 checksums.

## Signing boundary

A build being functional and a build being store-signed are different claims. Windows installer generation, macOS DMG creation, Android application compilation, and iOS application compilation are automated in public CI. Apple notarization/App Store signing and permanent Android Play signing remain owner-controlled identity operations and must use private signing credentials.
