import re
import json
import numpy as np
from datetime import datetime
from owasp_mapping import OWASP_MAPPING

# Load logs
with open("sample_logs.txt", "r") as f:
    logs = f.readlines()

alerts = []

# === Detection Rules ===
failed_auth_count = {}
for line in logs:
    ts = datetime.now().isoformat()
    if "failed password" in line.lower():
        user = re.search(r"user=(\w+)", line)
        ip = re.search(r"from ([\d\.]+)", line)
        entity = user.group(1) if user else "unknown"
        src_ip = ip.group(1) if ip else "unknown"

        failed_auth_count[src_ip] = failed_auth_count.get(src_ip, 0) + 1
        alerts.append({
            "ts": ts,
            "detection": "Failed authentication",
            "severity": "low",
            "entity": entity,
            "evidence": {"src_ip": src_ip, "user": entity},
            "owasp": OWASP_MAPPING["Failed authentication"],
            "recommendations": [
                "Monitor for password spraying",
                "Enforce MFA",
                "Alert if threshold exceeded"
            ]
        })

    if "union select" in line.lower():
        alerts.append({
            "ts": ts,
            "detection": "Injection pattern",
            "severity": "high",
            "entity": "database",
            "evidence": {"payload": line.strip()},
            "owasp": OWASP_MAPPING["Injection pattern"],
            "recommendations": [
                "Use parameterized queries",
                "Apply WAF rules for SQL injection"
            ]
        })

    if "GET /admin unauthenticated" in line:
        alerts.append({
            "ts": ts,
            "detection": "Unauthenticated access to admin path",
            "severity": "medium",
            "entity": "web-server",
            "evidence": {"request": line.strip()},
            "owasp": OWASP_MAPPING["Unauthenticated access to admin path"],
            "recommendations": [
                "Restrict admin panel to VPN or specific IPs",
                "Enable 2FA on admin login"
            ]
        })

    if "../" in line:
        alerts.append({
            "ts": ts,
            "detection": "Path traversal attempt",
            "severity": "critical",
            "entity": "filesystem",
            "evidence": {"request": line.strip()},
            "owasp": OWASP_MAPPING["Path traversal attempt"],
            "recommendations": [
                "Sanitize user input",
                "Harden file system permissions"
            ]
        })

# === Behavioral Anomaly Detection (Z-Score) ===
login_counts = np.array(list(failed_auth_count.values()))
if len(login_counts) > 0:
    mean = np.mean(login_counts)
    std = np.std(login_counts)
    for ip, count in failed_auth_count.items():
        if std > 0 and (count - mean) / std >= 3.0:
            alerts.append({
                "ts": datetime.now().isoformat(),
                "detection": "Behavioral anomaly",
                "severity": "high",
                "entity": ip,
                "evidence": {"login_count": count},
                "owasp": OWASP_MAPPING["Behavioral anomaly"],
                "recommendations": [
                    "Investigate possible brute force attack",
                    "Block suspicious IP at firewall"
                ]
            })

# Save alerts
with open("alerts.jsonl", "w") as f:
    for alert in alerts:
        f.write(json.dumps(alert) + "\n")

print(f"=== Alerts generated: {len(alerts)} (written to alerts.jsonl) ===")
for det in set([a["detection"] for a in alerts]):
    print("-", det)
