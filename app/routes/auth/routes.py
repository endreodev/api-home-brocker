from datetime import datetime, timedelta
from asyncio import sleep
from flask import jsonify, request, abort
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_jwt 
from werkzeug.security import check_password_hash , generate_password_hash
from app.models.models import User, Acessos
from datetime import timedelta
from flask_cors import cross_origin

def init_routes(app):

    @app.route("/")
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    @jwt_required()
    def hello_world():
        return "Hello, Cross-Origin World!"

    @app.route('/login', methods=['POST', 'OPTIONS'])
    @cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
    def login():
        email = request.json.get('email', None)
        password = request.json.get('password', None)

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):

            # Adiciona uma verificação para saber se o usuário está ativo
            if not user.ativo:
                return jsonify({"message": "Conta inativa. Por favor, entre em contato com o suporte."}), 403
            
            # Busca os acessos do usuário
            acessos = Acessos.query.filter_by(usuario_id=user.id, ativo=True).all()
            if not acessos and not user.interno:
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
            
            # Adiciona informações adicionais no token
            additional_claims = {
                'user_id': user.id,
                'nome': user.nome,
                'email': user.email,
                'telefone': user.telefone,
                'interno': user.interno,
                'ativo': user.ativo,
                'empresa_id': user.empresa_id,
                'acessos': acessos_list
            }

            # Cria o token com expiração de 8 horas
            expires = timedelta(hours=8)                
            access_token = create_access_token(identity=email, additional_claims=additional_claims, expires_delta=expires)
            expires_time = datetime.utcnow() + expires

            # Generate the token with an 8-hour expiration
            # expires = timedelta(hours=8)
            # access_token = create_access_token(identity=email, expires_delta=expires, additional_claims={"user_id": user.id})
            # expires_time = datetime.utcnow() + expires

            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'expires': expires_time.isoformat() + 'Z',  # ISO format with Zulu time zone
                'user_id': user.id,
                'nome': user.nome,
                'email': user.email,
                'telefone': user.telefone,
                'interno': user.interno,
                'empresa_id': user.empresa_id,
                'ativo': user.ativo
            }), 200
        else:
            return jsonify({"message": "Email ou Senha inválidos"}), 401


    @app.route('/recovery-password', methods=['POST'])
    @cross_origin()
    def recovery_psw():
        email = request.json.get('email', None)
        user = User.query.filter_by(email=email).first()
        if user :
            return jsonify({"message": "User created successfully"}), 201

        else:
            return jsonify({"message": "Não foi possivel recuperar acesso"}), 401
    

    @app.route('/protected', methods=['GET'])
    @jwt_required()
    def protected():
        # Obtém a identidade do token JWT (neste caso, o e-mail do usuário)
        current_user_email = get_jwt_identity()
        
        # Obtém outros dados adicionais (claims) do token JWT
        additional_claims = get_jwt()
        
        # Exemplo de acesso a dados adicionais diretamente
        user_id = additional_claims.get('user_id', None)
        user_name = additional_claims.get('nome', None)
        
        # Retorna os dados na resposta JSON
        return jsonify({
            "msg": "Access granted to protected route",
            "user_email": current_user_email,
            "user_id": user_id,
            "user_name": user_name,
            "clais": additional_claims
        }), 200


def send_mail_recovery_password():
    print("enviou email para recuperar senha")
    



