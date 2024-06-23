def configure_app(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Jaca@157@localhost/homebroker'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'homebrokerENDREO@2024'
    app.config['CORS_HEADERS'] = 'Content-Type'
