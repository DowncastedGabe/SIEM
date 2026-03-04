from flask import Blueprint, jsonify, request
from src.services.normalize import validate_event, normalize_event
from src.models import Event
from src.extensions import db
from src.services.detections import run_all

bp = Blueprint("ingest", __name__)

@bp.post("/ingest")
def ingest():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Send JSON in request body"}), 400

    items = data if isinstance(data, list) else [data]
    ingested = 0
    errors = []

    for i, e in enumerate(items):
        if not isinstance(e, dict):
            errors.append({"index": i, "errors": ["event must be a JSON object"]})
            continue

        ev_errors = validate_event(e)
        if ev_errors:
            errors.append({"index": i, "errors": ev_errors})
            continue

        n = normalize_event(e)
        db.session.add(Event(
            ts=n["ts_dt"],
            source=n["source"],
            event_type=n["event_type"],
            src_ip=n["src_ip"],
            method=n["method"],
            path=n["path"],
            status=n["status"],
            user_agent=n["user_agent"],
            referrer=n["referrer"],
        ))
        ingested += 1

    db.session.commit()

    created_alerts = run_all()
    db.session.commit()

    return jsonify({"ingested": ingested, "errors": errors, "created_alerts": created_alerts})