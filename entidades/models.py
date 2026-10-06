from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr



class Usuario(SQLModel,table=True):
    __tablename__="usuario"
    id_usuario : int | None = Field(None,primary_key=True)
    nome : str = Field(min_length=6, max_length=200)
    telefone : str = Field(min_length=11, max_length=20)
    login : str = Field(min_length=10, max_length=255)
    senha : str = Field(min_length=8, max_length=255)

################################################################################################################################

class NivelDeAcesso(SQLModel,table=True):
    __tablename__="nivel_acesso"    
    id_nivel_acesso : int | None = Field(None,primary_key=True)
    nivel : str = Field(min_length=4, max_length=30)


################################################################################################################################ 

class CategoriaEquipamento(SQLModel,table=True):
    __tablename__="categoria_equipamento"
    id_categoria : int | None = Field(None,primary_key=True)
    nome: str = Field(min_length=5,max_length=100)
    equipamento : list ["Equipamento"] = Relationship(back_populates="categoria_equipamento")

################################################################################################################################

class EnumEquipamento(str,Enum):
    disponivel="disponivel"
    emprestado="emprestado"
    manutencao="manutencao"
    baixado="baixado"

class EquipamentoBase(SQLModel):
    patrimonio : str = Field(min_length=4, max_length=100)
    nome : str = Field(min_length=4, max_length=100)
    modelo: str = Field(min_length=5, max_length=100)
    marca: str = Field(min_length=2, max_length=100)
    status_equipamento : EnumEquipamento = Field(default=EnumEquipamento.disponivel)
    id_categoria : int = Field(foreign_key="categoria_equipamento.id_categoria")

    
class Equipamento(EquipamentoBase,table=True):
    __tablename__="equipamento"
    id_equipamento : int | None = Field(default=None, primary_key=True)
    categoria_equipamento : CategoriaEquipamento | None = Relationship(back_populates="equipamento")

class EquipamentoPublico(EquipamentoBase):
    pass

################################################################################################################################ 

class EnumStatusEmprestimo(str, Enum):
    pendente = "pendente"
    aprovada = "aprovada"
    negada = "negada"
    devolvido = "devolvido"
    atrasada = "atrasada"

class EmprestimoBase(SQLModel):
    id_equipamento: int = Field(foreign_key="equipamento.id_equipamento")
    id_usuario_solicitante: int = Field(foreign_key="usuario.id_usuario")
    id_usuario_aprovador: Optional[int] = Field(default=None, foreign_key="usuario.id_usuario")
    prazo_devolucao: date
    status_solicitacao: EnumStatusEmprestimo = Field(default=EnumStatusEmprestimo.pendente)

class Emprestimo(EmprestimoBase, table=True):
    __tablename__ = "emprestimo"
    id_emprestimo: int | None = Field(default=None, primary_key=True)
    data_solicitacao: Optional[datetime] = Field(default=None)
    data_aprovacao: Optional[datetime] = Field(default=None)
    data_devolucao: Optional[datetime] = Field(default=None)

class EmprestimoPublico(EmprestimoBase):
    pass


################################################################################################################################ 
# autenticação de usuario
class UsuarioLogin(BaseModel):
    usuario: EmailStr
    senha: str

class UsuarioLogado(BaseModel):
    id: int
    nome: str
    roles:list[str]

