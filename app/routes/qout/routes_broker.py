from flask import Response, json, jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity,jwt_required,get_jwt
from app.models.models import User , Acessos, Parceiro
from app.database import db
from flask_cors import cross_origin
from time import sleep
import MetaTrader5 as mt5


# Inicializa o MetaTrader5
if not mt5.initialize():
    print("Não foi possível inicializar o MetaTrader5")
    quit()
    
def init_routes_broker(app):
    @app.route('/sse/<int:id>', methods=['GET'])
    def sse(id):

        token = request.args.get('token')
        if not token:
            return jsonify({"msg": "Token não Informado"}), 400

        try:
            # Configura manualmente o token para ser usado na requisição atual
            with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):

                print(token)
                # Verifica o JWT na requisição atual 
                verify_jwt_in_request()  # Verifica o JWT
                additional_claims = get_jwt()
                access = additional_claims.get('acessos', None)

                # Verifica se existe um dicionário na lista com 'parceiro_id' igual a 3
                existe_id = any(d['parceiro_id'] == id for d in access)
                if not existe_id:
                    return jsonify({'message': 'Sem acesso ao Parceiro'}), 400
                
                # user_id = additional_claims.get('user_id', None)
                # acessos_user = Acessos.query.filter_by(usuario_id=user_id, ativo=True).all()
                # existe_id_user = any(d['parceiro_id'] == id for d in acessos_user)
                # if not existe_id_user:
                #     return jsonify({'message': 'Sem acesso ao Parceiro Verifique com Suporte'}), 400
                
                parceiro = Parceiro.query.get(id)
                if not parceiro:
                    return jsonify({'message': 'parceiro não encontrada.'}), 400
                
                plano_parceiro = float(parceiro.plano)
            
        except Exception as e:
            # Caso haja algum erro na verificação do token, retorna a mensagem de erro
            return jsonify({"msg": "Token é invalido.", "error": str(e)}), 401


        def generate(plano_parceiro):

            # planos_valor = serialize_enum(PlanoValor)
            # planos = planos_valor.get(plano_parceiro)
            # if not planos:
            #     return jsonify({'message': 'PLANO não encontrada.'}), 400 
            
            while True:
                valor_dolar = 0

                valor_xauusd_data = mt5.copy_rates_from_pos('GOLD', mt5.TIMEFRAME_M1, 0, 1)
                valor_xauusd = [y['close'] for y in valor_xauusd_data] if valor_xauusd_data else [0]

                valor_usdbrl_data = mt5.copy_rates_from_pos('USDBRL', mt5.TIMEFRAME_M1, 0, 1)
                valor_usdbrl = [y['close'] for y in valor_usdbrl_data] if valor_usdbrl_data else [0]

                if valor_xauusd and valor_usdbrl:
                    valor_dolar = (valor_xauusd[0] / 31.1034768) * valor_usdbrl[0]

                    # Preparando o dicionário de dados
                    # dados = {
                    #     "valor_onca": valor_xauusd[0],
                    #     "valor_dolar": valor_usdbrl[0],
                    #     "valor_grama_real": valor_dolar,
                    #     "negociado":    round( valor_dolar - (valor_dolar * planos) , 4 )
                    # }

                    dados = {
                        "valor_onca": f"{round(valor_xauusd[0], 2):.2f}",
                        "valor_dolar": f"{round(valor_usdbrl[0], 2):.2f}",
                        "valor_grama_real": f"{round(valor_dolar, 2):.2f}",
                        "negociado": f"{round(valor_dolar - (valor_dolar * plano_parceiro), 4):.2f}"
                    }

                    # Serializando o dicionário para JSON e formatando para SSE
                    data = f"data:{json.dumps(dados)}\n\n"
                    print(data)
                    yield data

                sleep(1)
        
        print(plano_parceiro)
        return Response(generate(plano_parceiro), mimetype='text/event-stream')



def serialize_enum(enum):
    """ Retorna um dicionário de todos os valores do enum """
    return {e.name: e.value for e in enum}