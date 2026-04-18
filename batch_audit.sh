#!/bin/bash
# batch_audit.sh -- Audit permission patterns across multiple devices
# Usage: ./batch_audit.sh
# Connects to each device and runs permission audit, saves results

RESULTS_DIR="audit_results_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULTS_DIR"

echo "🔍 Batch Permission Auditor"
echo "Scanning all connected devices...\n"

adb devices | tail -n +2 | grep -v "^$" | while read -r SERIAL _; do
    if [[ "$SERIAL" == "emulator"* ]] || [[ "$SERIAL" == "127.0.0.1"* ]]; then
        continue
    fi

    MODEL=$(adb -s "$SERIAL" shell getprop ro.product.model 2>/dev/null)
    ANDROID=$(adb -s "$SERIAL" shell getprop ro.build.version.release 2>/dev/null)

    echo "📱 $MODEL (Android $ANDROID) [$SERIAL]"

    # Run permission audit
    python3 permission_audit.py --csv "$RESULTS_DIR/${SERIAL}_perms.csv" 2>/dev/null &

done

wait

echo "\n✅ Results saved to: $RESULTS_DIR"
echo "Files:"
ls -lh "$RESULTS_DIR"
