from sqlmodel import Session, select
from entidades.models import Emprestimo, EmprestimoPublico, Equipamento, Usuario
from sqlalchemy.exc import OperationalError, IntegrityError

def cadastrar_emprestimo(db: Session, dados_entrada: EmprestimoPublico) -> Emprestimo:
    try:
        # Valida se o equipamento existe
        equipamento = db.get(Equipamento, dados_entrada.id_equipamento)
        if not equipamento:
            raise ValueError("O equipamento informado não existe.")
        
        # Valida se o usuário solicitante existe
        usuario = db.get(Usuario, dados_entrada.id_usuario_solicitante)
        if not usuario:
            raise ValueError("O usuário solicitante informado não existe.")
        
        novo_emprestimo = Emprestimo(**dados_entrada.model_dump())
        db.add(novo_emprestimo)
        db.commit()
        db.refresh(novo_emprestimo)
        return novo_emprestimo

    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha na conexão com o banco de dados.") from e
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Erro de integridade ao registrar empréstimo.") from e

def buscar_emprestimos(db: Session) -> list[Emprestimo]:
    try:
        statement = select(Emprestimo)
        return db.exec(statement).all()
    except OperationalError as e:
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e

def buscar_emprestimo_por_id(db: Session, id_emprestimo: int) -> Emprestimo:
    try:
        emprestimo = db.get(Emprestimo, id_emprestimo)
        if not emprestimo:
            raise KeyError(f"Empréstimo de ID {id_emprestimo} não encontrado.")
        return emprestimo
    except OperationalError as e:
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e

def atualizar_emprestimo(db: Session, id_emprestimo: int, dados_atualizados: Emprestimo) -> Emprestimo:
    try:
        emprestimo = db.get(Emprestimo, id_emprestimo)
        if not emprestimo:
            raise KeyError(f"Empréstimo de ID {id_emprestimo} não encontrado.")
        
        emprestimo_data = dados_atualizados.model_dump(exclude_unset=True)
        for key, value in emprestimo_data.items():
            setattr(emprestimo, key, value)
        
        db.add(emprestimo)
        db.commit()
        db.refresh(emprestimo)
        return emprestimo
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e

def deletar_emprestimo(db: Session, id_emprestimo: int):
    try:
        emprestimo = db.get(Emprestimo, id_emprestimo)
        if not emprestimo:
            raise KeyError(f"Empréstimo de ID {id_emprestimo} não encontrado.")
        
        db.delete(emprestimo)
        db.commit()
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e