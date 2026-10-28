from sqlmodel import create_engine, Session
from sshtunnel import SSHTunnelForwarder
from config.config import settings
from dataclasses import dataclass
import urllib
from sqlalchemy.engine import Engine

@dataclass
class Database:

    _server: SSHTunnelForwarder | None = None
    _engine: Engine | None = None

    def __post_init__(self):
        """ Procedimentos que devem ser executados após a criação do objeto. 
            É executado apor a função __init__
        """
        self.start_tunnel()


    def _build_ssh_params(self) -> dict:
        """Monta os parâmetros do túnel conforme o tipo de autenticação."""
        params = {
            "ssh_host": (settings.ssh_host, settings.ssh_port),
            "ssh_username": settings.ssh_user,
            "remote_bind_address": (settings.db_host, settings.db_port),
        }
        if settings.ssh_key_path:
            params["ssh_pkey"] = settings.ssh_key_path
        elif settings.ssh_password:
            params["ssh_password"] = settings.ssh_password
        else:
            raise ValueError("Defina SSH_KEY_PATH ou SSH_PASSWORD no .env")

        return params


    def start_tunnel(self) -> None:
    #     """Abre o túnel SSH e inicializa o engine SQLModel."""
    #     self._server = SSHTunnelForwarder(
    #         (settings.ssh_host, settings.ssh_port),
    #         ssh_username=settings.ssh_user,            # Nome de usuário SSH
    #         ssh_password=settings.ssh_password,              # Senha SSH (ou usar ssh_pkey)
    #         remote_bind_address=(settings.db_host, settings.db_port)  # Serviço remoto (ex: MySQL)
    #         )
    #     self._server.start()
        encoded_password = urllib.parse.quote_plus(settings.db_password) ##necessário para senhas que contenham caracteres especiais
        url = (
            f"mysql+pymysql://{settings.db_user}:{encoded_password}"
            # f"@127.0.0.1:{self._server.local_bind_port}/{settings.db_name}"
            f"@127.0.0.1:{settings.db_port}/{settings.db_name}"
            f"?charset=utf8mb4"
        )

        
        self._engine = create_engine(
            url,                      #url de conexão
            echo=False,               # troque para True só para depurar o SQL
            pool_pre_ping=True,       # valida conexão antes de reutilizar
            pool_recycle=1800,        # recicla conexões a cada 30 min
            pool_size=5,              # numero máximo de conexões simultâneas
        )
        if not self._engine:
            raise ConnectionError("Erro na conexão do banco de dados")
    def stop_tunnel(self) -> None:
        """Fecha o engine e encerra o túnel SSH."""

        if self._engine:
            self._engine.dispose()

        if self._server and self._server.is_active:
            self._server.stop()

    def get_db(self):
        with Session(self._engine) as session:
            yield session



