from flask import jsonify, request, abort
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, create_access_token
from app.models.models import User
from app.database import db
from flask_cors import cross_origin
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

def init_routes_usuario(app):
    
    @app.route('/users', methods=['POST'])
    @jwt_required()
    def registrar():
        data = request.get_json()
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'message': 'Usuário já cadastrado!'}), 409

        new_user = User(
            nome=data['nome'],
            email=data['email'],
            telefone=data['telefone'],
            password=generate_password_hash(data['password']),
            ativo=data.get('ativo', True),
            interno=data.get('interno', False),
            empresa_id=data['empresa_id'],
            cod_interno=data.get('cod_interno', '')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Usuário cadastrado com sucesso!'}), 201

    @app.route('/users/<int:user_id>', methods=['GET'])
    @jwt_required()
    def get_user(user_id):
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'nome': user.nome,
            'email': user.email,
            'telefone': user.telefone,
            'ativo': user.ativo,
            'interno': user.interno,
            'cod_interno': user.cod_interno
        })

    @app.route('/users/<int:user_id>', methods=['PUT'])
    @jwt_required()
    def update_user(user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        if 'password' in data and data['password']:
            user.password = generate_password_hash(data['password'])
        user.nome = data.get('nome', user.nome)
        user.email = data.get('email', user.email)
        user.telefone = data.get('telefone', user.telefone)
        user.ativo = data.get('ativo', user.ativo)
        user.interno = data.get('interno', user.interno)
        user.cod_interno = data.get('cod_interno', user.cod_interno)
        db.session.commit()
        return jsonify({'message': 'Usuário atualizado com sucesso!'})

    @app.route('/users/<int:user_id>', methods=['DELETE'])
    @jwt_required()
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Usuário deletado com sucesso!'})

    @app.route('/users', methods=['GET'])
    @jwt_required()
    def get_users():
        users = User.query.all()
        # users_list = [{'id': user.id, 'nome': user.nome, 'email': user.email} for user in users]
        users_list = [
            {
                'id': user.id,
                'empresa_id': user.empresa_id,
                'cod_interno': user.cod_interno,
                # 'password': user.password,
                'nome': user.nome,
                'email': user.email,
                'telefone': user.telefone,
                'ativo': user.ativo,
                'interno': user.interno     
            } for user in users
        ]

        return jsonify(users_list)
