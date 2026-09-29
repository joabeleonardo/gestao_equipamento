from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from entidades.models import NivelDeAcesso
from dependencies.database import database
from controllers import NivelDeAcessoController

#Prefixo para não precisar ficar colocando /niveis-acesso toda vez
nivel_acesso_router = APIRouter(prefix="/niveis-acesso", tags=["Níveis de Acesso"])

@nivel_acesso_router.post("/", response_model=NivelDeAcesso, status_code=status.HTTP_201_CREATED)
def inserir(nivel: NivelDeAcesso, db: Session = Depends(database.get_db)):
    try:
        return NivelDeAcessoController.inserir_nivel_acesso(nivel, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@nivel_acesso_router.get("/", response_model=List[NivelDeAcesso], status_code=status.HTTP_200_OK)
def listar(db: Session = Depends(database.get_db)):
    try:
        return NivelDeAcessoController.buscar_niveis_acesso(db)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@nivel_acesso_router.get("/{id_nivel_acesso}", response_model=NivelDeAcesso, status_code=status.HTTP_200_OK)
def buscar_por_id(id_nivel_acesso: int, db: Session = Depends(database.get_db)):
    try:
        return NivelDeAcessoController.buscar_nivel_acesso_por_id(id_nivel_acesso, db)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@nivel_acesso_router.put("/{id_nivel_acesso}", response_model=NivelDeAcesso, status_code=status.HTTP_200_OK)
def atualizar(id_nivel_acesso: int, dados: NivelDeAcesso, db: Session = Depends(database.get_db)):
    try:
        return NivelDeAcessoController.atualizar_nivel_acesso(id_nivel_acesso, dados, db)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@nivel_acesso_router.delete("/{id_nivel_acesso}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(id_nivel_acesso: int, db: Session = Depends(database.get_db)):
    try:
        NivelDeAcessoController.deletar_nivel_acesso(id_nivel_acesso, db)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))