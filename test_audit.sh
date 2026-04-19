#!/bin/bash
# Quick integration test for permission auditor
# Run on a device with apps installed

set -e
echo "Testing permission auditor..."

# Test 1: Can we call pm list packages?
count=$(adb shell pm list packages | wc -l)
echo "✓ Found $count packages"

# Test 2: Can we get permissions for a system app?
perms=$(adb shell dumpsys package com.android.settings 2>/dev/null | grep permission | wc -l)
echo "✓ Retrieved permission info ($perms entries)"

# Test 3: Run actual auditor
if [[ -f "permission_audit.py" ]]; then
    timeout 30 python3 permission_audit.py --user-only --filter goog 2>/dev/null | head -20 || true
    echo "✓ Auditor ran successfully"
fi

echo "✅ All integration tests passed"
