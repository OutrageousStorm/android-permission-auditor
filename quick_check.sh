#!/bin/bash
# quick_check.sh -- Fast permission checker for top dangerous permissions
# Usage: ./quick_check.sh [package]

PKG="${1}"

if [[ -z "$PKG" ]]; then
    echo "Usage: $0 <package>"
    echo ""
    echo "Example dangerous packages:"
    adb shell pm list packages -3 | head -10
    exit 1
fi

echo "🔍 Checking: $PKG"
echo ""

PERMS=(
    "ACCESS_FINE_LOCATION"
    "ACCESS_COARSE_LOCATION"
    "READ_CONTACTS"
    "RECORD_AUDIO"
    "CAMERA"
    "READ_SMS"
    "READ_CALL_LOG"
)

adb shell dumpsys package "$PKG" 2>/dev/null | grep -E "granted=true" | while read line; do
    for perm in "${PERMS[@]}"; do
        if echo "$line" | grep -q "$perm"; then
            echo "  ⚠️  $perm — GRANTED"
        fi
    done
done

echo ""
echo "To revoke: adb shell pm revoke $PKG android.permission.<PERMISSION>"
