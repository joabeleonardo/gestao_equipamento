from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.CategoriaEquipamentoRoutes import categoria_equipamento_router
from routes.EquipamentoRoutes import equipamento_router
from routes.NivelDeAcessoRoutes import nivel_acesso_router
from routes.UsuarioRoutes import usuario_router
from routes.AuthRoutes import auth_router
from routes.EmprestimoRoutes import emprestimo_router
from routes.Perfil_UsuarioRoutes import perfil_usuario_router

from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Primeira API de Joabe_Leonardo",
    description="primeira API desenvolvida por Jobs",
    version="0.0.1"
)


# CORS: permite que o front-end (index.html aberto no navegador) chame a API.
# A autenticação é por token no cabeçalho (sem cookies), então "*" funciona.
# Em produção, troque "*" pelo endereço real do front-end.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nivel_acesso_router)
app.include_router(usuario_router)
app.include_router(categoria_equipamento_router)
app.include_router(equipamento_router)
app.include_router(auth_router)
app.include_router(emprestimo_router)
app.include_router(perfil_usuario_router)


# Caminho para o frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" 

@app.get("/", include_in_schema=False)
def pagina_inicial():
    return FileResponse(FRONTEND_DIR / "index.html")

app.mount(
    "/css",
    StaticFiles(directory=FRONTEND_DIR / "css"),
    name="css",
)

app.mount(
    "/js",
    StaticFiles(directory=FRONTEND_DIR / "js"),
    name="js",
)



@app.get("/{pagina:path}", include_in_schema=False)
def servir_pagina(pagina: str):
    # Permite servir páginas HTML existentes no frontend
    arquivo = (FRONTEND_DIR / pagina).resolve()

    # Impede acesso a arquivos fora da pasta frontend
    if FRONTEND_DIR.resolve() not in arquivo.parents:
        raise HTTPException(status_code=404, detail="Página não encontrada")

    if not arquivo.is_file() or arquivo.suffix.lower() != ".html":
        raise HTTPException(status_code=404, detail="Página não encontrada")

    return FileResponse(arquivo)
