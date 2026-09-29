from sqlmodel import Session, select
from entidades.models import Usuario, NivelDeAcesso
from sqlalchemy.exc import OperationalError, IntegrityError


def cadastrar_usuario(db:Session, dados : Usuario):
    try: 
        
        novo_usuario = Usuario(**dados.model_dump())
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        return novo_usuario

    except OperationalError as e:
            db.rollback()
            raise RuntimeError("Falha na conexão com o banco de dados.") from e 
        
    except IntegrityError as e :
            db.rollback()
            raise ValueError("Usuario indisponivel") from e
    
def buscar_usuario(db:Session)-> list[Usuario]:
    try:
        statement = select(Usuario)
        usuarios = db.exec(statement).all()
        return usuarios
    
    except OperationalError as e:
        raise RuntimeError("Falha de cominicação com o banco de dados") from e


# BUSCA USUARIO POR ID

def buscar_usuario_por_id(db: Session, id_usuario: int) -> Usuario:
    try:
        usuario = db.get(Usuario, id_usuario)
        if not usuario:
            raise KeyError(f"Usuário de ID {id_usuario} não encontrado.")
        return usuario
    except OperationalError as e:
        raise RuntimeError("Falha de comunicação com o banco de dados") from e

def atualizar_usuario(db: Session, id_usuario: int, dados_atualizados: Usuario) -> Usuario:
    try:
        usuario = db.get(Usuario, id_usuario)
        if not usuario:
            raise KeyError(f"Usuário de ID {id_usuario} não encontrado.")
        
        # Atualiza os campos fornecidos
        usuario_data = dados_atualizados.model_dump(exclude_unset=True)
        for key, value in usuario_data.items():
            setattr(usuario, key, value)
        
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario
        
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Erro de integridade. Verifique se o login já existe.") from e
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e

def deletar_usuario(db: Session, id_usuario: int):
    try:
        usuario = db.get(Usuario, id_usuario)
        if not usuario:
            raise KeyError(f"Usuário de ID {id_usuario} não encontrado.")
        
        db.delete(usuario)
        db.commit()
        
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e

