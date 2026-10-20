from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session

from entidades.models import PerfilDeUsuario, PerfilDeUsuarioPublico
from controllers import PerfilUsuarioController
from dependencies.database import database
from dependencies.auth_utils import RoleChecker

perfil_usuario_router = APIRouter(tags=["Perfis"],
                                  dependencies=[Depends(RoleChecker(["Administrador","Admin"]))]) #rolechecker para testar permissões do perfil)


# GET — listar todos os vínculos
@perfil_usuario_router.get("/perfil_usuario",response_model=list[PerfilDeUsuario],status_code=status.HTTP_200_OK,)
def buscar_vinculos(db: Session = Depends(database.get_db)):
    try:
        return PerfilUsuarioController.buscar_vinculos(db)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# GET — vínculo específico (PK composta via path params)
@perfil_usuario_router.get("/perfis_usuario/{id_usuario}/{id_nivel_acesso}",response_model=PerfilDeUsuario,)
def buscar_vinculo(id_usuario: int, id_nivel_acesso: int, db: Session = Depends(database.get_db)):
    try:
        return PerfilUsuarioController.buscar_vinculo(db, id_usuario, id_nivel_acesso)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# POST — criar vínculo
@perfil_usuario_router.post(
    "/usuarios-has-role",
    response_model=PerfilDeUsuario,
    status_code=status.HTTP_201_CREATED,
)
def criar_vinculo(
    dados: PerfilDeUsuarioPublico, db: Session = Depends(database.get_db)
):
    try:
        return PerfilUsuarioController.cadastrar_vinculo(db, dados)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# DELETE — remover vínculo
@perfil_usuario_router.delete(
    "/perfis_usuario/{id_usuario}/{id_nivel_acesso}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deletar_vinculo(id_usuario: int, id_nivel_acesso: int, db: Session = Depends(database.get_db)):
    try:
        PerfilUsuarioController.deletar_vinculo(db, id_usuario, id_nivel_acesso)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )