from src.extensions import db

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    ts = db.Column(db.DateTime(timezone=True), index=True, nullable=False)

    source = db.Column(db.String(50), index=True, nullable=False)       # nginx
    event_type = db.Column(db.String(50), index=True, nullable=False)   # http_request

    src_ip = db.Column(db.String(64), index=True, nullable=False)
    method = db.Column(db.String(16), nullable=False)
    path = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, index=True, nullable=False)

    user_agent = db.Column(db.Text, nullable=True)
    referrer = db.Column(db.Text, nullable=True)


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    ts_start = db.Column(db.DateTime(timezone=True), index=True, nullable=False)
    ts_end = db.Column(db.DateTime(timezone=True), index=True, nullable=False)

    rule_name = db.Column(db.String(100), index=True, nullable=False)
    severity = db.Column(db.String(10), index=True, nullable=False)

    src_ip = db.Column(db.String(64), index=True, nullable=False)
    summary = db.Column(db.Text, nullable=False)

    evidence = db.Column(db.Text, nullable=True)  # JSON como string (simples no começo)