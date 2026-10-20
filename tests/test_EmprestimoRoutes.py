import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


from routes.EmprestimoRoutes import emprestimo_router
from entidades.models import Emprestimo, EnumStatusEmprestimo
from dependencies.database import database
from dependencies.auth_utils import oauth2_scheme



app = FastAPI()
app.include_router(emprestimo_router)

# Mock da dependência do Banco de Dados 
# cria uma função falsa que simula uma sessão do banco de dados.
def override_get_db():
    yield MagicMock()

app.dependency_overrides[database.get_db] = override_get_db
app.dependency_overrides[oauth2_scheme] = lambda: "token-de-mentira"

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
@patch("dependencies.auth_utils.validar_token")
@patch("routes.EmprestimoRoutes.EmprestimoController.cadastrar_emprestimo")
def test_criar_emprestimo_sucesso(mock_cadastrar,mock_validar_token):
    mock_validar_token.return_value = {"sub": "1","roles": ["Solicitante"]}

    mock_cadastrar.return_value = MOCK_EMPRESTIMO_RESPOSTA

    response = client.post("/emprestimos",json=MOCK_EMPRESTIMO_PAYLOAD)

    assert response.status_code == 201
    assert response.json()["status_solicitacao"] == "pendente"


@patch("dependencies.auth_utils.validar_token")
@patch("routes.EmprestimoRoutes.EmprestimoController.cadastrar_emprestimo")
def test_criar_emprestimo_erro_validacao(mock_cadastrar, mock_validar_token):
    mock_validar_token.return_value = {"sub": "1","roles": ["Solicitante"]}

    mock_cadastrar.side_effect = ValueError("O equipamento informado não existe.")

    response = client.post("/emprestimos",json=MOCK_EMPRESTIMO_PAYLOAD)

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

@patch("dependencies.auth_utils.validar_token")
@patch("routes.EmprestimoRoutes.EmprestimoController.atualizar_emprestimo")
def test_atualizar_emprestimo_sucesso_gestor(mock_atualizar, mock_validar_token):
    # Simula que o usuário logado tem o papel "Gestor"
    mock_validar_token.return_value = {"sub": 2, "roles": ["Gestor"]}
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


#==================================
#TESTE DE VALIDAÇÃO DE USUARIOS
#==================================
@patch("dependencies.auth_utils.validar_token")
@patch("routes.EmprestimoRoutes.EmprestimoController.cadastrar_emprestimo")
def test_criar_emprestimo_sucesso_usuario_comum(mock_cadastrar, mock_validar_token):
    # Simula que o usuário logado tem o papel "Comum"
    mock_validar_token.return_value = {"sub": 1, "roles": ["Solicitante"]}
    mock_cadastrar.return_value = MOCK_EMPRESTIMO_RESPOSTA
    
    response = client.post("/emprestimos", json=MOCK_EMPRESTIMO_PAYLOAD)
    
    assert response.status_code == 201
    assert response.json()["id_emprestimo"] == 1

@patch("dependencies.auth_utils.validar_token")
def test_criar_emprestimo_acesso_negado_para_gestor(mock_validar_token):
    # Simula um Gestor tentando criar uma solicitação (ação restrita a Comum)
    mock_validar_token.return_value = {"sub": 2, "roles": ["Gestor"]}
    
    response = client.post("/emprestimos", json=MOCK_EMPRESTIMO_PAYLOAD)
    
    # O RoleChecker deve interceptar e retornar 403 Forbidden
    assert response.status_code == 403
    assert "Acesso negado" in response.json()["detail"]

# ==========================================
# TESTES DA ROTA: PUT /emprestimos/{id} (Aprovação/Devolução - Exige "Gestor")
# ==========================================
@patch("dependencies.auth_utils.validar_token")
@patch("routes.EmprestimoRoutes.EmprestimoController.atualizar_emprestimo")
def test_atualizar_emprestimo_sucesso_gestor(mock_atualizar, mock_validar_token):
    # Simula que o usuário logado tem o papel "Gestor"
    mock_validar_token.return_value = {"sub": 2, "roles": ["Gestor"]}
    mock_atualizar.return_value = MOCK_EMPRESTIMO_RESPOSTA
    
    response = client.put("/emprestimos/1", json=MOCK_EMPRESTIMO_PAYLOAD)
    
    assert response.status_code == 200
    assert response.json()["id_emprestimo"] == 1

@patch("dependencies.auth_utils.validar_token")
def test_atualizar_emprestimo_acesso_negado_usuario_comum(mock_validar_token):
    # Simula um Usuário Comum tentando aprovar um empréstimo (ação restrita a Gestor)
    mock_validar_token.return_value = {"sub": 1, "roles": ["Comum"]}
    
    response = client.put("/emprestimos/1", json=MOCK_EMPRESTIMO_PAYLOAD)
    
    # O RoleChecker deve interceptar e retornar 403 Forbidden
    assert response.status_code == 403
    assert "Acesso negado" in response.json()["detail"]

# ==========================================
# TESTES DA ROTA: GET /emprestimos (Listagem - Acesso liberado para exemplo)
# ==========================================
@patch("dependencies.auth_utils.validar_token")
@patch("routes.EmprestimoRoutes.EmprestimoController.buscar_emprestimos")
def test_listar_emprestimos_sucesso(mock_buscar, mock_validar_token):
    mock_validar_token.return_value = {"sub": 1, "roles": ["Solicitante"]}
    mock_buscar.return_value = [MOCK_EMPRESTIMO_RESPOSTA]
    
    response = client.get("/emprestimos")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)