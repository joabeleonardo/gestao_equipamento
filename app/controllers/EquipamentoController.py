from sqlmodel import Session, select
from entidades.models import Equipamento, CategoriaEquipamento,EquipamentoPublico, EnumEquipamento
from sqlalchemy.exc import OperationalError, IntegrityError


def buscar_equipamento(db:Session)-> list[Equipamento]:
    try:
        statement = select(Equipamento)
        equipamentos = db.exec(statement).all()
        return equipamentos
    except OperationalError as e:
        raise RuntimeError("Falha de cominicação com o banco de dados") from e



def cadastrar_equipamento(db:Session, dados_entrada: EquipamentoPublico)->Equipamento:
    try:
        #VERIFICA SE A CATEGORIA EXISTE
        categoria = db.get(CategoriaEquipamento,
                           dados_entrada.id_categoria)
        if not categoria: 
            raise ValueError("A CATEGORIA INFORMADA NÃO EXISTE.")
        
        novo_equipamento = Equipamento(**dados_entrada.model_dump())
        db.add(novo_equipamento)
        db.commit()
        db.refresh(novo_equipamento)
        return novo_equipamento

    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha na conexão com o banco de dados.") from e 
    
    except IntegrityError as e :
        db.rollback()
        raise ValueError("Verifique se o número de patrimônio já existe. ") from e

# BUSCAR EQUIPAMENTO POR ID
def buscar_equipamento_por_id(db: Session, id_equipamento: int) -> Equipamento:
    try:
        equipamento = db.get(Equipamento, id_equipamento)
        if not equipamento:
            raise KeyError(f"Equipamento de ID {id_equipamento} não encontrado.")
        return equipamento
    except OperationalError as e:
        raise RuntimeError("Falha de comunicação com o banco de dados") from e

#ATUALIZA DADOS DO EQUIPAMENTO
def atualizar_equipamento(db: Session, id_equipamento: int, dados_atualizados: Equipamento) -> Equipamento:
    try:
        equipamento = db.get(Equipamento, id_equipamento)
        if not equipamento:
            raise KeyError(f"Equipamento de ID {id_equipamento} não encontrado.")
        
        # Se o usuário tentar alterar a categoria, valida se a nova categoria existe
        if dados_atualizados.id_categoria:
            categoria = db.get(CategoriaEquipamento, dados_atualizados.id_categoria)
            if not categoria:
                raise ValueError(f"A categoria informada não existe.")
        # Valida os dados de entrada.
        Equipamento.model_validate(dados_atualizados)
        equipamento_data = dados_atualizados.model_dump(exclude_unset=True)
        equipamento_data.pop("id_equipamento", None)

        # "emprestado" é definido pelos empréstimos (aprovação/devolução), nunca à mão
        novo_status = equipamento_data.get("status_equipamento")
        if novo_status is not None and novo_status != equipamento.status_equipamento \
                and EnumEquipamento.emprestado in (novo_status, equipamento.status_equipamento):
            raise ValueError("O status 'emprestado' é controlado pelos empréstimos e não pode ser alterado manualmente.")
        for key, value in equipamento_data.items():
            setattr(equipamento, key, value)
        
        db.add(equipamento)
        db.commit()
        db.refresh(equipamento)
        
        return equipamento
        
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Erro de integridade. Verifique se o número de patrimônio já existe.") from e
        
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e

def deletar_equipamento(db: Session, id_equipamento: int):
    try:
        equipamento = db.get(Equipamento, id_equipamento)
        if not equipamento:
            raise KeyError(f"Equipamento de ID {id_equipamento} não encontrado.")
        
        db.delete(equipamento)
        db.commit()
        
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Equipamento possui empréstimos registrados e não pode ser excluído.") from e
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e





