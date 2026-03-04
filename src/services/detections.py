from datetime import datetime, timezone, timedelta
import json
from src.models import Event, Alert
from src.extensions import db

def detect_404_burst() -> int:
    now = datetime.now(timezone.utc)
    lookback = now - timedelta(minutes=15)

    rows = (
        db.session.query(Event)
        .filter(Event.ts >= lookback, Event.status == 404)
        .all()
    )

    by_ip = {}
    for ev in rows:
        by_ip.setdefault(ev.src_ip, []).append(ev)

    window = timedelta(minutes=5)
    threshold = 20
    created = 0

    for ip, evs in by_ip.items():
        evs.sort(key=lambda x: x.ts)

        left = 0
        for right in range(len(evs)):
            while evs[right].ts - evs[left].ts > window:
                left += 1

            count = right - left + 1
            if count >= threshold:
                ts_start = evs[left].ts
                ts_end = evs[right].ts

                paths = {}
                for k in range(left, right + 1):
                    p = evs[k].path
                    paths[p] = paths.get(p, 0) + 1
                top_paths = sorted(paths.items(), key=lambda x: x[1], reverse=True)[:5]

                db.session.add(Alert(
                    ts_start=ts_start,
                    ts_end=ts_end,
                    rule_name="nginx_404_burst",
                    severity="medium",
                    src_ip=ip,
                    summary=f"{count}x 404 em 5 min do IP {ip}",
                    evidence=json.dumps({
                        "count_404": count,
                        "top_paths": [{"path": p, "count": c} for p, c in top_paths],
                    }, ensure_ascii=False)
                ))
                created += 1
                break

    return created

def run_all() -> int:
    return detect_404_burst()