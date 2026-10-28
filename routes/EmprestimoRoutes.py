from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from dependencies.database import database
from dependencies.auth_utils import RoleChecker
from entidades.models import Emprestimo, EmprestimoPublico
from controllers import EmprestimoController

emprestimo_router = APIRouter(prefix="/emprestimos", tags=["Emprestimos"])

#
@emprestimo_router.post("/emprestimos", response_model=Emprestimo, status_code=status.HTTP_201_CREATED,dependencies=[Depends(RoleChecker(["Solicitante"]))])
def criar_emprestimo(dados: EmprestimoPublico, db: Session = Depends(database.get_db)):
    try:
        return EmprestimoController.cadastrar_emprestimo(db, dados)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@emprestimo_router.get("/emprestimos", response_model=List[Emprestimo], status_code=status.HTTP_200_OK)
def listar_emprestimos(db: Session = Depends(database.get_db)):
    try:
        return EmprestimoController.buscar_emprestimos(db)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@emprestimo_router.get("/emprestimos/{id_emprestimo}", response_model=Emprestimo, status_code=status.HTTP_200_OK)
def buscar_emprestimo_por_id(id_emprestimo: int, db: Session = Depends(database.get_db)):
    try:
        return EmprestimoController.buscar_emprestimo_por_id(db, id_emprestimo)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
#rolechecker para testar permissões do perfil -- dependencies=[Depends(RoleChecker(["Solicitante"]))]
@emprestimo_router.put("/emprestimos/{id_emprestimo}", response_model=Emprestimo, status_code=status.HTTP_200_OK, dependencies=[Depends(RoleChecker(["Gestor"]))])
def atualizar_emprestimo(id_emprestimo: int, dados: Emprestimo, db: Session = Depends(database.get_db)):
    try:
        return EmprestimoController.atualizar_emprestimo(db, id_emprestimo, dados)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@emprestimo_router.delete("/emprestimos/{id_emprestimo}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_emprestimo(id_emprestimo: int, db: Session = Depends(database.get_db)):
    try:
        EmprestimoController.deletar_emprestimo(db, id_emprestimo)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))