from datetime import datetime
import ipaddress

def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def validate_event(e: dict) -> list[str]:
    errors = []
    required = ["ts", "src_ip", "method", "path", "status"]
    for f in required:
        if f not in e:
            errors.append(f"missing field: {f}")
    if errors:
        return errors

    try:
        parse_ts(str(e["ts"]))
    except Exception:
        errors.append("invalid ts (ISO 8601 ex: 2026-03-04T13:45:10Z)")

    try:
        ipaddress.ip_address(str(e["src_ip"]))
    except Exception:
        errors.append("invalid src_ip")

    try:
        int(e["status"])
    except Exception:
        errors.append("status must be int")

    return errors

def normalize_event(e: dict) -> dict:
    ts_dt = parse_ts(str(e["ts"]))
    return {
        "ts_dt": ts_dt,
        "source": "nginx",
        "event_type": "http_request",
        "src_ip": str(e["src_ip"]),
        "method": str(e["method"]).upper(),
        "path": str(e["path"]),
        "status": int(e["status"]),
        "user_agent": str(e.get("user_agent", "")),
        "referrer": str(e.get("referrer", "")),
    }