from fastapi import FastAPI, Depends, HTTPException, status
from config.config import Settings
from routes.CategoriaEquipamentoRoutes import categoria_equipamento_router
from routes.EquipamentoRoutes import equipamento_router
from routes.NivelDeAcessoRoutes import nivel_de_acesso_router
from routes.UsuarioRoutes import usuario_router


app = FastAPI(
    title= "Primeira API de Joabe_Leonardo",
    description="primeira API desenvolvida por Jobs",
    version="0.0.1"
    )

#ROTA PARA NIVEL DE ACESSO
app.include_router(nivel_de_acesso_router)

#ROTA PARA USUARIO
app.include_router(usuario_router)

# rota para  categoria equipamento
app.include_router(categoria_equipamento_router)

 #inclui rota equipamento
app.include_router(equipamento_router)



@app.get("/config")
def config():
    return Settings


