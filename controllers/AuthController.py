from entidades.models import Usuario
from core.security import verifica_senha

from sqlmodel import Session, select
from sqlalchemy.exc import OperationalError, IntegrityError

def fazer_login(db:Session, username:str, password:str):
    try:
        usuario = db.exec(select(Usuario).where(Usuario.login == username))

        usuario = usuario if not None and verifica_senha(password,Usuario.senha)

        if not usuario:
            raise ValueError ("Credenciais inválidas.")
        
# 1:N
        # roles = db.exec(select(roles.descricao).join(Usuario).where(Usuario.id_usuario == Usuario.id_usuario)).all

        roles = db.exec(select(Roles.roles_descricao).
                        join(UsuarioHasRole,Roles.roles_id ==
                             UsuarioHasRole.usuario_has_role_role_id).
                        where(UsuarioHasRole.usuario_has_role_id_usuario == Usuario.id_usuario))

    except OperationalError as e:
        raise ValueError ("Credenciais Inválidas.")
