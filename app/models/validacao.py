from app.models.models import User


def valideUserInterno(id):

    usuario = User.query.get(id)
    if not usuario:
        return False
    
    if not usuario.interno:
        return False
    
    if not usuario.ativo:
        return False
    
    return True
