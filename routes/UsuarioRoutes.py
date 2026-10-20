from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from dependencies.database import database
from entidades.models import Usuario
from controllers import UsuarioController
from dependencies.auth_utils import RoleChecker

from typing import List


usuario_router = APIRouter(prefix="/usuario", tags=["Usuarios"])

@usuario_router.post("", response_model=Usuario,status_code=status.HTTP_201_CREATED,
                     dependencies=[Depends(RoleChecker(["Administrador","Admin","Gestor"]))])
def cadastrar_usuario(dados : Usuario, db:Session = Depends(database.get_db)):
    try:
        return UsuarioController.cadastrar_usuario(db, dados)

    except ValueError as e: 
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(e))
    
    except RuntimeError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))

#LISTA USUARIS
@usuario_router.get("/usuarios", response_model=List[Usuario], status_code=status.HTTP_200_OK,
                    dependencies=[Depends(RoleChecker(["Administrador","Admin","Gestor"]))])
def buscar_usuario(db: Session = Depends(database.get_db)):
    try:
        return UsuarioController.buscar_usuario(db)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

#busca usuario por id
@usuario_router.get("/{id_usuario}", response_model=Usuario, status_code=status.HTTP_200_OK,
                    dependencies=[Depends(RoleChecker(["Administrador","Admin","Gestor"]))])
def buscar_usuario_por_id(id_usuario: int, db: Session = Depends(database.get_db)):
    try:
        return UsuarioController.buscar_usuario_por_id(db, id_usuario)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


#Aletrar dados do usuario
@usuario_router.put("/{id_usuario}", response_model=Usuario, status_code=status.HTTP_200_OK,
                    dependencies=[Depends(RoleChecker(["Administrador","Admin","Gestor"]))])
def atualizar_usuario(id_usuario: int, dados: Usuario, db: Session = Depends(database.get_db)):
    try:
        return UsuarioController.atualizar_usuario(db, id_usuario, dados)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@usuario_router.delete("/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT,
                       dependencies=[Depends(RoleChecker(["Administrador","Admin"]))])
def deletar_usuario(id_usuario: int, db: Session = Depends(database.get_db)):
    try:
        UsuarioController.deletar_usuario(db, id_usuario)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

