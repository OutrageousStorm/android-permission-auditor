#!/usr/bin/env python3
"""
watch.py -- Continuously monitor for new dangerous permission grants on a connected device.
Alerts you in real-time when any app is granted a dangerous permission.
Usage: python3 watch.py [--interval 30]
"""
import subprocess, time, argparse, json
from pathlib import Path

DANGEROUS = [
    "ACCESS_FINE_LOCATION","ACCESS_COARSE_LOCATION","ACCESS_BACKGROUND_LOCATION",
    "READ_CONTACTS","RECORD_AUDIO","CAMERA","READ_SMS","READ_CALL_LOG",
    "GET_ACCOUNTS","BODY_SENSORS","ACTIVITY_RECOGNITION","BLUETOOTH_SCAN",
    "READ_MEDIA_IMAGES","READ_MEDIA_VIDEO","READ_EXTERNAL_STORAGE",
]

SNAPSHOT_FILE = Path("/tmp/perm_snapshot.json")

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout

def snapshot():
    raw = adb("pm list packages")
    pkgs = [l.split(":")[1].strip() for l in raw.splitlines() if l.startswith("package:")]
    state = {}
    for pkg in pkgs:
        dump = adb(f"dumpsys package {pkg}")
        granted = [p for p in DANGEROUS if f"android.permission.{p}" in dump and "granted=true" in dump]
        if granted:
            state[pkg] = granted
    return state

def diff(old, new):
    changes = []
    for pkg, perms in new.items():
        old_perms = set(old.get(pkg, []))
        new_perms = set(perms)
        added = new_perms - old_perms
        removed = old_perms - new_perms
        for p in added:   changes.append(("GRANTED", pkg, p))
        for p in removed: changes.append(("REVOKED", pkg, p))
    for pkg in old:
        if pkg not in new:
            for p in old[pkg]: changes.append(("APP_REMOVED", pkg, p))
    return changes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=30, help="Poll interval in seconds")
    args = parser.parse_args()

    print(f"👁️  Permission Watcher (polling every {args.interval}s) — Ctrl+C to stop\n")
    print("Taking initial snapshot...")
    prev = snapshot()
    print(f"Watching {len(prev)} apps with dangerous permissions\n")

    try:
        while True:
            time.sleep(args.interval)
            curr = snapshot()
            changes = diff(prev, curr)
            for kind, pkg, perm in changes:
                icon = "🔴" if kind == "GRANTED" else "✅" if kind == "REVOKED" else "📦"
                print(f"  {icon} [{kind}] {pkg.split('.')[-1]} — {perm}")
            prev = curr
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
