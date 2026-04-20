#!/usr/bin/env python3
"""report_gen.py -- Generate HTML permission audit report"""
import subprocess, argparse, html
from datetime import datetime

DANGEROUS = [
    "ACCESS_FINE_LOCATION", "READ_CONTACTS", "GET_ACCOUNTS",
    "RECORD_AUDIO", "CAMERA", "READ_SMS", "READ_CALL_LOG",
]

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="report.html")
    args = parser.parse_args()

    pkgs = adb("pm list packages -3").split("\n")
    pkgs = [p.split(":")[1] for p in pkgs if p.startswith("package:")]
    
    results = []
    for pkg in pkgs:
        out = adb(f"dumpsys package {pkg}")
        for d in DANGEROUS:
            if f"android.permission.{d}" in out and "granted=true" in out:
                results.append((pkg, d))

    html = "<html><head><title>Report</title></head><body>"
    html += f"<h1>Permission Audit</h1>"
    html += f"<p>Packages: {len(pkgs)}, Risky: {len(set(r[0] for r in results))}</p>"
    html += "<table border=1><tr><th>App</th><th>Permission</th></tr>"
    for pkg, perm in sorted(set(results)):
        html += f"<tr><td>{html.escape(pkg)}</td><td>{perm}</td></tr>"
    html += "</table></body></html>"

    with open(args.output, 'w') as f:
        f.write(html)
    print(f"Report: {args.output}")

if __name__ == "__main__":
    main()
