import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Ajuste os imports conforme a estrutura real do seu projeto
from routes.AuthRoutes import auth_router
from dependencies.database import database

# 1. Configuração do App de Teste
app = FastAPI()
app.include_router(auth_router)

# 2. Mock da dependência do Banco de Dados
def override_get_db():
    yield MagicMock()

app.dependency_overrides[database.get_db] = override_get_db

client = TestClient(app)

# 3. Dados Mockados
MOCK_LOGIN_PAYLOAD = {
    "login": "carlos.almeida",  # Ajuste para a chave esperada pelo seu UsuarioLogin
    "senha": "senhaSegura123"
}

MOCK_TOKEN_RESPOSTA = "eyJhbGciOiJIUzI1NiIsInR5cCI... (token jwt simulado)"

# ==========================================
# TESTES DA ROTA: POST /auth/login
# ==========================================
@patch("routes.AuthRoutes.AuthController.fazer_login")
def test_login_sucesso(mock_fazer_login):
    # Simula a geração e retorno de um token JWT string pelo controlador
    mock_fazer_login.return_value = MOCK_TOKEN_RESPOSTA
    
    response = client.post("/auth/login", json=MOCK_LOGIN_PAYLOAD)
    
    assert response.status_code == 200
    assert response.json() == MOCK_TOKEN_RESPOSTA

@patch("routes.AuthRoutes.AuthController.fazer_login")
def test_login_credenciais_invalidas(mock_fazer_login):
    # Simula o ValueError levantado quando a senha falha no verifica_senha
    mock_fazer_login.side_effect = ValueError("Credenciais inválidas.")
    
    response = client.post("/auth/login", json=MOCK_LOGIN_PAYLOAD)
    
    # O seu AuthRoutes converte ValueError em HTTP 401 Unauthorized
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas."