from sqlmodel import Session, select
from entidades.models import Usuario, NivelDeAcesso, PerfilDeUsuario, UsuarioAtualizacao, MeuPerfilAtualizacao
from sqlalchemy.exc import OperationalError, IntegrityError
from core.security import criptografar_senha, verifica_senha


def cadastrar_usuario(db:Session, dados : Usuario):
    try: 
        
        novo_usuario = Usuario(**dados.model_dump())
        novo_usuario.senha = criptografar_senha(dados.senha)  # nunca salvar senha pura
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

def atualizar_usuario(db: Session, id_usuario: int, dados_atualizados: UsuarioAtualizacao) -> Usuario:
    try:
        usuario = db.get(Usuario, id_usuario)
        if not usuario:
            raise KeyError(f"Usuário de ID {id_usuario} não encontrado.")
        
        # Atualiza os campos fornecidos
        usuario_data = dados_atualizados.model_dump(exclude_unset=True)
        usuario_data = {k: v for k, v in usuario_data.items() if v is not None}
        if usuario_data.get("senha"):
            usuario_data["senha"] = criptografar_senha(usuario_data["senha"])
        else:
            usuario_data.pop("senha", None)
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

def atualizar_meu_perfil(db: Session, id_usuario: int, dados: MeuPerfilAtualizacao) -> Usuario:
    """Edição do próprio perfil. Só nome, telefone, login e senha podem mudar."""
    campos = {k: v for k, v in dados.model_dump(exclude_unset=True).items() if v is not None}
    nova_senha = campos.pop("nova_senha", None)
    senha_atual = campos.pop("senha_atual", None)

    if nova_senha:
        usuario = db.get(Usuario, id_usuario)
        if not usuario:
            raise KeyError(f"Usuário de ID {id_usuario} não encontrado.")
        if not senha_atual or not verifica_senha(senha_atual, usuario.senha):
            raise ValueError("Senha atual incorreta.")
        campos["senha"] = nova_senha

    return atualizar_usuario(db, id_usuario, UsuarioAtualizacao(**campos))


def deletar_usuario(db: Session, id_usuario: int):
    try:
        usuario = db.get(Usuario, id_usuario)
        if not usuario:
            raise KeyError(f"Usuário de ID {id_usuario} não encontrado.")
        
        if db.exec(select(PerfilDeUsuario).where(PerfilDeUsuario.acesso_id_usuario == id_usuario)).first():
            raise ValueError("Usuário possui perfis de acesso vinculados e não pode ser excluído.")

        db.delete(usuario)
        db.commit()
        
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Usuário possui empréstimos registrados e não pode ser excluído.") from e
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e

