from flask import jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from app.models.models import Grupo
from app.database import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

def init_routes_grupo(app):

    @app.route('/grupos', methods=['POST'])
    @jwt_required()
    def add_grupo():

        additional_claims = get_jwt()
        empresa_id = additional_claims.get('empresa_id', None)

        data = request.get_json()
        new_grupo = Grupo(
            empresa_id=empresa_id,
            nome=data['nome'],
            ativo=data.get('ativo', True)
        )
        try:
            db.session.add(new_grupo)
            db.session.commit()
            return jsonify({'message': 'Grupo adicionado com sucesso!'}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Erro de integridade, possivelmente dados duplicados'}), 409
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Erro ao salvar no banco de dados', 'details': str(e)}), 500

    @app.route('/grupos', methods=['GET'])
    @jwt_required()
    def get_grupos():
        additional_claims = get_jwt()
        empresa_id = additional_claims.get('empresa_id', None)
        grupos = Grupo.query.filter_by(empresa_id=empresa_id, ativo=True).all()

        grupo_list = [{'id': g.id, 'empresa_id': g.empresa_id, 'nome': g.nome, 'ativo': g.ativo} for g in grupos]
        return jsonify(grupo_list), 200

    @app.route('/grupos/<int:id>', methods=['GET'])
    @jwt_required()
    def get_grupo(id):
        grupo = Grupo.query.get(id)
        if not grupo:
            return jsonify({'error': 'Grupo não encontrado'}), 404
 
        return jsonify({ 
            'id': grupo.id, 
            'empresa_id': grupo.empresa_id, 
            'nome': grupo.nome, 
            'ativo': grupo.ativo
        })

    @app.route('/grupos/<int:id>', methods=['PUT'])
    @jwt_required()
    def update_grupo(id):
        grupo = Grupo.query.get(id)
        if not grupo:
            return jsonify({'error': 'Grupo não encontrado'}), 404
        
        data = request.get_json()
        grupo.nome = data['nome']
        grupo.ativo = data.get('ativo', grupo.ativo)
        db.session.commit()
        return jsonify({'message': 'Grupo atualizado com sucesso!'}), 200

    # @app.route('/grupos/<int:id>', methods=['DELETE'])
    # @jwt_required()
    # def delete_grupo(id):
    #     grupo = Grupo.query.get(id)
    #     if not grupo:
    #         return jsonify({'error': 'Grupo não encontrado'}), 404
    #     db.session.delete(grupo)
    #     db.session.commit()
    #     return jsonify({'message': 'Grupo excluído com sucesso!'}), 200
