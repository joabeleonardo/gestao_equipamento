from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


from core.security import validar_token

# Define onde o FastAPI deve procurar o token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class RoleChecker: #Chega os perfis
    def __init__(self, allowed_roles: list[str]):
        """
        Define quais papéis (níveis de acesso) podem acessar a rota.
        Ex: allowed_roles=["Administrador", "Gestor"]
        """
        self.allowed_roles = allowed_roles

    def __call__(self, token: str = Depends(oauth2_scheme)):
        # abre o acesso do usuário usando a função core.security que valida o token
        payload = validar_token(token)
        
        #pega a lista de níveis de acesso que o usuário possui
        user_roles = payload.get("roles", [])

        # verifica se o usuaio tem pelo menos um dos niveis de acesso exigidos
        tem_permissao = any(role in self.allowed_roles for role in user_roles)
        
        if not tem_permissao:
            # Tratamento de exceção semântico exigido na avaliação (Erro 403)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Você não tem permissão para realizar esta operação."
            )
        
        # Retorna os dados do usuário (como o ID) caso a rota precise saber quem fez a ação
        return payload