#!/usr/bin/env python3
"""
revoke.py -- Bulk-revoke dangerous permissions from apps
Usage: python3 revoke.py                          # interactive
       python3 revoke.py --app com.facebook.katana  # single app
       python3 revoke.py --all-social              # all known social/ad apps
       python3 revoke.py --audit-first             # show before asking
"""
import subprocess, argparse, sys, re

DANGEROUS = [
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.ACCESS_BACKGROUND_LOCATION",
    "android.permission.READ_CONTACTS",
    "android.permission.GET_ACCOUNTS",
    "android.permission.READ_CALL_LOG",
    "android.permission.READ_SMS",
    "android.permission.RECORD_AUDIO",
    "android.permission.CAMERA",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.READ_MEDIA_IMAGES",
    "android.permission.BODY_SENSORS",
    "android.permission.ACTIVITY_RECOGNITION",
    "android.permission.BLUETOOTH_SCAN",
]

SOCIAL_AD_PACKAGES = [
    "com.facebook.katana", "com.facebook.orca", "com.facebook.appmanager",
    "com.instagram.android", "com.twitter.android", "com.snapchat.android",
    "com.tiktok.android", "com.zhiliaoapp.musically",
    "com.google.android.gm",  # Gmail
    "com.linkedin.android",
]

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_packages():
    out = adb("pm list packages")
    return {l.split(":")[1] for l in out.splitlines() if l.startswith("package:")}

def get_granted(pkg):
    out = adb(f"dumpsys package {pkg}")
    granted = []
    for line in out.splitlines():
        if "granted=true" in line:
            for p in DANGEROUS:
                if p in line:
                    granted.append(p)
    return granted

def revoke_all(pkg):
    granted = get_granted(pkg)
    if not granted:
        print(f"  {pkg}: nothing to revoke")
        return
    for perm in granted:
        r = adb(f"pm revoke {pkg} {perm}")
        short = perm.split(".")[-1]
        status = "✓" if "Success" in r or r == "" else "✗"
        print(f"  {status} {pkg.split('.')[-1]}: {short}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", help="Revoke from specific package")
    parser.add_argument("--all-social", action="store_true", help="Revoke from all known social/ad packages")
    parser.add_argument("--audit-first", action="store_true", help="Show granted perms before revoking")
    args = parser.parse_args()

    installed = get_packages()
    print("\n🔐 Permission Revoker")
    print("=" * 45)

    if args.app:
        targets = [args.app]
    elif args.all_social:
        targets = [p for p in SOCIAL_AD_PACKAGES if p in installed]
        print(f"Found {len(targets)} social/ad packages installed\n")
    else:
        # Interactive
        print("Installed packages (type package name or 'q' to quit):")
        print("Tip: use --all-social to revoke from all social apps at once\n")
        targets = []
        while True:
            pkg = input("Package (or q): ").strip()
            if pkg == 'q': break
            if pkg in installed:
                targets.append(pkg)
            else:
                print(f"  Not installed: {pkg}")

    if args.audit_first:
        print("\nCurrent granted dangerous permissions:\n")
        for pkg in targets:
            granted = get_granted(pkg)
            if granted:
                print(f"  {pkg}:")
                for p in granted:
                    print(f"    - {p.split('.')[-1]}")
        confirm = input("\nRevoke all of the above? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Aborted.")
            return

    print("\nRevoking permissions...\n")
    for pkg in targets:
        revoke_all(pkg)

    print("\n✅ Done.")

if __name__ == "__main__":
    main()
