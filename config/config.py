from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # SSH
    ssh_host: str
    ssh_port: int = 22
    ssh_user: str
    ssh_key_path: str | None = None
    ssh_password: str | None = None

    # MariaDB
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_name: str
    db_user: str
    db_password: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
#Variável que armazena os valores lidos do arquivo .env
settings = Settings()


# from pydantic_settings import BaseSettings, SettingsConfigDict

# class Settings(BaseSettings):
#     ssh_host: str
#     ssh_port: int = 22
#     ssh_user: str
#     ssh_password: str | None = None

#     #Myslq
#     db_host: str = "127.0.0.1"
#     db_port: int = 3306
#     sb_name: str
#     db_user: str
#     db_password: str

#     model_config = SettingsConfigDict(env_file=".env",env_file_encoding="UTF-8")

# settings = Settings()