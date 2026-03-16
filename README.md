# 🔍 Android Permission Auditor

> Audit every app on your Android for dangerous permissions — via ADB, no root required. CLI + HTML report.

[![Python](https://img.shields.io/badge/python-3.7+-blue?logo=python)](https://python.org)
[![ADB](https://img.shields.io/badge/requires-ADB-green?logo=android)](https://developer.android.com/tools/releases/platform-tools)
[![No Root](https://img.shields.io/badge/root-not%20required-brightgreen)](.)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Stop wondering what your apps are doing behind your back. **Android Permission Auditor** scans every installed app and tells you exactly which dangerous permissions they've been granted — in seconds.

---

## ✨ Features

- 🔍 Scans all installed apps (third-party or all including system)
- 🎯 Detects 30+ dangerous permissions (camera, microphone, location, SMS, etc.)
- 🔴 Risk scoring — HIGH / MEDIUM / LOW per app
- 📄 Beautiful HTML report with dark theme
- 💾 JSON export for scripting/automation
- 🎛️ Filter by package name
- 📱 Multi-device support
- ⚡ No root required — pure ADB

---

## 📦 Requirements

- Python 3.7+
- [ADB (Android Platform Tools)](https://developer.android.com/tools/releases/platform-tools)
- USB Debugging enabled on your Android device

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/OutrageousStorm/android-permission-auditor
cd android-permission-auditor

# Connect your phone via USB, enable USB Debugging, then:
python audit.py

# Generate an HTML report too
python audit.py --html

# Include system apps
python audit.py --all --html

# Filter by a specific app
python audit.py --filter com.facebook
```

---

## 📊 Example Output

```
🔍 Android Permission Auditor
   Connected device: R3CN80XXXXX
   Scanning 87 third-party apps

============================================================
  AUDIT RESULTS — 2025-01-15 14:32
============================================================

  🔴 HIGH — com.facebook.katana
  ──────────────────────────────────────────────────────
    • 📍 Precise GPS location
    • 🎙️ Use your microphone
    • 📷 Use your camera
    • 📇 Read your contacts
    • 💬 Read your SMS messages
    • 💾 Read files/photos

  🟡 MEDIUM — com.instagram.android
  ──────────────────────────────────────────────────────
    • 📍 Precise GPS location
    • 📷 Use your camera
    • 🎙️ Use your microphone
```

---

## 🛡️ Dangerous Permissions Detected

| Permission | Risk |
|------------|------|
| `ACCESS_FINE_LOCATION` | Precise GPS tracking |
| `RECORD_AUDIO` | Microphone access |
| `CAMERA` | Camera access |
| `READ_SMS` | Read all text messages |
| `SEND_SMS` | Send SMS (could cost money) |
| `READ_CONTACTS` | Access your contact list |
| `READ_CALL_LOG` | See all call history |
| `READ_PHONE_STATE` | Read IMEI & device identifiers |
| `ACCESS_BACKGROUND_LOCATION` | Track you even when app is closed |
| `PROCESS_OUTGOING_CALLS` | Intercept your calls |
| ... and 20+ more | |

---

## 📄 HTML Report

Run with `--html` to generate a beautiful dark-themed report you can open in any browser:

```bash
python audit.py --html --output my_audit.html
```

---

## 🔧 Full Usage

```
usage: audit.py [-h] [--device DEVICE] [--all] [--filter FILTER]
                [--html] [--output OUTPUT] [--json JSON]

Options:
  --device, -d    Target device serial (from adb devices)
  --all, -a       Include system apps
  --filter, -f    Filter packages by name substring
  --html          Generate HTML report
  --output, -o    HTML output filename (default: permission_audit.html)
  --json, -j      Save results as JSON
```

---

## 🤝 Contributing

PRs welcome! Ideas:
- Watch mode (re-audit after installs)
- Permission diff between audits
- ADB over Wi-Fi support
- App store lookup integration

---

## 📜 License

MIT — free to use, modify, and share.

---

*Built with ❤️ for Android privacy nerds. No data ever leaves your machine.*
