#!/bin/bash
# batch_audit.sh -- Audit permissions on multiple devices
# Usage: ./batch_audit.sh [output_dir]
set -e

OUT="${1:-.}"
mkdir -p "$OUT"

echo "🔍 Multi-Device Permission Audit"
echo "Waiting for connected devices..."
sleep 1

while IFS= read -r line; do
    [[ "$line" =~ "device" ]] || continue
    serial=$(echo "$line" | awk '{print $1}')
    [[ -z "$serial" ]] && continue
    
    echo "Auditing: $serial"
    model=$(adb -s "$serial" shell getprop ro.product.model 2>/dev/null || echo "unknown")
    python3 permission_audit.py --csv "$OUT/${serial}_${model}_permissions.csv" 2>/dev/null || true
done < <(adb devices)

echo "✅ Audits complete. Results in: $OUT/"
ls -lh "$OUT"
