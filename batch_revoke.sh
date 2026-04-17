#!/bin/bash
# batch_revoke.sh -- Revoke multiple permissions from multiple apps via ADB

set -e

DANGEROUS_PERMS=(
    "android.permission.ACCESS_FINE_LOCATION"
    "android.permission.ACCESS_COARSE_LOCATION"
    "android.permission.READ_CONTACTS"
    "android.permission.RECORD_AUDIO"
    "android.permission.CAMERA"
    "android.permission.READ_SMS"
    "android.permission.READ_CALL_LOG"
)

PACKAGES=(
    "com.facebook.katana"
    "com.instagram.android"
    "com.twitter.android"
    "com.tiktok.android"
)

echo "🔐 Batch Permission Revoker"
echo "From: ${#PACKAGES[@]} apps"
echo "Perms: ${#DANGEROUS_PERMS[@]} each"
echo ""

revoked=0; failed=0
for pkg in "${PACKAGES[@]}"; do
    for perm in "${DANGEROUS_PERMS[@]}"; do
        result=$(adb shell pm revoke "$pkg" "$perm" 2>&1)
        if [[ "$result" == "" || "$result" == "Success" ]]; then
            short_perm=$(echo "$perm" | rev | cut -d. -f1 | rev)
            echo "  ✓ $pkg / $short_perm"
            ((revoked++))
        else
            ((failed++))
        fi
    done
done

echo ""
echo "✅ Revoked: $revoked   ❌ Failed: $failed"
