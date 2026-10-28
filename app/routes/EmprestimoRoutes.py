from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from dependencies.database import database
from dependencies.auth_utils import RoleChecker
from entidades.models import Emprestimo, EmprestimoPublico
from controllers import EmprestimoController

emprestimo_router = APIRouter(prefix="/emprestimos", tags=["Emprestimos"])

GESTAO = ["Gestor", "Administrador", "Admin"]
TODOS = ["Solicitante"] + GESTAO


def eh_gestao(payload: dict) -> bool:
    return any(r in GESTAO for r in payload.get("roles", []))


# POST /emprestimos — o solicitante é SEMPRE o usuário do token
@emprestimo_router.post("", response_model=Emprestimo, status_code=status.HTTP_201_CREATED)
def criar_emprestimo(dados: EmprestimoPublico, db: Session = Depends(database.get_db),
                     usuario: dict = Depends(RoleChecker(TODOS))):
    try:
        return EmprestimoController.cadastrar_emprestimo(db, dados, int(usuario["sub"]))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# GET /emprestimos — gestão vê todos; solicitante vê só os próprios
@emprestimo_router.get("", response_model=List[Emprestimo], status_code=status.HTTP_200_OK)
def listar_emprestimos(db: Session = Depends(database.get_db), usuario: dict = Depends(RoleChecker(TODOS))):
    try:
        so_do_usuario = None if eh_gestao(usuario) else int(usuario["sub"])
        return EmprestimoController.buscar_emprestimos(db, so_do_usuario)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@emprestimo_router.get("/{id_emprestimo}", response_model=Emprestimo, status_code=status.HTTP_200_OK)
def buscar_emprestimo_por_id(id_emprestimo: int, db: Session = Depends(database.get_db),
                             usuario: dict = Depends(RoleChecker(TODOS))):
    try:
        emprestimo = EmprestimoController.buscar_emprestimo_por_id(db, id_emprestimo)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    if not eh_gestao(usuario) and emprestimo.id_usuario_solicitante != int(usuario["sub"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Este empréstimo não é seu.")
    return emprestimo


# PUT /emprestimos/{id} — aprovar, negar ou registrar devolução (gestão)
@emprestimo_router.put("/{id_emprestimo}", response_model=Emprestimo, status_code=status.HTTP_200_OK)
def atualizar_emprestimo(id_emprestimo: int, dados: Emprestimo, db: Session = Depends(database.get_db),
                         usuario: dict = Depends(RoleChecker(GESTAO))):
    try:
        return EmprestimoController.atualizar_emprestimo(db, id_emprestimo, dados, int(usuario["sub"]))
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@emprestimo_router.delete("/{id_emprestimo}", status_code=status.HTTP_204_NO_CONTENT,
                          dependencies=[Depends(RoleChecker(GESTAO))])
def deletar_emprestimo(id_emprestimo: int, db: Session = Depends(database.get_db)):
    try:
        EmprestimoController.deletar_emprestimo(db, id_emprestimo)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
