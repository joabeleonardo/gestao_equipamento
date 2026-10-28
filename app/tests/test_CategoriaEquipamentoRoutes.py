import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# importações do  projeto
from routes.CategoriaEquipamentoRoutes import categoria_equipamento_router
from entidades.models import CategoriaEquipamento
from dependencies.database import database

# Configura o app e rota de teste
app = FastAPI()
app.include_router(categoria_equipamento_router)

# Mock da dependência do Banco de Dados 
# cria uma função falsa que simula uma sessão do banco de dados.
def override_get_db():
    yield MagicMock()

app.dependency_overrides[database.get_db] = override_get_db

#faz chamada simulando rotas
client = TestClient(app)

# Dados Mockados (testados)
MOCK_CATEGORIA_PAYLOAD = {
    "nome": "Projetores"
}

MOCK_CATEGORIA_RESPOSTA = CategoriaEquipamento(
    id_categoria=1,
    **MOCK_CATEGORIA_PAYLOAD
)

# ==========================================
# TESTES DA ROTA: POST /categorias/
# ==========================================
@patch("routes.CategoriaEquipamentoRoutes.CategoriaEquipamentoController.inserir_categoria")
def test_inserir_categoria_sucesso(mock_inserir):
    mock_inserir.return_value = MOCK_CATEGORIA_RESPOSTA
    
    # Como usamos prefix="/categorias" e rota "/" o caminho correto no teste é "/categorias/"
    response = client.post("/categorias/", json=MOCK_CATEGORIA_PAYLOAD)
    
    assert response.status_code == 201
    assert response.json()["nome"] == "Projetores"
    assert "id_categoria" in response.json()

@patch("routes.CategoriaEquipamentoRoutes.CategoriaEquipamentoController.inserir_categoria")
def test_inserir_categoria_erro_integridade(mock_inserir):
    mock_inserir.side_effect = ValueError("Erro de integridade ao inserir categoria.")
    
    response = client.post("/categorias/", json=MOCK_CATEGORIA_PAYLOAD)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Erro de integridade ao inserir categoria."

# ==========================================
# TESTES DA ROTA: GET /categorias/
# ==========================================
@patch("routes.CategoriaEquipamentoRoutes.CategoriaEquipamentoController.buscar_categorias")
def test_listar_categorias_sucesso(mock_buscar):
    mock_buscar.return_value = [MOCK_CATEGORIA_RESPOSTA]
    
    response = client.get("/categorias/")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

# ==========================================
# TESTES DA ROTA: GET /categorias/{id}
# ==========================================
@patch("routes.CategoriaEquipamentoRoutes.CategoriaEquipamentoController.buscar_categoria_por_id")
def test_buscar_categoria_por_id_sucesso(mock_buscar_id):
    mock_buscar_id.return_value = MOCK_CATEGORIA_RESPOSTA
    
    response = client.get("/categorias/1")
    
    assert response.status_code == 200
    assert response.json()["id_categoria"] == 1

@patch("routes.CategoriaEquipamentoRoutes.CategoriaEquipamentoController.buscar_categoria_por_id")
def test_buscar_categoria_por_id_nao_encontrada(mock_buscar_id):
    mock_buscar_id.side_effect = KeyError("Categoria de ID 999 não encontrada.")
    
    response = client.get("/categorias/999")
    
    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"]

# ==========================================
# TESTES DA ROTA: PUT /categorias/{id}
# ==========================================
@patch("routes.CategoriaEquipamentoRoutes.CategoriaEquipamentoController.atualizar_categoria")
def test_atualizar_categoria_sucesso(mock_atualizar):
    mock_atualizar.return_value = MOCK_CATEGORIA_RESPOSTA
    
    response = client.put("/categorias/1", json=MOCK_CATEGORIA_PAYLOAD)
    
    assert response.status_code == 200
    assert response.json()["nome"] == "Projetores"

# ==========================================
# TESTES DA ROTA: DELETE /categorias/{id}
# ==========================================
@patch("routes.CategoriaEquipamentoRoutes.CategoriaEquipamentoController.deletar_categoria")
def test_deletar_categoria_sucesso(mock_deletar):
    mock_deletar.return_value = None 
    
    response = client.delete("/categorias/1")
    
    assert response.status_code == 204 

@patch("routes.CategoriaEquipamentoRoutes.CategoriaEquipamentoController.deletar_categoria")
def test_deletar_categoria_nao_encontrada(mock_deletar):
    mock_deletar.side_effect = KeyError("Categoria de ID 999 não encontrada.")
    
    response = client.delete("/categorias/999")
    
    assert response.status_code == 404