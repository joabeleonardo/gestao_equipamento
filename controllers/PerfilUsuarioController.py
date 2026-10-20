from sqlmodel import Session, select
from sqlalchemy.exc import OperationalError, IntegrityError
from entidades.models import (
    PerfilDeUsuario,
    PerfilDeUsuarioPublico,
    Usuario,
    NivelDeAcesso,
)


# ----------------------------------------------------------------------------
# LISTAR TODOS OS VÍNCULOS (usuario x role)
# ----------------------------------------------------------------------------
def buscar_vinculos(db: Session) -> list[PerfilDeUsuario]:
    try:
        return db.exec(select(PerfilDeUsuario)).all()
    except OperationalError as e:
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e


# ----------------------------------------------------------------------------
# BUSCAR UM VÍNCULO ESPECÍFICO
# Como a PK é composta (id_usuario, id_nivel_aceeso), passamos uma TUPLA em db.get().
# ----------------------------------------------------------------------------
def buscar_vinculo(db: Session, id_usuario: int, id_nivel_acesso: int) -> PerfilDeUsuario:
    try:
        vinculo = db.get(PerfilDeUsuario, (id_usuario, id_nivel_acesso))
        if not vinculo:
            raise KeyError(
                f"Vínculo usuário {id_usuario} x role {id_nivel_acesso} não encontrado."
            )
        return vinculo
    except OperationalError as e:
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e


# ----------------------------------------------------------------------------
# CADASTRAR VÍNCULO (ACESSO)
# ----------------------------------------------------------------------------
def cadastrar_vinculo(
    db: Session, dados_entrada: PerfilDeUsuarioPublico
) -> PerfilDeUsuario:
    try:
        #Integridade... usuário existe?
        if not db.get(Usuario, dados_entrada.acesso_id_usuario):
            raise ValueError("Usuário informado não está cadastrado no sistema.")

        #integridade referencial: o nivel de acesso(perfil) existe?
        if not db.get(NivelDeAcesso, dados_entrada.acesso_id_nivel_acesso):
            raise ValueError("Role informada não está cadastrada no sistema.")

        #vínculo
        novo_vinculo = PerfilDeUsuario(**dados_entrada.model_dump())
        db.add(novo_vinculo)
        db.commit()
        db.refresh(novo_vinculo)
        return novo_vinculo
    except IntegrityError as e:
        # PK composta duplicada -> este vínculo já existe
        db.rollback()
        raise ValueError("Este vínculo já existe ou os dados são inválidos.") from e
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e


# ----------------------------------------------------------------------------
# DELETAR VÍNCULO (ACESSO/Perfil)
# ----------------------------------------------------------------------------
def deletar_vinculo(db: Session, id_usuario: int, id_nivel_acesso: int) -> None:
    try:
        vinculo = db.get(PerfilDeUsuario, (id_usuario, id_nivel_acesso))
        if not vinculo:
            raise KeyError(
                f"Vínculo usuário {id_usuario} x role {id_nivel_acesso} não encontrado."
            )
        db.delete(vinculo)
        db.commit()
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e