# Android Permissions Explained

## Critical (UID, Contacts, SMS, Phone)

| Permission | Why risky | Apps that legitimately need it |
|------------|----------|-------------------------------|
| `READ_CONTACTS` | Full contact list access | Phone, Messaging, Social media (for @mentions) |
| `WRITE_CONTACTS` | Can modify/delete contacts | Contact apps, backup apps |
| `READ_CALL_LOG` | History of all calls | Phone, Dialer, Call recording apps |
| `WRITE_CALL_LOG` | Can delete call history | Some call management apps |
| `READ_SMS` | Access to text messages | SMS backup apps, some messengers |
| `SEND_SMS` | Can send SMS, costs money | Messaging, OTP verification apps |
| `READ_PHONE_STATE` | Phone number, call state | Phone, SIP clients |
| `GET_ACCOUNTS` | List all accounts on device | Google Play, corporate auth apps |

**Risk level: CRITICAL** — Revoke from everything except core apps.

## Location & Movement

| Permission | Why risky | Legit uses |
|------------|----------|-----------|
| `ACCESS_FINE_LOCATION` | GPS coordinates, accurate to ~5m | Maps, Uber, weather (with location) |
| `ACCESS_COARSE_LOCATION` | WiFi/cell tower location, ~500m | Same as above |
| `ACCESS_BACKGROUND_LOCATION` | Location even when app is closed | Fitness trackers, delivery apps, some maps |
| `ACTIVITY_RECOGNITION` | Step count, movement detection | Fitness apps, pedometers |
| `BODY_SENSORS` | Accelerometer, gyro, compass | Fitness, navigation, games |

**Risk level: HIGH** — Revoke from social media, news, ad trackers.

## Privacy-Threatening

| Permission | Why risky | Legit uses |
|------------|----------|-----------|
| `CAMERA` | Can spy via camera | Camera app, video calls, scanning |
| `RECORD_AUDIO` | Can record conversations | Voice calls, voice notes, music apps |
| `READ_EXTERNAL_STORAGE` | Access to all your files | Photo editors, file managers |
| `READ_MEDIA_IMAGES` | All photos on device | Gallery, photo editors |
| `READ_MEDIA_VIDEO` | All videos on device | Video editors, galleries |
| `READ_MEDIA_AUDIO` | All music files | Music players, podcasters |
| `BLUETOOTH_SCAN` | Detect nearby Bluetooth devices | Bluetooth manager, some smartwatch apps |
| `BLUETOOTH_CONNECT` | Connect to Bluetooth devices | Smart speakers, headphones, cars |
| `READ_CALENDAR` | Calendar events, appointments | Calendar app, some organizers |

**Risk level: HIGH** — Only grant to the intended app.

## Low-Risk But Monitor

| Permission | Risk |
|-----------|------|
| `INTERNET` | Necessary for most apps; monitor with NetGuard |
| `ACCESS_WIFI_STATE` | Know if WiFi is connected; low risk |
| `CHANGE_WIFI_STATE` | Toggle WiFi; low risk |
| `ACCESS_NETWORK_STATE` | Know if device is online; low risk |
| `VIBRATE` | Vibration motor control; low risk |

---

## Revocation Strategy

**Do this for every app:**
1. `READ_CONTACTS` → Revoke unless it's a contact/messaging app
2. `READ_CALL_LOG` → Revoke unless it's a phone app
3. `ACCESS_FINE_LOCATION` → Revoke from social media, news, games, ads
4. `CAMERA` → Revoke unless it's a camera or video call app
5. `RECORD_AUDIO` → Revoke from everything except voice apps
6. `GET_ACCOUNTS` → Revoke from most apps (Gmail, Google services exempt)

**Use the audit tool:**
```bash
python3 permission_audit.py --csv risky_perms.csv
python3 revoke.py --all-social    # Remove location/contacts from FB, Insta, TikTok, etc.
```
