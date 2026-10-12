# Mobile Apps (Android & iOS)

Companion mobile UIs live under `mobile/`:

| Path | Stack | Purpose |
|------|--------|--------|
| `mobile/expo/` | Expo / React Native | Primary cross-platform companion (Android + iOS) |
| `mobile/flutter/` | Flutter | Alternative companion UI |

These apps show project docs/status. **Trading control remains on the Telegram Python bot.** They are not full trading terminals.

---

## Expo (recommended for both Android and iOS)

### Prerequisites
- Node.js 18+
- Expo CLI / `npx expo`
- For device builds: Expo account + EAS CLI
- iOS store builds: Apple Developer account
- Android store builds: Google Play Developer account + keystore

### Local development

```bash
cd mobile/expo
npm install
npx expo start
```

Then press `a` for Android emulator, `i` for iOS simulator, or scan the QR code with Expo Go.

### Production builds with EAS (Android APK/AAB + iOS IPA)

```bash
cd mobile/expo
npm install -g eas-cli
eas login
eas build:configure

# Android
eas build -p android --profile production

# iOS (requires Apple Developer Program)
eas build -p ios --profile production
```

You must complete signing setup in the Expo / Apple / Google consoles. Store submission cannot be finished from this environment without your developer accounts and certificates.

App identifiers (see `app.json`):
- Android package: `com.beeniko.jarvistrader`
- iOS bundle: `com.beeniko.jarvistrader`

---

## Flutter alternative

```bash
cd mobile/flutter
flutter pub get
flutter run                # device/emulator
flutter build apk          # Android APK
flutter build appbundle    # Play Store
flutter build ipa          # iOS (macOS + Xcode + Apple account required)
```

---

## Scope across all repositories

| Repository | Mobile status |
|------------|---------------|
| **jarvis-trader-ecosystem** | Expo + Flutter companions updated |
| jarvis-ai | Separate frontend / historical Flutter paths may exist; not the primary mobile target |
| jarvistrader | Web (Next.js), not native |
| Other repos | No dedicated mobile apps; use the main ecosystem companion |

Building and publishing **seven separate store apps** is not appropriate: one companion app for the main trading system is the correct product approach.

---

## What cannot be done from this assistant environment

1. Keep long-running Telegram/trading bots online for you (no persistent process hosting; needs your secrets and a server/VPS).
2. Sign and upload App Store / Play Store binaries (requires your Apple/Google accounts and signing keys).
3. End-to-end live trading tests without your rotated tokens and risk acceptance.

---

## Recommended next steps for you

1. Rotate previously exposed credentials.
2. Run the Python bot locally or on a VPS with `python main.py` after `scripts/check_config.py`.
3. Run the Expo app with `npx expo start` for a mobile companion.
4. When ready for stores, use EAS builds and your developer accounts.
