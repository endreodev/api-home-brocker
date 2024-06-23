from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def init_db(app):

    migrate = Migrate(app, db)
    # db.create_all()  # Cria as tabelas se elas não existirem
