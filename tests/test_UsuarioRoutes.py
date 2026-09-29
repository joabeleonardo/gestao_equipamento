import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from routes.UsuarioRoutes import usuario_router
from entidades.models import Usuario
from dependencies.database import database

# 1. Configuração do App de Teste
app = FastAPI()
app.include_router(usuario_router)


def override_get_db():
    yield MagicMock()

app.dependency_overrides[database.get_db] = override_get_db

client = TestClient(app)


MOCK_USUARIO_PAYLOAD = {
    "nome": "Carlos Almeida",
    "telefone": "11988887777",
    "login": "carlos.almeida",
    "senha": "senhaSegura123"
}

MOCK_USUARIO_RESPOSTA = Usuario(
    id_usuario=3,
    **MOCK_USUARIO_PAYLOAD
)

# ==========================================
# TESTES DA ROTA: POST /usuarios
# ==========================================
@patch("routes.UsuarioRoutes.UsuarioController.cadastrar_usuario")
def test_cadastro_usuario_sucesso(mock_cadastrar):
    mock_cadastrar.return_value = MOCK_USUARIO_RESPOSTA
    
    
    response = client.post("/usuario", json=MOCK_USUARIO_PAYLOAD)
    
    assert response.status_code == 201
    assert response.json()["nome"] == "Carlos Almeida"
    assert "id_usuario" in response.json()

@patch("routes.UsuarioRoutes.UsuarioController.cadastrar_usuario")
def test_cadastro_usuario_erro_integridade(mock_cadastrar):
    mock_cadastrar.side_effect = ValueError("Usuario indisponivel")
    
    
    response = client.post("/usuario", json=MOCK_USUARIO_PAYLOAD)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Usuario indisponivel"

# ==========================================
# TESTES DA ROTA: GET /usuarios
# ==========================================
@patch("routes.UsuarioRoutes.UsuarioController.buscar_usuario")
def test_buscar_todos_usuarios_sucesso(mock_buscar):
    mock_buscar.return_value = [MOCK_USUARIO_RESPOSTA]
    
    # ALTERADO: Removida a barra final
    response = client.get("/usuarios")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

# ==========================================
# TESTES DA ROTA: GET /usuarios/{id}
# ==========================================
@patch("routes.UsuarioRoutes.UsuarioController.buscar_usuario_por_id")
def test_buscar_usuario_por_id_sucesso(mock_buscar_id):
    mock_buscar_id.return_value = MOCK_USUARIO_RESPOSTA
    
    response = client.get("/usuario/3")
    
    assert response.status_code == 200
    assert response.json()["id_usuario"] == 3

@patch("routes.UsuarioRoutes.UsuarioController.buscar_usuario_por_id")
def test_buscar_usuario_por_id_nao_encontrado(mock_buscar_id):
    mock_buscar_id.side_effect = KeyError("Usuário de ID 999 não encontrado.")
    
    response = client.get("/usuario/999")
    
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]

# ==========================================
# TESTES DA ROTA: PUT /usuarios/{id}
# ==========================================
@patch("routes.UsuarioRoutes.UsuarioController.atualizar_usuario")
def test_atualizar_usuario_sucesso(mock_atualizar):
    mock_atualizar.return_value = MOCK_USUARIO_RESPOSTA
    
    response = client.put("/usuario/3", json=MOCK_USUARIO_PAYLOAD)
    
    assert response.status_code == 200
    assert response.json()["login"] == "carlos.almeida"

# ==========================================
# TESTES DA ROTA: DELETE /usuarios/{id}
# ==========================================
@patch("routes.UsuarioRoutes.UsuarioController.deletar_usuario")
def test_deletar_usuario_sucesso(mock_deletar):
    mock_deletar.return_value = None 
    
    response = client.delete("/usuario/3")
    
    assert response.status_code == 204 

@patch("routes.UsuarioRoutes.UsuarioController.deletar_usuario")
def test_deletar_usuario_nao_encontrado(mock_deletar):
    mock_deletar.side_effect = KeyError("Usuário de ID 999 não encontrado.")
    
    response = client.delete("/usuarios/999")
    
    assert response.status_code == 404