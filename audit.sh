#!/bin/bash
# audit.sh -- Quick permission audit wrapper
[[ -z $(adb devices | grep device) ]] && echo "No device connected." && exit 1
echo "Scanning installed apps for dangerous permissions..."
python3 permission_audit.py "$@"
