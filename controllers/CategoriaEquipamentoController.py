from entidades.models import CategoriaEquipamento
from sqlmodel import Session, select
from sqlalchemy.exc import OperationalError, IntegrityError

def inserir_categoria(categoria: CategoriaEquipamento, db: Session) -> CategoriaEquipamento:
    try:
        categoria_insert = CategoriaEquipamento.model_validate(categoria)
        db.add(categoria_insert)
        db.commit()
        db.refresh(categoria_insert)
        return categoria_insert
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Erro de integridade ao inserir categoria.") from e
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e

def buscar_categorias(db: Session) -> list[CategoriaEquipamento]:
    try:
        statement = select(CategoriaEquipamento)
        return db.exec(statement).all()
    except OperationalError as e:
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e

def buscar_categoria_por_id(id_categoria: int, db: Session) -> CategoriaEquipamento:
    try:
        categoria = db.get(CategoriaEquipamento, id_categoria)
        if not categoria:
            raise KeyError(f"Categoria de ID {id_categoria} não encontrada.")
        return categoria
    except OperationalError as e:
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e

def atualizar_categoria(id_categoria: int, dados_atualizados: CategoriaEquipamento, db: Session) -> CategoriaEquipamento:
    try:
        categoria = db.get(CategoriaEquipamento, id_categoria)
        if not categoria:
            raise KeyError(f"Categoria de ID {id_categoria} não encontrada.")
        
        categoria_data = dados_atualizados.model_dump(exclude_unset=True)
        for key, value in categoria_data.items():
            setattr(categoria, key, value)
        
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
        return categoria
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Erro de integridade ao atualizar categoria.") from e
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e

def deletar_categoria(id_categoria: int, db: Session):
    try:
        categoria = db.get(CategoriaEquipamento, id_categoria)
        if not categoria:
            raise KeyError(f"Categoria de ID {id_categoria} não encontrada.")
        
        db.delete(categoria)
        db.commit()
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e