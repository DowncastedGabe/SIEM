from flask import Flask
from src.config import Config
from src.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # inicializa extensões
    db.init_app(app)

    # importa models para registrar as tabelas no SQLAlchemy
    from src import models  # noqa: F401

    # cria as tabelas (para MVP; depois você pode trocar por migrations)
    with app.app_context():
        db.create_all()

    # importa blueprints UMA vez
    from src.routes.health import bp as health_bp
    from src.routes.ingest import bp as ingest_bp
    from src.routes.events import bp as events_bp
    from src.routes.alerts import bp as alerts_bp

    # registra blueprints UMA vez (com prefixos opcionais)
    app.register_blueprint(health_bp)                 # /health
    app.register_blueprint(ingest_bp, url_prefix="")  # /ingest
    app.register_blueprint(events_bp, url_prefix="")  # /events
    app.register_blueprint(alerts_bp, url_prefix="")  # /alerts

    return app