#!/usr/bin/env python3
"""interactive.py -- Interactive permission manager"""
import subprocess

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout

PERMS = [("LOCATION", "android.permission.ACCESS_FINE_LOCATION"),
         ("CAMERA", "android.permission.CAMERA"),
         ("MIC", "android.permission.RECORD_AUDIO")]

pkgs = [l.split(":")[1] for l in adb("pm list packages -3").splitlines() if l.startswith("package:")]

for pkg in pkgs[:3]:
    print(f"\n{pkg.split('.')[-1]}")
    for short, full in PERMS:
        granted = "granted=true" in adb(f"dumpsys package {pkg}")
        print(f"  {'✅' if granted else '❌'} {short}")
