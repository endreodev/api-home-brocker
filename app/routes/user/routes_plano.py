from flask import jsonify, request, abort
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_jwt 
from numpy import empty
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.security import generate_password_hash
from app.database import db
from app.models.models import Plano, PlanoValor
from enum import Enum

def init_routes_plano(app):
    
    # consulta todas as empresas 
    @app.route('/plano', methods=['GET'])
    @jwt_required()
    def get_plano():
        planos = serialize_enum(Plano)
        return jsonify(planos)

    @app.route('/plano-valor', methods=['GET'])
    @jwt_required()
    def get_plano_valor():
        planos = serialize_enum(PlanoValor)
        return jsonify(planos)
    
    #consulta plano plano
    @app.route('/plano-valor/<string:id>', methods=['GET'])
    @jwt_required()
    def get_planos_id(id):
        planos_valor = serialize_enum(PlanoValor)
        planos = planos_valor.get(id)
        if not planos:
            return jsonify({'message': 'PLANO não encontrada.'}), 400 

        return jsonify({'message': planos })
        

        
def serialize_enum(enum):
    """ Retorna um dicionário de todos os valores do enum """
    return {e.name: e.value for e in enum}