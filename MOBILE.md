# Mobile Apps (Android & iOS)

Companion mobile UIs live under `mobile/`:

| Path | Stack | Purpose |
|------|--------|--------|
| `mobile/expo/` | Expo / React Native | Primary cross-platform companion (Android + iOS) |
| `mobile/flutter/` | Flutter | Alternative companion UI |

**Trading control remains on the Telegram Python bot.** Mobile is for docs + live status.

---

## Live bot status API

Run the status server next to the bot (same folder as `jarvis_memory.json`):

```bash
cd jarvis-trader-ecosystem
python status_server.py
# http://127.0.0.1:8787/health
# http://127.0.0.1:8787/status
```

Expo “Live bot” button calls this API.

| Client | Suggested `EXPO_PUBLIC_STATUS_URL` |
|--------|-------------------------------------|
| iOS simulator | `http://127.0.0.1:8787` |
| Android emulator | `http://10.0.2.2:8787` |
| Physical phone | `http://<your-computer-LAN-IP>:8787` (and set `STATUS_HOST=0.0.0.0`) |

```bash
# example for Android emulator
EXPO_PUBLIC_STATUS_URL=http://10.0.2.2:8787 npx expo start
```

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

### Production builds with EAS

```bash
cd mobile/expo
npm install -g eas-cli
eas login
eas build:configure
eas build -p android --profile production
eas build -p ios --profile production
```

App identifiers (`app.json`):
- Android: `com.beeniko.jarvistrader`
- iOS: `com.beeniko.jarvistrader`

---

## Flutter alternative

```bash
cd mobile/flutter
flutter pub get
flutter run
```

---

## Scope

One companion app for the main ecosystem is enough. Other repos do not each need a store app.

## Your ops checklist

1. Rotate credentials  
2. `python main.py` (bot) + `python status_server.py` (API)  
3. `npx expo start` (mobile)  
4. EAS when ready for stores  
