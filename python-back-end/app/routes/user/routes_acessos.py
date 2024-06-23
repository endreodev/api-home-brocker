from flask import jsonify, request, abort
from werkzeug.security import generate_password_hash
from flask_jwt_extended import get_jwt, jwt_required, create_access_token
from app.models.models import Acessos, User, Empresa, Parceiro
from app.database import db
from flask_cors import cross_origin
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

def init_routes_acessos(app):
    
    @app.route('/acessos', methods=['POST'])
    @jwt_required()
    def create_or_update_acesso():
        
        additional_claims = get_jwt()
        empresa_id = additional_claims.get('empresa_id', None)

        data = request.get_json()
        usuario_id = data['usuario_id']
        parceiro_id = data['parceiro_id']
        ativo = data.get('ativo', True)

        # Busca um acesso existente
        acesso = Acessos.query.filter_by(usuario_id=usuario_id, empresa_id=empresa_id, parceiro_id=parceiro_id).first()

        if acesso:
            # Atualiza o acesso existente
            acesso.ativo = ativo
            action_message = 'Acesso atualizado com sucesso!'
        else:
            # Cria um novo acesso se não encontrar existente
            acesso = Acessos(
                usuario_id=usuario_id,
                empresa_id=empresa_id,
                parceiro_id=parceiro_id,
                ativo=ativo
            )
            db.session.add(acesso)
            action_message = 'Acesso criado com sucesso!'

        try:
            db.session.commit()
            return jsonify({'message': action_message}), 201
        except IntegrityError as e:
            db.session.rollback()  # Reverte a transação se ocorrer um erro de integridade
            return jsonify({'message': 'Erro de integridade, possivelmente dados duplicados', 'details': str(e)}), 400
        except SQLAlchemyError as e:
            db.session.rollback()  # Reverte a transação para qualquer outro erro SQLAlchemy
            return jsonify({'message': 'Erro ao salvar no banco de dados', 'details': str(e)}), 500
        except Exception as e:
            db.session.rollback()  # Reverte para quaisquer outros erros não capturados
            return jsonify({'message': 'Erro interno do servidor', 'details': str(e)}), 500


    # retorna todos os acessos 
    @app.route('/acessos', methods=['GET'])
    @jwt_required()
    def get_acessos():
        acessos = Acessos.query.all()
        acessos_list = [
            {
                'id': acesso.id,
                'usuario_id': acesso.usuario_id,
                'empresa_id': acesso.empresa_id,
                'parceiro_id': acesso.parceiro_id,
                'ativo': acesso.ativo
            } for acesso in acessos
        ]
        return jsonify(acessos_list)

    #  Consulra o acesso pelo id
    @app.route('/acessos/<int:id>', methods=['GET'])
    @jwt_required()
    def get_acesso_id(id):
        acesso = Acessos.query.get(id)
        if not acesso:
            return jsonify({'message': 'acesso não encontrada'}), 400
        return jsonify({
            'id': acesso.id,
            'usuario_id': acesso.usuario_id,
            'empresa_id': acesso.empresa_id,
            'parceiro_id': acesso.parceiro_id,
            'ativo': acesso.ativo
        })

    # autera o acesso pelo id 
    @app.route('/acessos/<int:id>', methods=['PUT'])
    @jwt_required()
    def update_acesso(id):
        acesso = Acessos.query.get(id)
        if not acesso:
            return jsonify({'message': 'acesso não encontrada'}), 400

        data = request.get_json()
        acesso.usuario_id = data.get('usuario_id', acesso.usuario_id)
        acesso.empresa_id = data.get('empresa_id', acesso.empresa_id)
        acesso.parceiro_id = data.get('parceiro_id', acesso.parceiro_id)
        acesso.ativo = data.get('ativo', acesso.ativo)
        db.session.commit()
        return jsonify({'message': 'Acesso atualizado com sucesso!'})

    # deleta o acesso pelo id 
    @app.route('/acessos/<int:id>', methods=['DELETE'])
    @jwt_required()
    def delete_acesso(id):
        acesso = Acessos.query.get(id)
        if not acesso:
            return jsonify({'message': 'acesso não encontrada'}), 400
        db.session.delete(acesso)
        db.session.commit()
        return jsonify({'message': 'Acesso deletado com sucesso!'})
    
    # retorna acessos de um usuario especifico
    @app.route('/usuarios/<int:usuario_id>/acessos', methods=['GET'])
    @jwt_required()
    def get_acessos_usuario(usuario_id):
        # Busca o usuário pelo ID para verificar se ele existe
        usuario = User.query.get(usuario_id)
        if not usuario:
            return jsonify({'message': 'Usuário não encontrado.'}), 404

        # Busca os acessos do usuário
        acessos = Acessos.query.filter_by(usuario_id=usuario_id).all()
        if not acessos:
            return jsonify({'message': 'Nenhum acesso encontrado para este usuário.'}), 404

        # Prepara a lista de acessos para retornar
        acessos_list = []
        for acesso in acessos:
            acessos_list.append({
                'acesso_id': acesso.id,
                'empresa_id': acesso.empresa_id,
                'empresa_nome': acesso.empresa.nome,
                'parceiro_id': acesso.parceiro_id,
                'parceiro_nome': acesso.parceiro.nome,
                'ativo': acesso.ativo
            })

        return jsonify({
            'usuario_id': usuario_id,
            'usuario_nome': usuario.nome,
            'acessos': acessos_list
        }), 200


    @app.route('/acessos-parceiro/<int:usuario_id>', methods=['GET'])
    @jwt_required()
    def get_parceiros_com_acessos(usuario_id):

        # additional_claims = get_jwt()
        # user_id = additional_claims.get('user_id', None)
    
        try:
            parceiros = Parceiro.query.all()
            acessos = Acessos.query.filter_by(usuario_id=usuario_id, ativo=True).all()
            acessos_ids = {acesso.parceiro_id for acesso in acessos}  # Conjunto de IDs para acesso rápido

            result = [
                {
                    "id": parceiro.id,
                    "nome": parceiro.nome,
                    "cgc": parceiro.cgc,
                    "cod_interno": parceiro.cod_interno,
                    "empresa_id": parceiro.empresa_id,
                    "grupo_id": parceiro.grupo_id,
                    "lmt_mes": str(parceiro.lmt_mes),
                    "lmt_trava": str(parceiro.lmt_trava),
                    "plano": str(parceiro.plano),
                    "ativo": parceiro.ativo,
                    "acesso": parceiro.id in acessos_ids
                }
                for parceiro in parceiros
            ]
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"message": "Erro ao buscar parceiros e acessos", "details": str(e)}), 500
        

    @app.route('/atualizar-acessos/<int:usuario_id>', methods=['POST'])
    @jwt_required()
    def atualizar_acessos(usuario_id):
        data = request.get_json()
        try:
            # Primeiro, desative todos os acessos
            Acessos.query.filter_by(usuario_id=usuario_id).update({"ativo": False})
            
            # Ative os acessos fornecidos
            for parceiro_id in data['parceiro_ids']:
                acesso = Acessos.query.filter_by(usuario_id=usuario_id, parceiro_id=parceiro_id).first()
                if acesso:
                    acesso.ativo = True
                else:
                    db.session.add(Acessos(usuario_id=usuario_id, parceiro_id=parceiro_id, ativo=True))
            
            db.session.commit()
            return jsonify({"message": "Acessos atualizados com sucesso"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Erro ao atualizar acessos", "details": str(e)}), 500