import json
import random
import argparse
import re
from datetime import datetime, timedelta
from uuid import uuid4
from collections import defaultdict

# -----------------------------
# Configuration
# -----------------------------
USERS = ["alice", "bob", "charlie", "testuser", "admin"]
IPS = ["192.168.1.10", "192.168.1.11", "192.168.1.12", "192.168.1.50"]
ADMIN_IP = "192.168.1.99"

OUTPUT_FILE = "events.jsonl"
AUTH_LOG = "/var/log/auth.log"

# -----------------------------
# Helpers
# -----------------------------
def now_ts():
    return datetime.utcnow().isoformat() + "Z"


def write_event(f, event):
    f.write(json.dumps(event) + "\n")


def base_event(user, src_ip, action, resource, meta=None):
    return {
        "event_id": str(uuid4()),
        "ts": now_ts(),
        "user": user,
        "src_ip": src_ip,
        "action": action,
        "resource": resource,
        "meta": meta or {}
    }

# -----------------------------
# SIMULATED EVENTS
# -----------------------------
def generate_normal_events(f, count=30):
    for _ in range(count):
        user = random.choice(USERS[:-1])
        ip = random.choice(IPS)

        event_type = random.choices(
            ["LOGIN_SUCCESS", "LOGIN_FAIL", "FILE_ACCESS", "ADMIN_ACTION"],
            weights=[60, 20, 15, 5]
        )[0]

        if event_type == "LOGIN_SUCCESS":
            event = base_event(user, ip, "LOGIN_SUCCESS", "auth")

        elif event_type == "LOGIN_FAIL":
            event = base_event(user, ip, "LOGIN_FAIL", "auth", {"attempt": 1})

        elif event_type == "FILE_ACCESS":
            event = base_event(
                user,
                ip,
                "FILE_ACCESS",
                "filesystem",
                {"file": f"/home/{user}/report.txt"}
            )

        else:
            event = base_event(
                "admin",
                ADMIN_IP,
                "ADMIN_ACTION",
                "system",
                {"action": "view_logs"}
            )

        write_event(f, event)


def brute_force_attack(f, target_user="testuser", attacker_ip="192.168.1.50"):
    for i in range(15):
        event = base_event(
            target_user,
            attacker_ip,
            "LOGIN_FAIL",
            "auth",
            {"attempt": i + 1}
        )
        write_event(f, event)


def privilege_abuse_attack(f):
    for _ in range(5):
        event = base_event(
            "admin",
            ADMIN_IP,
            "ADMIN_ACTION",
            "system",
            {"action": "role_change", "target": "bob"}
        )
        write_event(f, event)


def log_tampering_attempt(f):
    event = base_event(
        "admin",
        ADMIN_IP,
        "LOG_TAMPERING",
        "audit_log",
        {"method": "delete_event"}
    )
    write_event(f, event)

# -----------------------------
# REAL SSH LOG INGESTION
# -----------------------------
def ingest_ssh_logs(f):
    print("[+] Ingesting real SSH logs from auth.log")

    fail_pattern = re.compile(r"Failed password for (\w+) from ([\d.]+)")
    success_pattern = re.compile(r"Accepted password for (\w+) from ([\d.]+)")

    attempt_counter = defaultdict(int)

    with open(AUTH_LOG, "r") as log:
        for line in log:
            fail = fail_pattern.search(line)
            success = success_pattern.search(line)

            if fail:
                user, ip = fail.groups()
                attempt_counter[(user, ip)] += 1

                event = base_event(
                    user,
                    ip,
                    "LOGIN_FAIL",
                    "auth",
                    {"attempt": attempt_counter[(user, ip)]}
                )
                write_event(f, event)

            elif success:
                user, ip = success.groups()
                attempt_counter[(user, ip)] = 0

                event = base_event(
                    user,
                    ip,
                    "LOGIN_SUCCESS",
                    "auth"
                )
                write_event(f, event)

# -----------------------------
# MAIN
# -----------------------------
def main(mode):
    with open(OUTPUT_FILE, "w") as f:
        print(f"[+] Writing events to {OUTPUT_FILE}")

        if mode == "normal":
            generate_normal_events(f)

        elif mode == "attack":
            generate_normal_events(f)
            brute_force_attack(f)
            privilege_abuse_attack(f)
            log_tampering_attempt(f)

        elif mode == "ssh":
            ingest_ssh_logs(f)

        print("[✓] Done")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Security Event Generator")
    parser.add_argument(
        "--mode",
        choices=["normal", "attack", "ssh"],
        default="normal",
        help="normal | attack | ssh (real auth.log ingestion)"
    )

    args = parser.parse_args()
    main(args.mode)
