from flask import Blueprint, jsonify, request
from sqlalchemy import desc
from src.extensions import db
from src.models import Event
from src.services.normalize import parse_ts

bp = Blueprint("events", __name__)

@bp.get("/events")
def list_events():
    # Query base
    q = db.session.query(Event)

    # Query params
    src_ip = request.args.get("src_ip")
    status = request.args.get("status")
    path_contains = request.args.get("path_contains")
    from_ts = request.args.get("from")
    to_ts = request.args.get("to")

    # Paginação (com defaults e limites)
    try:
        limit = min(int(request.args.get("limit", "50")), 200)
        offset = max(int(request.args.get("offset", "0")), 0)
    except ValueError:
        return jsonify({"error": "limit/offset must be int"}), 400

    # Filtros
    if src_ip:
        q = q.filter(Event.src_ip == src_ip)

    if status:
        try:
            q = q.filter(Event.status == int(status))
        except ValueError:
            return jsonify({"error": "status must be int"}), 400

    if path_contains:
        q = q.filter(Event.path.contains(path_contains))

    if from_ts:
        try:
            q = q.filter(Event.ts >= parse_ts(from_ts))
        except Exception:
            return jsonify({"error": "from must be ISO 8601, ex: 2026-03-04T13:00:00Z"}), 400

    if to_ts:
        try:
            q = q.filter(Event.ts <= parse_ts(to_ts))
        except Exception:
            return jsonify({"error": "to must be ISO 8601, ex: 2026-03-04T14:00:00Z"}), 400

    # Ordena e pagina
    rows = q.order_by(desc(Event.ts)).offset(offset).limit(limit).all()

    # Serializa
    out = []
    for e in rows:
        out.append({
            "id": e.id,
            "ts": e.ts.isoformat().replace("+00:00", "Z"),
            "source": e.source,
            "event_type": e.event_type,
            "src_ip": e.src_ip,
            "method": e.method,
            "path": e.path,
            "status": e.status,
            "user_agent": e.user_agent or "",
            "referrer": e.referrer or "",
        })

    return jsonify(out), 200