from entidades.models import NivelDeAcesso
from sqlmodel import Session, select
from sqlalchemy.exc import OperationalError, IntegrityError

def inserir_nivel_acesso(nivel_de_acesso: NivelDeAcesso, db: Session) -> NivelDeAcesso:
    try:
        nivel_insert = NivelDeAcesso.model_validate(nivel_de_acesso)
        db.add(nivel_insert)
        db.commit()
        db.refresh(nivel_insert)
        return nivel_insert
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Erro de integridade. Verifique se este nível já existe.") from e
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com a base de dados.") from e

def buscar_niveis_acesso(db: Session) -> list[NivelDeAcesso]:
    try:
        statement = select(NivelDeAcesso)
        return db.exec(statement).all()
    except OperationalError as e:
        raise RuntimeError("Falha de comunicação com a base de dados.") from e

def buscar_nivel_acesso_por_id(id_nivel_acesso: int, db: Session) -> NivelDeAcesso:
    try:
        nivel = db.get(NivelDeAcesso, id_nivel_acesso)
        if not nivel:
            raise KeyError(f"Nível de acesso de ID {id_nivel_acesso} não encontrado.")
        return nivel
    except OperationalError as e:
        raise RuntimeError("Falha de comunicação com a base de dados.") from e

def atualizar_nivel_acesso(id_nivel_acesso: int, dados_atualizados: NivelDeAcesso, db: Session) -> NivelDeAcesso:
    try:
        nivel = db.get(NivelDeAcesso, id_nivel_acesso)
        if not nivel:
            raise KeyError(f"Nível de acesso de ID {id_nivel_acesso} não encontrado.")
        
        nivel_data = dados_atualizados.model_dump(exclude_unset=True)
        for key, value in nivel_data.items():
            setattr(nivel, key, value)
        
        db.add(nivel)
        db.commit()
        db.refresh(nivel)
        return nivel
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Erro de integridade ao atualizar nível de acesso.") from e
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com a base de dados.") from e

def deletar_nivel_acesso(id_nivel_acesso: int, db: Session):
    try:
        nivel = db.get(NivelDeAcesso, id_nivel_acesso)
        if not nivel:
            raise KeyError(f"Nível de acesso de ID {id_nivel_acesso} não encontrado.")
        
        db.delete(nivel)
        db.commit()
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com a base de dados.") from e