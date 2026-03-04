from flask import Blueprint, jsonify, request
from sqlalchemy import desc
from src.extensions import db
from src.models import Alert
from src.services.normalize import parse_ts

bp = Blueprint("alerts", __name__)

@bp.get("/alerts")
def list_alerts():
    q = db.session.query(Alert)

    severity = request.args.get("severity")
    rule_name = request.args.get("rule_name")
    src_ip = request.args.get("src_ip")
    from_ts = request.args.get("from")
    to_ts = request.args.get("to")

    if severity:
        q = q.filter(Alert.severity == severity)

    if rule_name:
        q = q.filter(Alert.rule_name == rule_name)

    if src_ip:
        q = q.filter(Alert.src_ip == src_ip)

    if from_ts:
        try:
            q = q.filter(Alert.ts_start >= parse_ts(from_ts))
        except Exception:
            return jsonify({"error": "from must be ISO 8601, ex: 2026-03-04T13:00:00Z"}), 400

    if to_ts:
        try:
            q = q.filter(Alert.ts_end <= parse_ts(to_ts))
        except Exception:
            return jsonify({"error": "to must be ISO 8601, ex: 2026-03-04T14:00:00Z"}), 400

    # paginação (opcional, mas útil)
    try:
        limit = min(int(request.args.get("limit", "200")), 200)
        offset = max(int(request.args.get("offset", "0")), 0)
    except ValueError:
        return jsonify({"error": "limit/offset must be int"}), 400

    rows = q.order_by(desc(Alert.ts_end)).offset(offset).limit(limit).all()

    out = []
    for a in rows:
        out.append({
            "id": a.id,
            "ts_start": a.ts_start.isoformat().replace("+00:00", "Z"),
            "ts_end": a.ts_end.isoformat().replace("+00:00", "Z"),
            "rule_name": a.rule_name,
            "severity": a.severity,
            "src_ip": a.src_ip,
            "summary": a.summary,
            # evidence está salvo como string JSON (Text); devolvemos como string mesmo
            "evidence": a.evidence or "{}",
        })

    return jsonify(out), 200