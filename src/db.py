from src.extensions import db

# opcional: função para inicializar (não é obrigatória)
def init_db(app):
    db.init_app(app)