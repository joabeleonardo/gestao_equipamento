from datetime import datetime, date
from sqlmodel import Session, select
from entidades.models import (Emprestimo, EmprestimoPublico, Equipamento, Usuario,
                              EnumEquipamento, EnumStatusEmprestimo as St)
from sqlalchemy.exc import OperationalError, IntegrityError

# Mudanças de status permitidas: (de, para)
TRANSICOES = {
    (St.pendente, St.aprovada), (St.pendente, St.negada),
    (St.aprovada, St.devolvido), (St.atrasada, St.devolvido),
}



from datetime import date, datetime


def _sem_fuso(d):
    if d is None:
        return None

    if isinstance(d, str):
        d = datetime.fromisoformat(d.replace("Z", "+00:00"))

    if isinstance(d, datetime):
        return d.replace(tzinfo=None)

    if isinstance(d, date):
        return datetime.combine(d, datetime.min.time())

    raise TypeError(
        f"Tipo de data não suportado: {type(d).__name__}"
    )


def cadastrar_emprestimo(db: Session, dados_entrada: EmprestimoPublico, id_solicitante: int) -> Emprestimo:
    try:
        equipamento = db.get(Equipamento, dados_entrada.id_equipamento)
        if not equipamento:
            raise ValueError("O equipamento informado não existe.")
        if equipamento.status_equipamento != EnumEquipamento.disponivel:
            raise ValueError("O equipamento não está disponível para empréstimo.")
        if not db.get(Usuario, id_solicitante):
            raise ValueError("O usuário solicitante informado não existe.")

        prazo = _sem_fuso(dados_entrada.prazo_devolucao)
        if not prazo:
            raise ValueError("Informe o prazo de devolução.")
        if prazo <= datetime.utcnow():
            raise ValueError("O prazo de devolução deve ser uma data futura.")

        # status e aprovador não vêm do cliente: todo pedido nasce "pendente"
        novo_emprestimo = Emprestimo(
            id_equipamento=dados_entrada.id_equipamento,
            id_usuario_solicitante=id_solicitante,
            prazo_devolucao=prazo,
            status_solicitacao=St.pendente,
        )
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


def buscar_emprestimos(db: Session, id_solicitante: int | None = None) -> list[Emprestimo]:
    try:
        statement = select(Emprestimo)
        if id_solicitante is not None:
            statement = statement.where(Emprestimo.id_usuario_solicitante == id_solicitante)
        emprestimos = db.exec(statement).all()

        # empréstimo aprovado com prazo vencido passa a "atrasada"
        agora, mudou = datetime.utcnow(), False
        for e in emprestimos:
            if e.status_solicitacao == St.aprovada and e.prazo_devolucao and _sem_fuso(e.prazo_devolucao) < agora:
                e.status_solicitacao = St.atrasada
                db.add(e)
                mudou = True
        if mudou:
            db.commit()
        return emprestimos
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


def atualizar_emprestimo(db: Session, id_emprestimo: int, dados: Emprestimo, id_responsavel: int) -> Emprestimo:
    """Aplica a decisão do gestor. Só o status (e o prazo, ao aprovar) são aceitos do cliente;
    datas, aprovador e status do equipamento são definidos aqui."""
    try:
        emprestimo = db.get(Emprestimo, id_emprestimo)
        if not emprestimo:
            raise KeyError(f"Empréstimo de ID {id_emprestimo} não encontrado.")

        anterior, novo = emprestimo.status_solicitacao, dados.status_solicitacao
        if novo != anterior:
            if (anterior, novo) not in TRANSICOES:
                raise ValueError(f"Não é possível mudar o empréstimo de '{anterior.value}' para '{novo.value}'.")

            equipamento = db.get(Equipamento, emprestimo.id_equipamento)
            agora = datetime.utcnow()

            if novo == St.aprovada:
                if not equipamento or equipamento.status_equipamento != EnumEquipamento.disponivel:
                    raise ValueError("O equipamento não está disponível para empréstimo.")
                prazo = _sem_fuso(dados.prazo_devolucao) or _sem_fuso(emprestimo.prazo_devolucao)
                if not prazo or prazo <= agora:
                    raise ValueError("Informe um prazo de devolução futuro para aprovar.")
                emprestimo.prazo_devolucao = prazo
                emprestimo.data_aprovacao = agora
                emprestimo.id_usuario_aprovador = id_responsavel
                equipamento.status_equipamento = EnumEquipamento.emprestado
                db.add(equipamento)
            elif novo == St.devolvido:
                emprestimo.data_devolucao = agora
                if equipamento:
                    equipamento.status_equipamento = EnumEquipamento.disponivel
                    db.add(equipamento)
            else:  # negada
                emprestimo.id_usuario_aprovador = id_responsavel

            emprestimo.status_solicitacao = novo

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

        # se o empréstimo estava em aberto, o equipamento volta a ficar disponível
        if emprestimo.status_solicitacao in (St.aprovada, St.atrasada):
            equipamento = db.get(Equipamento, emprestimo.id_equipamento)
            if equipamento:
                equipamento.status_equipamento = EnumEquipamento.disponivel
                db.add(equipamento)

        db.delete(emprestimo)
        db.commit()
    except OperationalError as e:
        db.rollback()
        raise RuntimeError("Falha de comunicação com o banco de dados.") from e
