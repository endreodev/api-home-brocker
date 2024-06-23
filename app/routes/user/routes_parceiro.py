from flask import jsonify, request, abort
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_jwt, verify_jwt_in_request 
from app.database import db
from app.models.models import Grupo, Parceiro, Empresa,Acessos

def init_routes_parceiro(app):
    # CADASTRAR PARCEIRO NOVO
    @app.route('/parceiro', methods=['POST'])
    @jwt_required()
    def create_parceiro():
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Nenhum dado fornecido.'}), 400
        
        grupo_id = data.get('grupo_id') or None 

        required_fields = ['empresa_id', 'cgc', 'parceiro', 'nome', 'plano','lmt_trava','lmt_mes']
        if not all(data.get(field) for field in required_fields):
            return jsonify({'message': 'Faltando campos obrigatórios ou campos vazios'}), 400

        empresa = Empresa.query.get(data['empresa_id'])
        if not empresa:
            return jsonify({'message': 'Empresa não encontrada.'}), 404
        
        # planos_valor = serialize_enum(Plano)
        # planos = planos_valor.get(data['plano'])
        # if not planos:
        #     return jsonify({'message': 'PLANO não encontrada.'}), 400 

        new_parceiro = Parceiro(
            cod_interno = data.get('cod_interno',''),
            empresa_id  = data.get('empresa_id' ,''),
            cgc         = data.get('cgc',''),
            nome        = data.get('nome',''),
            plano       = data.get('plano',99),
            lmt_trava   = data.get('lmt_trava'), 
            lmt_mes     = data.get('lmt_mes'),
            grupo_id    = grupo_id ,
            ativo       = data.get('ativo', True)
        )

        db.session.add(new_parceiro)
        
        try:
            db.session.commit()
            return jsonify({'message': 'parceiro criada com sucesso!'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Erro ao salvar no banco de dados', 'details': str(e)}), 500

    # BUSCA TODOS OS DADOS DE PARCEIROS
    @app.route('/parceiro', methods=['GET'])
    @jwt_required()
    def get_parceiro():

        parceiros = db.session.query(
            Parceiro, 
            Grupo.nome.label('grupo')
        ).outerjoin(Grupo, Parceiro.grupo_id == Grupo.id).all()

        parceiro_list = [
            {
                'id'         : parceiro.id,     
                'cod_interno': parceiro.cod_interno,
                'empresa_id' : parceiro.empresa_id,
                'cgc'        : parceiro.cgc,      
                'nome'       : parceiro.nome,    
                'plano'      : parceiro.plano,    
                'lmt_trava'  : parceiro.lmt_trava,   
                'lmt_mes'    : parceiro.lmt_mes,    
                'grupo_id'   : parceiro.grupo_id,  
                'grupo'      : grupo,
                'ativo'      : parceiro.ativo 
            } for parceiro, grupo in parceiros
        ]
        return jsonify(parceiro_list)

    #consulta parceiro com id 
    @app.route('/parceiro/<int:id>', methods=['GET'])
    @jwt_required()
    def get_parceiro_id(id):
        parceiro = Parceiro.query.get(id)
        if not parceiro:
            return jsonify({'message': 'Parceiro não encontrada.'}), 400
        return jsonify({
            'id'         : parceiro.id,     
            'cod_interno': parceiro.cod_interno,
            'empresa_id' : parceiro.empresa_id  ,
            'cgc'        : parceiro.cgc,      
            'nome'       : parceiro.nome,    
            'plano'      : parceiro.plano,    
            'lmt_trava'  : parceiro.lmt_trava,   
            'lmt_mes'    : parceiro.lmt_mes,    
            'grupo_id'   : parceiro.grupo_id,  
            'ativo'      : parceiro.ativo 
        })
    

    @app.route('/parceiro/usuario', methods=['GET'])
    @jwt_required()
    def get_parceiros_by_user():
        additional_claims = get_jwt()
        user_id = additional_claims.get('user_id', None)

        # Consulta para buscar os parceiros aos quais o usuário tem acesso
        acessos = Acessos.query.filter_by(usuario_id=user_id, ativo=True).all()
        if not acessos:
            return jsonify({'message': 'Nenhum acesso encontrado para este usuário.'}), 404

        # Cria uma lista dos IDs dos parceiros
        parceiro_ids = [acesso.parceiro_id for acesso in acessos]
        print(parceiro_ids)
        # Busca os parceiros com base nos IDs obtidos
        parceiros = Parceiro.query.filter(Parceiro.id.in_(parceiro_ids)).all()
        
        # Serializa os dados dos parceiros para a resposta
        parceiros_list = [
            {
                'id'         : parceiro.id,     
                'cod_interno': parceiro.cod_interno,
                'empresa_id' : parceiro.empresa_id  ,
                'cgc'        : parceiro.cgc,      
                'nome'       : parceiro.nome,    
                'plano'      : parceiro.plano,    
                'lmt_trava'  : parceiro.lmt_trava,   
                'lmt_mes'    : parceiro.lmt_mes,    
                'grupo_id'   : parceiro.grupo_id,  
                'ativo'      : parceiro.ativo 
            } for parceiro in parceiros
        ]

        return jsonify(parceiros_list)

    # auterar parceiro
    @app.route('/parceiro/<int:id>', methods=['PUT'])
    @jwt_required()
    def update_parceiro(id):
        parceiro = Parceiro.query.get(id)
        if not parceiro:
            return jsonify({'message': 'parceiro não encontrada.'}), 400

        data = request.get_json() 
        grupo_id = data.get('grupo_id', None)
        grupo_id = None if grupo_id == '' else grupo_id

        parceiro.cod_interno   = data.get('cod_interno', parceiro.cod_interno) 
        parceiro.empresa_id    = data.get('empresa_id', parceiro.empresa_id )   
        parceiro.cgc           = data.get('cgc', parceiro.cgc )       
        parceiro.nome          = data.get('nome', parceiro.nome ) 
        parceiro.plano         = data.get('plano', parceiro.plano)   
        parceiro.lmt_trava     = data.get('lmt_trava', parceiro.lmt_trava ) 
        parceiro.lmt_mes       = data.get('lmt_mes', parceiro.lmt_mes ) 
        parceiro.grupo_id      = grupo_id         
        parceiro.ativo         = data.get('ativo', parceiro.ativo ) 

        try:
            db.session.commit()
            return jsonify({'message': 'parceiro atualizada com sucesso!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Erro ao atualizar a parceiro', 'details': str(e)}), 500
    
    # remover parceiro
    @app.route('/parceiro/<int:id>', methods=['DELETE'])
    @jwt_required()
    def delete_parceiro(id):
        parceiro = Parceiro.query.get(id)
        if not parceiro:
            return jsonify({'message': 'parceiro não encontrada.'}), 400 

        try:
            db.session.delete(parceiro)
            db.session.commit()
            return jsonify({'message': 'parceiro deletada com sucesso!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Erro ao deletar a parceiro', 'details': str(e)}), 500
        

def serialize_enum(enum):
    """ Retorna um dicionário de todos os valores do enum """
    return {e.name: e.value for e in enum}