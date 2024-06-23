from flask import jsonify, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models.models import Firebase

def init_routes_firebase(app):
    
    @app.route('/firebase', methods=['POST'])
    @jwt_required()
    def create_or_update_acesso_firebase():
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Nenhum dado fornecido.'}), 400

        required_fields = ['empresa_id', 'usuario_id', 'token']
        if not all(data.get(field) is not None for field in required_fields):
            return jsonify({'message': 'Faltando campos obrigatórios ou campos nulos'}), 400

        # Busca um acesso existente
        acesso = Firebase.query.filter_by(
            empresa_id=data['empresa_id'], 
            usuario_id=data['usuario_id']
        ).first()

        if acesso:
            # Atualiza o token e o interno se já existe um registro
            acesso.token = data['token']
            acesso.interno = data.get('interno', acesso.interno)
        else:
            # Cria um novo registro se não existir
            acesso = Firebase(
                empresa_id=data['empresa_id'],
                usuario_id=data['usuario_id'],
                token=data['token'],
                interno=data.get('interno', False)
            )
            db.session.add(acesso)

        try:
            db.session.commit()
            return jsonify({'message': 'Acesso criado ou atualizado com sucesso!'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Erro ao salvar no banco de dados', 'details': str(e)}), 500
