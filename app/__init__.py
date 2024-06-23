from flask import Flask
from flask_cors import CORS
from app.config import configure_app
from app.database import db, init_db
from app.routes.auth.routes import init_routes
from app.routes.qout.routes_travas import init_routes_trava
from app.routes.user.routes_empresa import init_routes_empresa
from app.routes.user.routes_firebase import init_routes_firebase
from app.routes.user.routes_grupo import init_routes_grupo
from app.routes.user.routes_parceiro  import init_routes_parceiro
# from app.routes.user.routes_plano import init_routes_plano
from app.routes.user.routes_usuario import init_routes_usuario
from app.routes.user.routes_acessos  import init_routes_acessos
from app.routes.qout.routes_broker import init_routes_broker
from app.auth import jwt 

def create_app():
    
    app = Flask(__name__) 
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True) 
    configure_app(app)
    db.init_app(app)
    jwt.init_app(app)
    
    with app.app_context():
        init_db(app)

    init_routes(app)
    init_routes_empresa(app)
    # init_routes_plano(app)
    init_routes_grupo(app)
    init_routes_parceiro(app)
    init_routes_usuario(app)
    init_routes_acessos(app)
    init_routes_broker(app)
    init_routes_trava(app)
    init_routes_firebase(app)
    
    return app

app = create_app()