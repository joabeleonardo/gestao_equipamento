import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Ajuste os imports conforme a estrutura real do seu projeto
from routes.Perfil_UsuarioRoutes import perfil_usuario_router
from entidades.models import PerfilDeUsuario
from dependencies.database import database

# 1. Configuração do App de Teste
app = FastAPI()
app.include_router(perfil_usuario_router)

# 2. Mock da dependência do Banco de Dados
def override_get_db():
    yield MagicMock()

app.dependency_overrides[database.get_db] = override_get_db

client = TestClient(app)

# 3. Dados Mockados
MOCK_PERFIL_PAYLOAD = {
    "acesso_id_usuario": 1,
    "acesso_id_nivel_acesso": 2
}

MOCK_PERFIL_RESPOSTA = PerfilDeUsuario(**MOCK_PERFIL_PAYLOAD)

# ==========================================
# TESTES DA ROTA: POST /usuarios-has-role
# ==========================================
@patch("routes.Perfil_UsuarioRoutes.PerfilUsuarioController.cadastrar_vinculo")
def test_criar_vinculo_sucesso(mock_cadastrar):
    mock_cadastrar.return_value = MOCK_PERFIL_RESPOSTA
    
    response = client.post("/usuarios-has-role", json=MOCK_PERFIL_PAYLOAD)
    
    assert response.status_code == 201
    assert response.json()["acesso_id_usuario"] == 1
    assert response.json()["acesso_id_nivel_acesso"] == 2

@patch("routes.Perfil_UsuarioRoutes.PerfilUsuarioController.cadastrar_vinculo")
def test_criar_vinculo_erro_validacao(mock_cadastrar):
    # Simula erro de usuário/role não encontrado ou vínculo duplicado
    mock_cadastrar.side_effect = ValueError("Usuário informado não está cadastrado no sistema.")
    
    response = client.post("/usuarios-has-role", json=MOCK_PERFIL_PAYLOAD)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Usuário informado não está cadastrado no sistema."

# ==========================================
# TESTES DA ROTA: GET /perfil_usuario
# ==========================================
@patch("routes.Perfil_UsuarioRoutes.PerfilUsuarioController.buscar_vinculos")
def test_listar_vinculos_sucesso(mock_buscar):
    mock_buscar.return_value = [MOCK_PERFIL_RESPOSTA]
    
    response = client.get("/perfil_usuario")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

# ==========================================
# TESTES DA ROTA: GET /perfis_usuario/{id_usuario}/{id_nivel_acesso}
# ==========================================
@patch("routes.Perfil_UsuarioRoutes.PerfilUsuarioController.buscar_vinculo")
def test_buscar_vinculo_especifico_sucesso(mock_buscar_vinculo):
    mock_buscar_vinculo.return_value = MOCK_PERFIL_RESPOSTA
    
    response = client.get("/perfis_usuario/1/2")
    
    assert response.status_code == 200
    assert response.json()["acesso_id_usuario"] == 1

@patch("routes.Perfil_UsuarioRoutes.PerfilUsuarioController.buscar_vinculo")
def test_buscar_vinculo_especifico_nao_encontrado(mock_buscar_vinculo):
    mock_buscar_vinculo.side_effect = KeyError("Vínculo usuário 1 x role 99 não encontrado.")
    
    response = client.get("/perfis_usuario/1/99")
    
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]

# ==========================================
# TESTES DA ROTA: DELETE /perfis_usuario/{id_usuario}/{id_nivel_acesso}
# ==========================================
@patch("routes.Perfil_UsuarioRoutes.PerfilUsuarioController.deletar_vinculo")
def test_deletar_vinculo_sucesso(mock_deletar):
    mock_deletar.return_value = None
    
    response = client.delete("/perfis_usuario/1/2")
    
    assert response.status_code == 204

@patch("routes.Perfil_UsuarioRoutes.PerfilUsuarioController.deletar_vinculo")
def test_deletar_vinculo_nao_encontrado(mock_deletar):
    mock_deletar.side_effect = KeyError("Vínculo usuário 1 x role 99 não encontrado.")
    
    response = client.delete("/perfis_usuario/1/99")
    
    assert response.status_code == 404