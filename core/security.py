import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from config.config import settings
from datetime import datetime, timezone, timedelta

from jwt.exceptions import ExpiredSignatureError, PyJWTError

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def criptografar_senha(senha:str):
    return pwd_context.hash(senha)
    pass

def verifica_senha(senha_informada:str, senha_banco:str):
    return pwd_context.verify(senha_informada,senha_banco)

def create_token(id_usuario:str, roles:list[str]):
    vence_em = datetime.now(timezone.utc)+settings.JWT_ACCESS_EXPIRE_MINUTES

    payload = {
        "sub": id_usuario,
        "exp": vence_em,
        "roles": roles,
        "iss": settings.JWT_ISSUER

    }

    token = jwt.encode(payload,
                       settings.JWT_SECRET_KEY,
                       settings.JWT_ALGORITHM)
    return token

#VALIDAR TOKEN DE ACESSO JWT
def validar_token(token: str) -> dict:
    try:
        # Tenta abrir a identificação do user usando a chave secreta do seu sistema
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER
        )
        return payload  # Retorna os dados, incluindo o "sub" (id) e as "roles" (níveis de acesso)

    except ExpiredSignatureError:
        # Lança erro HTTP 401 se o tempo do token já acabou
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado. Faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except PyJWTError:
        # Lança erro HTTP 401 se o token for falso ou malformado
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou credenciais incorretas.",
            headers={"WWW-Authenticate": "Bearer"},
        )