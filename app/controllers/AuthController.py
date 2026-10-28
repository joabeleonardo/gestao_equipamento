from entidades.models import Usuario, NivelDeAcesso, PerfilDeUsuario
from core.security import verifica_senha, create_token

from sqlmodel import Session, select
from sqlalchemy.exc import OperationalError
import logging

logger = logging.getLogger("uvicorn.error")  # aparece no terminal onde a API está rodando


def fazer_login(db: Session, username: str, password: str):
    try:
        usuario = db.exec(select(Usuario).where(Usuario.login == username)).first()

        # mesma mensagem para login inexistente e senha errada (não revela qual deu erro)
        # o MOTIVO real vai só para o terminal da API (nunca para o navegador, e nunca a senha)
        if usuario is None:
            logger.warning("Login recusado: o login '%s' não existe na tabela usuario.", username)
            raise ValueError("Credenciais inválidas.")
        if not verifica_senha(password, usuario.senha):
            logger.warning("Login recusado: a senha de '%s' não confere ou não está criptografada (argon2). "
                           "Rode: python preparar_banco.py --diagnosticar", username)
            raise ValueError("Credenciais inválidas.")

        # N:N -> nomes dos níveis de acesso do usuário que está logando
        perfis = list(db.exec(
            select(NivelDeAcesso.nivel)
            .join(PerfilDeUsuario, NivelDeAcesso.id_nivel_acesso == PerfilDeUsuario.acesso_id_nivel_acesso)
            .where(PerfilDeUsuario.acesso_id_usuario == usuario.id_usuario)
        ).all())

        token = create_token(usuario.id_usuario, perfis)
        return {
            "access_token": token,
            "token_type": "bearer",
            "usuario": {"id": usuario.id_usuario, "nome": usuario.nome, "perfis": perfis},
        }

    except OperationalError as e:
        logger.error("Login falhou por erro do banco (veja se as colunas batem com o código): %s", e.orig)
        raise ValueError("Não foi possível autenticar agora. Tente novamente.") from e
