import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Importações do seu projeto
from routes.NivelDeAcessoRoutes import nivel_acesso_router
from entidades.models import NivelDeAcesso
from dependencies.database import database
from dependencies.auth_utils import oauth2_scheme

# 1. Configuração do App de Teste
app = FastAPI()
app.include_router(nivel_acesso_router)

# 2. Mock da dependência do Banco de Dados
def override_get_db():
    yield MagicMock()
    
app.dependency_overrides[database.get_db] = override_get_db
app.dependency_overrides[oauth2_scheme] = lambda: "token-de-mentira"

client = TestClient(app)

# 3. Dados Mockados
MOCK_NIVEL_PAYLOAD = {"nivel": "Administrador",}


MOCK_NIVEL_RESPOSTA = NivelDeAcesso(id_nivel_acesso=1,**MOCK_NIVEL_PAYLOAD)



# ==========================================
# TESTES DA ROTA: POST /niveis-acesso/
# ==========================================
@patch("dependencies.auth_utils.validar_token")
@patch("routes.NivelDeAcessoRoutes.NivelDeAcessoController.inserir_nivel_acesso")
def test_inserir_nivel_acesso_sucesso(mock_inserir, mock_validar_token):

    mock_validar_token.return_value = {"sub": "1","roles": ["Administrador"]}
    
    mock_inserir.return_value = MOCK_NIVEL_RESPOSTA
    
    # Como da definição prefix="/niveis-acesso" e rota "/", o acesso será feito "/niveis-acesso/"
    response = client.post("/niveis-acesso/", json=MOCK_NIVEL_PAYLOAD)
    
    assert response.status_code == 201
    assert response.json()["nivel"] == "Administrador"
    assert "id_nivel_acesso" in response.json()

@patch("dependencies.auth_utils.validar_token")
@patch("routes.NivelDeAcessoRoutes.NivelDeAcessoController.inserir_nivel_acesso")
def test_inserir_nivel_acesso_erro_integridade(mock_inserir,mock_validar_token):
    mock_validar_token.return_value = {"sub": "1","roles": ["Administrador"]}

    mock_inserir.side_effect = ValueError("Erro de integridade. Verifique se este nível já existe.")
    
    response = client.post("/niveis-acesso/", json=MOCK_NIVEL_PAYLOAD)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Erro de integridade. Verifique se este nível já existe."

# ==========================================
# TESTES DA ROTA: GET /niveis-acesso/
# ==========================================
@patch("dependencies.auth_utils.validar_token")
@patch("routes.NivelDeAcessoRoutes.NivelDeAcessoController.buscar_niveis_acesso")
def test_listar_niveis_acesso_sucesso(mock_buscar,mock_validar_token):

    mock_validar_token.return_value = {"sub": "1","roles": ["Administrador"]}

    mock_buscar.return_value = [MOCK_NIVEL_RESPOSTA]
    
    response = client.get("/niveis-acesso/")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

# ==========================================
# TESTES DA ROTA: GET /niveis-acesso/{id}
# ==========================================
@patch("dependencies.auth_utils.validar_token")
@patch("routes.NivelDeAcessoRoutes.NivelDeAcessoController.buscar_nivel_acesso_por_id")
def test_buscar_nivel_acesso_por_id_sucesso(mock_buscar_id, mock_validar_token):

    mock_validar_token.return_value = {"sub": "1","roles": ["Administrador"]}

    mock_buscar_id.return_value = MOCK_NIVEL_RESPOSTA
    
    response = client.get("/niveis-acesso/1")
    
    assert response.status_code == 200
    assert response.json()["id_nivel_acesso"] == 1

@patch("dependencies.auth_utils.validar_token")
@patch("routes.NivelDeAcessoRoutes.NivelDeAcessoController.buscar_nivel_acesso_por_id")
def test_buscar_nivel_acesso_por_id_nao_encontrado(mock_buscar_id, mock_validar_token):
    
    mock_validar_token.return_value = {"sub": "1","roles": ["Administrador"]}
    mock_buscar_id.side_effect = KeyError("Nível de acesso de ID 999 não encontrado.")
    
    response = client.get("/niveis-acesso/999")
    
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]

# ==========================================
# TESTES DA ROTA: PUT /niveis-acesso/{id}
# ==========================================
@patch("dependencies.auth_utils.validar_token")
@patch("routes.NivelDeAcessoRoutes.NivelDeAcessoController.atualizar_nivel_acesso")
def test_atualizar_nivel_acesso_sucesso(mock_atualizar, mock_validar_token):

    mock_validar_token.return_value = {"sub": "1","roles": ["Administrador"]}

    mock_atualizar.return_value = MOCK_NIVEL_RESPOSTA
    
    response = client.put("/niveis-acesso/1", json=MOCK_NIVEL_PAYLOAD)
    
    assert response.status_code == 200
    assert response.json()["nivel"] == "Administrador"

# ==========================================
# TESTES DA ROTA: DELETE /niveis-acesso/{id}
# ==========================================
@patch("dependencies.auth_utils.validar_token")
@patch("routes.NivelDeAcessoRoutes.NivelDeAcessoController.deletar_nivel_acesso")
def test_deletar_nivel_acesso_sucesso(mock_deletar, mock_validar_token):

    mock_validar_token.return_value = {"sub": "1","roles": ["Administrador"]}
    mock_deletar.return_value = None 
    
    response = client.delete("/niveis-acesso/1")
    
    assert response.status_code == 204 

@patch("dependencies.auth_utils.validar_token")
@patch("routes.NivelDeAcessoRoutes.NivelDeAcessoController.deletar_nivel_acesso")
def test_deletar_nivel_acesso_nao_encontrado(mock_deletar, mock_validar_token):

    mock_validar_token.return_value = {"sub": "1","roles": ["Administrador"]}
    mock_deletar.side_effect = KeyError("Nível de acesso de ID 999 não encontrado.")
    
    response = client.delete("/niveis-acesso/999")
    
    assert response.status_code == 404