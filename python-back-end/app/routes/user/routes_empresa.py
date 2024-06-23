from flask import jsonify, request, abort
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_jwt 
from numpy import empty
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.security import generate_password_hash
from app.database import db
from app.models.models import Acessos, Empresa, User
from app.models.validacao import valideUserInterno
# import firebase_admin 
# from firebase_admin import credentials, messaging

# cred = credentials.Certificate("homebrokerdtvm-7824e290ff8d.json")
# firebase_admin.initialize_app(cred)


def init_routes_empresa(app):
    # CADASTRA EMPRESA 
    @app.route('/empresas', methods=['POST'])
    @jwt_required()
    def create_empresa():
        additional_claims = get_jwt()
        user_id = additional_claims.get('user_id', None)
        if not valideUserInterno(user_id):
            return jsonify({'message': 'Usuario sem acesso a rotina'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'message': 'Nenhum dado fornecido.'}), 400
        
        # Verifica se todos os campos obrigatórios estão presentes
        required_fields = ['cgc', 'empresa', 'nome']   
        if not all(data.get(field) for field in required_fields):  # Verifica presença e não vazio
            return jsonify({'error': 'Faltando campos  obrigatórios ou campos vazios'}), 400

        try:
            new_empresa = Empresa(
                cgc=data['cgc'],
                empresa=data['empresa'],
                nome=data['nome'],
                valsaldo=data.get('valsaldo', False) ,
                ativo=data.get('ativo', True)  # Assume true se não especificado
            )
            db.session.add(new_empresa)
            db.session.commit()
            return jsonify({'message': 'Empresa cadastrada com sucesso!'}), 201

        except IntegrityError as e:
            db.session.rollback()  # Reverte a transação se ocorrer um erro de integridade
            return jsonify({'message': 'Erro de integridade, possivelmente dados duplicados'}), 400

        except SQLAlchemyError as e:
            db.session.rollback()  # Reverte a transação para qualquer outro erro SQLAlchemy
            return jsonify({'message': 'Erro ao salvar no banco de dados', 'details': str(e)}), 500

        except Exception as e:
            db.session.rollback()  # Reverte para quaisquer outros erros não capturados
            return jsonify({'message': 'Erro interno do servidor', 'details': str(e)}), 500


    # consulta todas as empresas 
    @app.route('/empresas', methods=['GET'])
    @jwt_required()
    def get_empresas():
        additional_claims = get_jwt()
        user_id = additional_claims.get('user_id', None)
        if not valideUserInterno(user_id):
            return jsonify({'message': 'Usuario sem acesso a rotina'}), 400
    
        empresas = Empresa.query.all()
        # empresas =Empresa.query.filter_by(ativo=True).all()
        empresas_list = [empresa.to_dict() for empresa in empresas]  # Use o método to_dict()
        return jsonify(empresas_list)

    # CONSULTA ID EMPRESA
    @app.route('/empresas/<int:id>', methods=['GET'])
    @jwt_required()
    def get_empresa(id):
        additional_claims = get_jwt()
        user_id = additional_claims.get('user_id', None)
        if not valideUserInterno(user_id):
            return jsonify({'message': 'Usuario sem acesso a rotina'}), 400
        
        empresa = Empresa.query.get(id)
        if not empresa:
            return jsonify({'message': 'Empresa não encontrada'}), 404  # Use 404 para "não encontrado"

        return jsonify(empresa.to_dict()), 200  # Retorna o dicionário serializado com status 200 OK

    # EDITAR EMPRESA 
    @app.route('/empresas/<int:id>', methods=['PUT'])
    @jwt_required()
    def update_empresa(id):
        additional_claims = get_jwt()
        user_id = additional_claims.get('user_id', None)
        if not valideUserInterno(user_id):
            return jsonify({'message': 'Usuario sem acesso a rotina'}), 400
        
        empresa = Empresa.query.get(id)
        if not empresa:
            return jsonify({'message': 'Empresa não encontrada.'}), 400 
    
        try:
            data = request.get_json()
            empresa.cod_interno = data.get('cod_interno', empresa.cod_interno)
            empresa.cgc         = data.get('cgc'        , empresa.cgc        )
            empresa.empresa     = data.get('empresa'    , empresa.empresa    )
            empresa.nome        = data.get('nome'       , empresa.nome       )
            empresa.valsaldo    = data.get('valsaldo'   , empresa.valsaldo   )
            empresa.telegran    = data.get('telegran'   , empresa.telegran   )
            empresa.ativo       = data.get('ativo'      , empresa.ativo      )
            db.session.commit()
            return jsonify({'message': 'Empresa atualizada com sucesso!'})

        except IntegrityError as e:
            db.session.rollback()  # Reverte a transação se ocorrer um erro de integridade
            return jsonify({'message': 'Erro de integridade, possivelmente dados duplicados'}), 400

        except SQLAlchemyError as e:
            db.session.rollback()  # Reverte a transação para qualquer outro erro SQLAlchemy
            return jsonify({'message': 'Erro ao salvar no banco de dados', 'details': str(e)}), 500

        except Exception as e:
            db.session.rollback()  # Reverte para quaisquer outros erros não capturados
            return jsonify({'message': 'Erro interno do servidor', 'details': str(e)}), 500


    # apaga empresa
    # @app.route('/empresas/<int:id>', methods=['DELETE'])
    # @jwt_required()
    # def delete_empresa(id):
    #     empresa = Empresa.query.get(id)
    #     if not empresa:
    #         return jsonify({'message': 'Empresa não encontrada.'}), 400
        
    #     try:
    #         db.session.delete(empresa)
    #         db.session.commit()
    #         return jsonify({'message': 'Empresa deletada com sucesso!'})

    #     except IntegrityError as e:
    #         db.session.rollback()  # Reverte a transação se ocorrer um erro de integridade
    #         return jsonify({'message': 'Erro de integridade, possivelmente dados duplicados'}), 400

    #     except SQLAlchemyError as e:
    #         db.session.rollback()  # Reverte a transação para qualquer outro erro SQLAlchemy
    #         return jsonify({'message': 'Erro ao salvar no banco de dados', 'details': str(e)}), 500

    #     except Exception as e:
    #         db.session.rollback()  # Reverte para quaisquer outros erros não capturados
    #         return jsonify({'message': 'Erro interno do servidor', 'details': str(e)}), 500
        

    # @app.route('/notificate/<string:token>', methods=['get'])   
    # def send_push_notification(token):
    #     try:
    #         message = messaging.Message(
    #             notification=messaging.Notification(
    #                 title='title aksdklajslkdjlkasjldkjasljdklajslkdjals',
    #                 body='body  ajsdkasjldaskkadns d assd asd as das d as dsa d as q wr qw r weg b s d fa  as das d a ',
    #             ),
    #             token=token,
    #     )
    #         response = messaging.send(message)
    #         print('Successfully sent message:', response)
    #         return jsonify({
    #             'success': True,
    #             'message_id': response,
    #             'details': 'Message sent successfully.'
    #         })
    #     except messaging.ApiCallError as e:
    #         print('Failed to send message:', e)
    #         return jsonify({
    #             'success': False,
    #             'error': str(e),
    #             'details': 'API call error occurred while sending message.'
    #         })
    #     except Exception as e:
    #         print('Unexpected error:', e)
    #         return jsonify({
    #             'success': False,
    #             'error': str(e),
    #             'details': 'An unexpected error occurred while sending message.'
    #         })
