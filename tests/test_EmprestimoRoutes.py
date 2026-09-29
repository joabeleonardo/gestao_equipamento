import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


from routes.EmprestimoRoutes import emprestimo_router
from entidades.models import Emprestimo, EnumStatusEmprestimo
from dependencies.database import database


app = FastAPI()
app.include_router(emprestimo_router)

# Mock da dependência do Banco de Dados 
# cria uma função falsa que simula uma sessão do banco de dados.
def override_get_db():
    yield MagicMock()

app.dependency_overrides[database.get_db] = override_get_db

client = TestClient(app)

MOCK_EMPRESTIMO_PAYLOAD = {
    "id_equipamento": 1,
    "id_usuario_solicitante": 1,
    "prazo_devolucao": "2026-12-31",
    "status_solicitacao": EnumStatusEmprestimo.pendente
}

MOCK_EMPRESTIMO_RESPOSTA = Emprestimo(
    id_emprestimo=1,
    **MOCK_EMPRESTIMO_PAYLOAD
)


# TESTE DA ROTA: POST /emprestimos

@patch("routes.EmprestimoRoutes.EmprestimoController.cadastrar_emprestimo")
def test_criar_emprestimo_sucesso(mock_cadastrar):
    mock_cadastrar.return_value = MOCK_EMPRESTIMO_RESPOSTA
    
    response = client.post("/emprestimos", json=MOCK_EMPRESTIMO_PAYLOAD)
    
    assert response.status_code == 201
    assert response.json()["id_emprestimo"] == 1
    assert response.json()["status_solicitacao"] == "pendente"

@patch("routes.EmprestimoRoutes.EmprestimoController.cadastrar_emprestimo")
def test_criar_emprestimo_erro_validacao(mock_cadastrar):
    mock_cadastrar.side_effect = ValueError("O equipamento informado não existe.")
    
    response = client.post("/emprestimos", json=MOCK_EMPRESTIMO_PAYLOAD)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "O equipamento informado não existe."


# TESTES DA ROTA: GET /emprestimos

@patch("routes.EmprestimoRoutes.EmprestimoController.buscar_emprestimos")
def test_listar_emprestimos_sucesso(mock_buscar):
    mock_buscar.return_value = [MOCK_EMPRESTIMO_RESPOSTA]
    
    response = client.get("/emprestimos")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


# TESTES DA ROTA: GET /emprestimos/{id}

@patch("routes.EmprestimoRoutes.EmprestimoController.buscar_emprestimo_por_id")
def test_buscar_emprestimo_por_id_sucesso(mock_buscar_id):
    mock_buscar_id.return_value = MOCK_EMPRESTIMO_RESPOSTA
    
    response = client.get("/emprestimos/1")
    
    assert response.status_code == 200
    assert response.json()["id_emprestimo"] == 1

@patch("routes.EmprestimoRoutes.EmprestimoController.buscar_emprestimo_por_id")
def test_buscar_emprestimo_por_id_nao_encontrado(mock_buscar_id):
    mock_buscar_id.side_effect = KeyError("Empréstimo de ID 999 não encontrado.")
    
    response = client.get("/emprestimos/999")
    
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]


# TESTES DA ROTA: PUT /emprestimos/{id}

@patch("routes.EmprestimoRoutes.EmprestimoController.atualizar_emprestimo")
def test_atualizar_emprestimo_sucesso(mock_atualizar):
    mock_atualizar.return_value = MOCK_EMPRESTIMO_RESPOSTA
    
    response = client.put("/emprestimos/1", json=MOCK_EMPRESTIMO_PAYLOAD)
    
    assert response.status_code == 200
    assert response.json()["id_emprestimo"] == 1


# TESTES DA ROTA: DELETE /emprestimos/{id}

@patch("routes.EmprestimoRoutes.EmprestimoController.deletar_emprestimo")
def test_deletar_emprestimo_sucesso(mock_deletar):
    mock_deletar.return_value = None 
    
    response = client.delete("/emprestimos/1")
    
    assert response.status_code == 204

@patch("routes.EmprestimoRoutes.EmprestimoController.deletar_emprestimo")
def test_deletar_emprestimo_nao_encontrado(mock_deletar):
    mock_deletar.side_effect = KeyError("Empréstimo de ID 999 não encontrado.")
    
    response = client.delete("/emprestimos/999")
    
    assert response.status_code == 404