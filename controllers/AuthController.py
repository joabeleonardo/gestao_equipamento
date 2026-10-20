from entidades.models import Usuario, NivelDeAcesso, PerfilDeUsuario
from core.security import verifica_senha

from sqlmodel import Session, select
from sqlalchemy.exc import OperationalError, IntegrityError

def fazer_login(db:Session, username:str, password:str):
    try:
        usuario = db.exec(select(Usuario).where(Usuario.login==username)).first()
        senha = usuario is not None and verifica_senha(password,usuario.senha)
        
        if not senha:
            raise ValueError ("Credenciais inválidas.")
        
# 1:N
        # roles = db.exec(select(roles.descricao).join(Usuario).where(Usuario.id_usuario == Usuario.id_usuario)).all

        perfis = db.exec(select(NivelDeAcesso.nivel_acesso.nivel).
                        join(PerfilDeUsuario,NivelDeAcesso.id_nivel_acesso ==
                             PerfilDeUsuario.acesso_id_nivel_acesso).
                        where(PerfilDeUsuario.acesso_id_usuario == Usuario.id_usuario))

    except OperationalError as e:
        raise ValueError ("Credenciais Inválidas.")
