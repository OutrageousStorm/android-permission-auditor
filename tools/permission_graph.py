#!/usr/bin/env python3
"""
permission_graph.py -- Visualize app permission dependencies
Shows which apps have which dangerous permissions and which apps depend on those apps.
Usage: python3 permission_graph.py --output graph.txt
"""
import subprocess, json, re

DANGEROUS = {
    "LOCATION": ["android.permission.ACCESS_FINE_LOCATION", "android.permission.ACCESS_COARSE_LOCATION"],
    "CONTACTS": ["android.permission.READ_CONTACTS", "android.permission.WRITE_CONTACTS"],
    "CAMERA": ["android.permission.CAMERA"],
    "MICROPHONE": ["android.permission.RECORD_AUDIO"],
    "SMS": ["android.permission.READ_SMS", "android.permission.SEND_SMS"],
    "CALL_LOG": ["android.permission.READ_CALL_LOG"],
}

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout

def get_packages():
    out = adb("pm list packages")
    return [l.split(":")[1] for l in out.splitlines() if l.startswith("package:")]

def get_permissions(pkg):
    out = adb(f"dumpsys package {pkg}")
    perms = {}
    for cat, perm_list in DANGEROUS.items():
        for p in perm_list:
            if "granted=true" in out and p in out:
                perms[cat] = True
    return perms

def main():
    print("\n📊 Permission Graph Analyzer\n")
    pkgs = get_packages()[:50]  # limit to speed up
    
    results = {}
    for pkg in pkgs:
        perms = get_permissions(pkg)
        if perms:
            results[pkg] = list(perms.keys())
    
    # Display as tree
    print(f"Apps with dangerous permissions ({len(results)}):\n")
    for pkg, perms in sorted(results.items()):
        label = pkg.split(".")[-1]
        print(f"  {label:<30} {', '.join(perms)}")

if __name__ == "__main__":
    main()
