use regex::Regex;
use std::process::{Command, Stdio};
use colored::*;
use std::collections::HashMap;

const DANGEROUS_PERMS: &[&str] = &[
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.READ_CONTACTS",
    "android.permission.READ_CALL_LOG",
    "android.permission.RECORD_AUDIO",
    "android.permission.CAMERA",
    "android.permission.READ_SMS",
    "android.permission.GET_ACCOUNTS",
];

fn adb(cmd: &str) -> String {
    let output = Command::new("adb")
        .arg("shell")
        .args(cmd.split_whitespace())
        .stdout(Stdio::piped())
        .output()
        .unwrap_or_default();
    String::from_utf8_lossy(&output.stdout).to_string()
}

fn get_packages() -> Vec<String> {
    let output = adb("pm list packages");
    output
        .lines()
        .filter_map(|l| l.strip_prefix("package:").map(String::from))
        .collect()
}

fn get_perms(pkg: &str) -> Vec<String> {
    let output = adb(&format!("dumpsys package {}", pkg));
    let re = Regex::new(r"granted=true.*?(\S*permission\S+)").unwrap();
    re.captures_iter(&output)
        .filter_map(|c| c.get(1).map(|m| m.as_str().to_string()))
        .filter(|p| DANGEROUS_PERMS.contains(&p.as_str()))
        .collect()
}

fn main() {
    println!("
{}", "🔍 Android Permission Auditor (Rust)".bold().cyan());
    println!("{}", "=".repeat(50).cyan());

    let packages = get_packages();
    println!("
Scanning {} packages...
", packages.len());

    let mut risky: HashMap<String, Vec<String>> = HashMap::new();

    for (i, pkg) in packages.iter().enumerate() {
        let perms = get_perms(pkg);
        if !perms.is_empty() {
            risky.insert(pkg.clone(), perms);
        }
        if (i + 1) % 20 == 0 {
            println!("  ... {} scanned", i + 1);
        }
    }

    println!("
{}", "Results:".bold().underline());
    for (pkg, perms) in &risky {
        println!("
  {}", pkg.yellow());
        for perm in perms {
            let short = perm.split('.').last().unwrap_or(&perm);
            println!("    {}", format!("→ {}", short).red());
        }
    }

    println!(
        "
{} Found {}/{} packages with dangerous permissions",
        "⚠️ ".yellow(),
        risky.len().to_string().red(),
        packages.len()
    );
    println!("   Run: adb shell pm revoke <package> <permission>");
}
