from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from entidades.models import CategoriaEquipamento
from dependencies.database import database
from controllers import CategoriaEquipamentoController

#Prefixo para não precisar ficar colocando /niveis-acesso toda vez
categoria_equipamento_router = APIRouter(prefix="/categorias", tags=["Categoria Equipamento"])

@categoria_equipamento_router.post("/", response_model=CategoriaEquipamento, status_code=status.HTTP_201_CREATED)
def inserir(categoria: CategoriaEquipamento, db: Session = Depends(database.get_db)):
    try:
        return CategoriaEquipamentoController.inserir_categoria(categoria, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@categoria_equipamento_router.get("/", response_model=List[CategoriaEquipamento], status_code=status.HTTP_200_OK)
def listar(db: Session = Depends(database.get_db)):
    try:
        return CategoriaEquipamentoController.buscar_categorias(db)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@categoria_equipamento_router.get("/{id_categoria}", response_model=CategoriaEquipamento, status_code=status.HTTP_200_OK)
def buscar_por_id(id_categoria: int, db: Session = Depends(database.get_db)):
    try:
        return CategoriaEquipamentoController.buscar_categoria_por_id(id_categoria, db)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@categoria_equipamento_router.put("/{id_categoria}", response_model=CategoriaEquipamento, status_code=status.HTTP_200_OK)
def atualizar(id_categoria: int, dados: CategoriaEquipamento, db: Session = Depends(database.get_db)):
    try:
        return CategoriaEquipamentoController.atualizar_categoria(id_categoria, dados, db)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@categoria_equipamento_router.delete("/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(id_categoria: int, db: Session = Depends(database.get_db)):
    try:
        CategoriaEquipamentoController.deletar_categoria(id_categoria, db)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))