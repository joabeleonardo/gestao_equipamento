from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from dependencies.database import database
from entidades.models import Equipamento, EquipamentoPublico
from controllers import EquipamentoController   


equipamento_router = APIRouter()


@equipamento_router.post("/equipamentos", response_model=Equipamento,status_code=status.HTTP_201_CREATED)
def cadastro_equipamento(dados : EquipamentoPublico, db:Session = Depends(database.get_db)):
    try: 
        return EquipamentoController.cadastrar_equipamento(db, dados)

    except ValueError as e: 
         # Retorna HTTP 400 (Bad Request) se a categoria não existir ou houver conflito de dados
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(e))

    except RuntimeError as e:
         #  HTTP 500 (Internal Server Error - erro interno) se o banco estiver inacessível
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@equipamento_router.get("/equipamentos", status_code=status.HTTP_200_OK)
def buscar_equipamento(db: Session = Depends(database.get_db)):
    try:
        equipamentos = EquipamentoController.buscar_equipamento(db)
        return equipamentos
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

#rota para buscar um único equipamento pelo ID
@equipamento_router.get("/equipamentos/{id_equipamento}", response_model=Equipamento, status_code=status.HTTP_200_OK)
def buscar_equipamento_por_id(id_equipamento: int, db: Session = Depends(database.get_db)):
    try:
        return EquipamentoController.buscar_equipamento_por_id(db, id_equipamento)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@equipamento_router.put("/equipamentos/{id_equipamento}", response_model=Equipamento)
def atualizar_equipamento(id_equipamento: int, dados: Equipamento, db: Session = Depends(database.get_db)):
    try:
        return EquipamentoController.atualizar_equipamento(db, id_equipamento, dados)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@equipamento_router.delete("/equipamentos/{id_equipamento}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_equipamento(id_equipamento: int, db: Session = Depends(database.get_db)):
    try:
        EquipamentoController.deletar_equipamento(db, id_equipamento)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


