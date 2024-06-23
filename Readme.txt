new_empresa = Empresa(
            cgc=data['cgc'],
            empresa=data['empresa'],
            nome=data['nome'],
            ativo=data.get('ativo', True)  # Assume true se não especificado
        )

flask db init: Inicializa o diretório de migração.
flask db migrate: Gera os arquivos de migração automaticamente a partir das diferenças detectadas nos modelos.
flask db upgrade: Aplica as migrações ao banco de dados para sincronizar os modelos com o banco de dados.
flask db downgrade: Reverte a última migração aplicada.


flask db init
flask db migrate -m "Descrição da migração"
flask db upgrade
flask db downgrade

python.exe -m pip install --upgrade pip
pip install Flask
pip install flask_cors
pip install flask_sqlalchemy
pip install flask_migrate
pip install flask_jwt_extended
pip install requests
pip install firebase_admin
