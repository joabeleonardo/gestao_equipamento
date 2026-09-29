import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# verifica se os caminhos de importação estão corretos
from routes.EquipamentoRoutes import equipamento_router
from entidades.models import Equipamento, EnumEquipamento
from dependencies.database import database

# Configuração do App de Teste
app = FastAPI()
app.include_router(equipamento_router)

# Mock da dependência do Banco de Dados 
# cria uma função falsa que simula uma sessão do banco de dados.
def override_get_db():
    yield MagicMock()

app.dependency_overrides[database.get_db] = override_get_db

client = TestClient(app)

#Dados Mockados para os testes

MOCK_EQUIPAMENTO_PAYLOAD = {
    "patrimonio": "PTR-1001",
    "nome": "Projetor Epson",
    "modelo": "PowerLite",
    "marca": "Epson",
    "status_equipamento": EnumEquipamento.disponivel,
    "id_categoria": 1
}

MOCK_EQUIPAMENTO_RESPOSTA = Equipamento(
    id_equipamento=1,
    **MOCK_EQUIPAMENTO_PAYLOAD
)

# ==========================================
# TESTES DA ROTA: POST /equipamentos
# ==========================================
@patch("routes.EquipamentoRoutes.EquipamentoController.cadastrar_equipamento")
def test_cadastro_equipamento_sucesso(mock_cadastrar):
    # Simula o retorno de sucesso do controller
    mock_cadastrar.return_value = MOCK_EQUIPAMENTO_RESPOSTA
    
    response = client.post("/equipamentos", json=MOCK_EQUIPAMENTO_PAYLOAD)
    
    assert response.status_code == 201
    assert response.json()["patrimonio"] == "PTR-1001"
    assert "id_equipamento" in response.json()

@patch("routes.EquipamentoRoutes.EquipamentoController.cadastrar_equipamento")
def test_cadastro_equipamento_erro_categoria_inexistente(mock_cadastrar):
    # Simula o erro ValueError no controller
    mock_cadastrar.side_effect = ValueError("A CATEGORIA INFORMADA NÃO EXISTE.")
    
    response = client.post("/equipamentos", json=MOCK_EQUIPAMENTO_PAYLOAD)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "A CATEGORIA INFORMADA NÃO EXISTE."

# ==========================================
# TESTES DA ROTA: GET /equipamentos
# ==========================================
@patch("routes.EquipamentoRoutes.EquipamentoController.buscar_equipamento")
def test_buscar_todos_equipamentos_sucesso(mock_buscar):
    mock_buscar.return_value = [MOCK_EQUIPAMENTO_RESPOSTA]
    
    response = client.get("/equipamentos")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

# ==========================================
# TESTES DA ROTA: GET /equipamentos/{id}
# ==========================================
@patch("routes.EquipamentoRoutes.EquipamentoController.buscar_equipamento_por_id")
def test_buscar_equipamento_por_id_sucesso(mock_buscar_id):
    mock_buscar_id.return_value = MOCK_EQUIPAMENTO_RESPOSTA
    
    response = client.get("/equipamentos/1")
    
    assert response.status_code == 200
    assert response.json()["id_equipamento"] == 1

@patch("routes.EquipamentoRoutes.EquipamentoController.buscar_equipamento_por_id")
def test_buscar_equipamento_por_id_nao_encontrado(mock_buscar_id):
    mock_buscar_id.side_effect = KeyError("Equipamento de ID 999 não encontrado.")
    
    response = client.get("/equipamentos/999")
    
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]

# ==========================================
# TESTES DA ROTA: PUT /equipamentos/{id}
# ==========================================
@patch("routes.EquipamentoRoutes.EquipamentoController.atualizar_equipamento")
def test_atualizar_equipamento_sucesso(mock_atualizar):
    mock_atualizar.return_value = MOCK_EQUIPAMENTO_RESPOSTA
    
  
    response = client.put("/equipamentos/1", json=MOCK_EQUIPAMENTO_PAYLOAD)
    
    assert response.status_code == 200
    assert response.json()["nome"] == "Projetor Epson"

# ==========================================
# TESTES DA ROTA: DELETE /equipamentos/{id}
# ==========================================
@patch("routes.EquipamentoRoutes.EquipamentoController.deletar_equipamento")
def test_deletar_equipamento_sucesso(mock_deletar):
    mock_deletar.return_value = None # Deletar não retorna nada
    
    response = client.delete("/equipamentos/1")
    
    assert response.status_code == 204 

@patch("routes.EquipamentoRoutes.EquipamentoController.deletar_equipamento")
def test_deletar_equipamento_nao_encontrado(mock_deletar):
    mock_deletar.side_effect = KeyError("Equipamento de ID 999 não encontrado.")
    
    response = client.delete("/equipamentos/999")
    
    assert response.status_code == 404