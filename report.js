#!/usr/bin/env node
/**
 * report.js -- Generate HTML permission audit report from ADB
 * Usage: node report.js > audit.html
 */
const { execSync } = require('child_process');

function adb(cmd) {
    try {
        return execSync(`adb shell ${cmd}`, { encoding: 'utf-8' }).trim();
    } catch (e) {
        return '';
    }
}

const DANGEROUS = [
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.READ_CONTACTS",
    "android.permission.RECORD_AUDIO",
    "android.permission.CAMERA",
];

const packages = adb("pm list packages -3").split('\n')
    .map(l => l.replace('package:', ''))
    .filter(p => p);

const auditData = [];
for (const pkg of packages) {
    const perms = adb(`dumpsys package ${pkg}`);
    const dangerous = [];
    for (const perm of DANGEROUS) {
        if (perms.includes(perm) && perms.includes("granted=true")) {
            dangerous.push(perm.split('.').pop());
        }
    }
    if (dangerous.length > 0) {
        auditData.push({ pkg, dangerous });
    }
}

const html = `<!DOCTYPE html>
<html>
<head>
    <title>Android Permission Audit Report</title>
    <style>
        body { font-family: sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #d32f2f; }
        table { width: 100%; border-collapse: collapse; background: white; }
        th, td { padding: 10px; text-align: left; border: 1px solid #ddd; }
        th { background: #d32f2f; color: white; }
        tr:hover { background: #f9f9f9; }
        .badge { background: #ffcdd2; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>🔐 Android Permission Audit Report</h1>
    <p>Generated: ${new Date().toISOString()}</p>
    <p><strong>${auditData.length}</strong> apps with dangerous permissions</p>
    
    <table>
        <tr>
            <th>Package</th>
            <th>Dangerous Permissions</th>
            <th>Action</th>
        </tr>
        ${auditData.map(a => `
        <tr>
            <td><code>${a.pkg}</code></td>
            <td>${a.dangerous.map(p => `<span class="badge">${p}</span>`).join(' ')}</td>
            <td><code>adb shell pm revoke ${a.pkg} android.permission.X</code></td>
        </tr>
        `).join('')}
    </table>
</body>
</html>`;

console.log(html);
