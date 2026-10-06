from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from entidades.models import UsuarioLogin
from dependencies.database import database
from controllers import AuthController


auth_router = APIRouter()

@auth_router.post("/auth/login")
def usuario_login(credenciais:UsuarioLogin,db:Session = Depends(database.get_db)):
    try:
       token= AuthController.fazer_login(db,credenciais.email,credenciais.senha)
       return token

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=str(e))




