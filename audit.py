#!/usr/bin/env python3
"""
android-permission-auditor
Audits all installed Android apps for dangerous permissions via ADB.
Generates a CLI report + optional HTML report.
No root required.
"""

import subprocess
import sys
import json
import os
import argparse
from datetime import datetime

DANGEROUS_PERMISSIONS = {
    "READ_CONTACTS":        "📇 Read your contacts",
    "WRITE_CONTACTS":       "📇 Modify your contacts",
    "READ_CALL_LOG":        "📞 Read call history",
    "WRITE_CALL_LOG":       "📞 Modify call history",
    "PROCESS_OUTGOING_CALLS": "📞 Intercept outgoing calls",
    "READ_SMS":             "💬 Read your SMS messages",
    "SEND_SMS":             "💬 Send SMS (costs money!)",
    "RECEIVE_SMS":          "💬 Intercept incoming SMS",
    "RECEIVE_MMS":          "💬 Intercept incoming MMS",
    "ACCESS_FINE_LOCATION": "📍 Precise GPS location",
    "ACCESS_COARSE_LOCATION": "📍 Approximate location",
    "ACCESS_BACKGROUND_LOCATION": "📍 Location in background",
    "RECORD_AUDIO":         "🎙️ Use your microphone",
    "CAMERA":               "📷 Use your camera",
    "READ_EXTERNAL_STORAGE":"💾 Read files/photos",
    "WRITE_EXTERNAL_STORAGE":"💾 Write files/photos",
    "READ_MEDIA_IMAGES":    "🖼️ Read images",
    "READ_MEDIA_VIDEO":     "🎬 Read videos",
    "READ_MEDIA_AUDIO":     "🎵 Read audio files",
    "GET_ACCOUNTS":         "👤 Access your accounts",
    "USE_BIOMETRIC":        "🔐 Use biometric sensors",
    "USE_FINGERPRINT":      "🔐 Use fingerprint sensor",
    "BODY_SENSORS":         "❤️ Read body sensors",
    "ACTIVITY_RECOGNITION": "🏃 Track physical activity",
    "READ_PHONE_STATE":     "📱 Read phone state & IMEI",
    "READ_PHONE_NUMBERS":   "📱 Read phone numbers",
    "CALL_PHONE":           "📞 Make calls without confirmation",
    "BLUETOOTH_SCAN":       "📡 Scan for nearby Bluetooth devices",
    "BLUETOOTH_CONNECT":    "📡 Connect to Bluetooth devices",
    "UWB_RANGING":          "📡 Ultra-wideband ranging",
    "NEARBY_WIFI_DEVICES":  "📶 Scan nearby Wi-Fi devices",
}

def run_adb(args, device=None):
    cmd = ["adb"]
    if device:
        cmd += ["-s", device]
    cmd += args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except FileNotFoundError:
        print("❌ ADB not found. Install Android Platform Tools first.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        return ""

def get_devices():
    output = run_adb(["devices"])
    lines = output.splitlines()[1:]
    devices = []
    for line in lines:
        if "\tdevice" in line:
            devices.append(line.split("\t")[0])
    return devices

def get_all_packages(device=None):
    output = run_adb(["shell", "pm", "list", "packages"], device)
    return [line.replace("package:", "").strip() for line in output.splitlines() if line.startswith("package:")]

def get_app_label(package, device=None):
    output = run_adb(["shell", "pm", "dump", package], device)
    for line in output.splitlines():
        if "labelRes=" in line or "label=" in line:
            parts = line.strip().split()
            for p in parts:
                if p.startswith("label="):
                    val = p.split("=", 1)[1]
                    if val and not val.startswith("0x"):
                        return val
    return package

def get_granted_dangerous_perms(package, device=None):
    output = run_adb(["shell", "dumpsys", "package", package], device)
    granted = []
    in_granted = False
    for line in output.splitlines():
        if "granted=true" in line:
            for perm_key in DANGEROUS_PERMISSIONS:
                if f"android.permission.{perm_key}" in line or perm_key in line:
                    granted.append(perm_key)
    return list(set(granted))

def audit(device=None, package_filter=None, third_party_only=True):
    print(f"\n🔍 Android Permission Auditor")
    print(f"   Connected device: {device or 'default'}")
    print(f"   Fetching installed packages...\n")

    packages = get_all_packages(device)
    
    if third_party_only:
        # Filter to third-party apps (not system apps)
        sys_output = run_adb(["shell", "pm", "list", "packages", "-s"], device)
        system_pkgs = set(line.replace("package:", "").strip() for line in sys_output.splitlines())
        packages = [p for p in packages if p not in system_pkgs]
        print(f"   Scanning {len(packages)} third-party apps (use --all to include system apps)\n")
    else:
        print(f"   Scanning {len(packages)} apps\n")

    if package_filter:
        packages = [p for p in packages if package_filter.lower() in p.lower()]

    results = []
    for i, pkg in enumerate(packages):
        perms = get_granted_dangerous_perms(pkg, device)
        if perms:
            results.append({"package": pkg, "permissions": perms})
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"   Progress: {i+1}/{len(packages)}...", end="\r")

    print(f"\n\n{'='*60}")
    print(f"  AUDIT RESULTS — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")

    if not results:
        print("  ✅ No apps with dangerous permissions found.")
        return results

    # Sort by number of permissions (most suspicious first)
    results.sort(key=lambda x: len(x["permissions"]), reverse=True)

    for app in results:
        pkg = app["package"]
        perms = app["permissions"]
        risk = "🔴 HIGH" if len(perms) >= 5 else "🟡 MEDIUM" if len(perms) >= 2 else "🟢 LOW"
        print(f"\n  {risk} — {pkg}")
        print(f"  {'─'*50}")
        for p in perms:
            desc = DANGEROUS_PERMISSIONS.get(p, p)
            print(f"    • {desc}")

    print(f"\n{'='*60}")
    print(f"  Total apps with dangerous permissions: {len(results)}")
    print(f"{'='*60}\n")

    return results

def generate_html_report(results, output_file="permission_audit.html"):
    high = [r for r in results if len(r["permissions"]) >= 5]
    medium = [r for r in results if 2 <= len(r["permissions"]) < 5]
    low = [r for r in results if len(r["permissions"]) < 2]

    cards = ""
    for app in results:
        pkg = app["package"]
        perms = app["permissions"]
        count = len(perms)
        color = "#e74c3c" if count >= 5 else "#f39c12" if count >= 2 else "#27ae60"
        label = "HIGH RISK" if count >= 5 else "MEDIUM RISK" if count >= 2 else "LOW RISK"
        perm_list = "".join(f"<li>{DANGEROUS_PERMISSIONS.get(p, p)}</li>" for p in perms)
        cards += f"""
        <div class="card">
          <div class="card-header" style="border-left: 4px solid {color}">
            <span class="pkg-name">{pkg}</span>
            <span class="badge" style="background:{color}">{label} ({count})</span>
          </div>
          <ul class="perm-list">{perm_list}</ul>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Android Permission Audit Report</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f0f0f; color: #e0e0e0; padding: 2rem; }}
  h1 {{ font-size: 2rem; margin-bottom: 0.5rem; color: #fff; }}
  .subtitle {{ color: #888; margin-bottom: 2rem; }}
  .stats {{ display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }}
  .stat {{ background: #1a1a1a; border-radius: 8px; padding: 1rem 1.5rem; flex: 1; min-width: 120px; }}
  .stat .num {{ font-size: 2rem; font-weight: bold; }}
  .stat .lbl {{ font-size: 0.8rem; color: #888; text-transform: uppercase; }}
  .card {{ background: #1a1a1a; border-radius: 8px; margin-bottom: 1rem; overflow: hidden; }}
  .card-header {{ display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem; background: #222; flex-wrap: wrap; gap: 0.5rem; }}
  .pkg-name {{ font-family: monospace; font-size: 0.9rem; word-break: break-all; }}
  .badge {{ font-size: 0.7rem; font-weight: bold; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; white-space: nowrap; }}
  .perm-list {{ list-style: none; padding: 0.75rem 1rem; }}
  .perm-list li {{ padding: 0.25rem 0; color: #ccc; font-size: 0.9rem; }}
  .perm-list li::before {{ content: "• "; color: #555; }}
  .footer {{ margin-top: 2rem; color: #555; font-size: 0.8rem; }}
</style>
</head>
<body>
<h1>🔍 Android Permission Audit</h1>
<p class="subtitle">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · android-permission-auditor</p>
<div class="stats">
  <div class="stat"><div class="num" style="color:#e74c3c">{len(high)}</div><div class="lbl">High Risk</div></div>
  <div class="stat"><div class="num" style="color:#f39c12">{len(medium)}</div><div class="lbl">Medium Risk</div></div>
  <div class="stat"><div class="num" style="color:#27ae60">{len(low)}</div><div class="lbl">Low Risk</div></div>
  <div class="stat"><div class="num">{len(results)}</div><div class="lbl">Total Apps</div></div>
</div>
{cards}
<p class="footer">android-permission-auditor · github.com/OutrageousStorm/android-permission-auditor</p>
</body>
</html>"""

    with open(output_file, "w") as f:
        f.write(html)
    print(f"📄 HTML report saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="🔍 Audit Android app permissions via ADB — no root required",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python audit.py                        # Audit all third-party apps
  python audit.py --all                  # Include system apps
  python audit.py --html                 # Also generate HTML report
  python audit.py --filter com.facebook  # Filter by package name
  python audit.py --device emulator-5554 # Target specific device
        """
    )
    parser.add_argument("--device", "-d", help="Target device serial (from adb devices)")
    parser.add_argument("--all", "-a", action="store_true", help="Include system apps")
    parser.add_argument("--filter", "-f", help="Filter packages by name")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--output", "-o", default="permission_audit.html", help="HTML output file (default: permission_audit.html)")
    parser.add_argument("--json", "-j", help="Save results as JSON to this file")
    args = parser.parse_args()

    devices = get_devices()
    if not devices:
        print("❌ No Android device connected. Connect via USB and enable USB Debugging.")
        sys.exit(1)

    device = args.device or devices[0]
    if len(devices) > 1 and not args.device:
        print(f"⚠️  Multiple devices found. Using: {device}")
        print(f"   Others: {', '.join(devices[1:])} — use --device to specify\n")

    results = audit(
        device=device,
        package_filter=args.filter,
        third_party_only=not args.all
    )

    if args.html:
        generate_html_report(results, args.output)

    if args.json:
        with open(args.json, "w") as f:
            json.dump(results, f, indent=2)
        print(f"📄 JSON results saved to: {args.json}")

if __name__ == "__main__":
    main()
