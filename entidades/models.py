from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

#Autenticação de usuario
class UsuarioLogin(BaseModel):
    login:str
    senha:str
class UsuarioLogado(BaseModel):
    id:int
    nome:str
    login:str
    #Relacionamento Perfil/acesso <-> Usuário N:N
    perfil:list[str]
    

class UsuarioBase(SQLModel):
    # Dados "públicos" (não inclui senha para não vazar por engano)
    nome : str = Field(min_length=6, max_length=200)
    telefone : str = Field(min_length=11, max_length=20)
    login : str = Field(min_length=10, max_length=255)
     
class Usuario(UsuarioBase,table=True):
    __tablename__="usuario"
    id_usuario : int | None = Field(None,primary_key=True)
    
    senha : str = Field(min_length=8, max_length=255)

    niveis_acesso: list["PerfilDeUsuario"] = Relationship(back_populates="usuario")


    # IMPORTANTE: Emprestimo tem DUAS FKs para Usuario (solicitante e aprovador).
    # Sem o sa_relationship_kwargs apontando qual FK pertence a qual relação,
    # o SQLAlchemy não sabe desambiguar e lança AmbiguousForeignKeysError.
    emprestimos_solicitados: list["Emprestimo"] = Relationship(
        back_populates="solicitante",
        sa_relationship_kwargs={
            "foreign_keys": "[Emprestimo.id_usuario_solicitante]"
        },
    )
    emprestimos_aprovados: list["Emprestimo"] = Relationship(
        back_populates="aprovador",
        sa_relationship_kwargs={
            "foreign_keys": "[Emprestimo.id_usuario_aprovador]"
        },
    )


class UsuarioPublico(UsuarioBase):
    # Schema que a API expõe — sem senha.
    pass




################################################################################################################################
# ============================================================================
# NÍVEL DE ACESSO (Roles)
# ============================================================================
class NivelDeAcessoBase(SQLModel):
    nivel : str = Field(min_length=4, max_length=30)

class NivelDeAcesso(NivelDeAcessoBase,table=True):
    __tablename__="nivel_acesso"    
    id_nivel_acesso : int | None = Field(default=None,primary_key=True)
    

    perfil_usuario: list["PerfilDeUsuario"] = Relationship(back_populates="nivel_acesso")

class NivelDeAcessoPublico(NivelDeAcessoBase):
    pass

# ============================================================================
# USUARIO_HAS_ROLE (associação N:N entre usuario e roles)
# ============================================================================
class PerfilDeUsuarioBase(SQLModel):
    # As duas FKs
    acesso_id_usuario: int = Field(foreign_key="usuario.id_usuario")
    acesso_id_nivel_acesso: int = Field(foreign_key="nivel_acesso.id_nivel_acesso")


class PerfilDeUsuario(PerfilDeUsuarioBase, table=True):
    __tablename__ = "acesso"

    # Chave primária COMPOSTA: o par (usuario_id, role_id) é único.
    # Redeclaramos os campos aqui para marcar primary_key=True nos dois.
    acesso_id_usuario: int = Field(
        foreign_key="usuario.id_usuario", primary_key=True
    )
    acesso_id_nivel_acesso: int = Field(
        foreign_key="nivel_acesso.id_nivel_acesso", primary_key=True
    )

    # Relacionamentos reversos
    usuario: Usuario | None = Relationship(back_populates="niveis_acesso")
    nivel_acesso: NivelDeAcesso | None = Relationship(back_populates="perfil_usuario")


class PerfilDeUsuarioPublico(PerfilDeUsuarioBase):
    pass





################################################################################################################################ 
# ============================================================================
# CATEGORIA DE EQUIPAMENTO
# ----------------------------------------------------------------------------
# Base  -> campos puros (sem tabela) usados para validação de entrada/saída
# Table -> a tabela real do banco (hereda os campos da Base)
# Publico -> o que a API expõe / recebe do cliente
# ============================================================================
class CategoriaEquipamentoBase(SQLModel):
    nome: str = Field(min_length=5,max_length=100)
    
class CategoriaEquipamento(CategoriaEquipamentoBase,table=True):
    __tablename__="categoria_equipamento"
    id_categoria : int | None = Field(None,primary_key=True)
    
    equipamento : list ["Equipamento"] = Relationship(back_populates="categoria_equipamento")

class CategoriaEquipamentoPublico(CategoriaEquipamentoBase):
    # Só herda os campos válidos para o cliente (sem PK).
    # Usado como schema de entrada no POST/PUT e como schema de saída.
    pass

################################################################################################################################
# ============================================================================
# EQUIPAMENTO
# ============================================================================
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

     # Relacionamento 1:N -> um equipamento pode ter vários empréstimos (histórico)
    emprestimos: list["Emprestimo"] = Relationship(back_populates="equipamento")

class EquipamentoPublico(EquipamentoBase):
    pass

################################################################################################################################ 
# ============================================================================
# EMPRESTIMO
# ============================================================================
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
    prazo_devolucao: datetime | None = None
    status_solicitacao: EnumStatusEmprestimo = Field(default=EnumStatusEmprestimo.pendente)

   

class Emprestimo(EmprestimoBase, table=True):
    __tablename__ = "emprestimo"
    id_emprestimo: int | None = Field(default=None, primary_key=True)
    data_solicitacao: datetime = Field(default_factory=datetime.utcnow)
    data_aprovacao: datetime | None = None
    data_devolucao: datetime | None = None

    solicitante: Usuario | None = Relationship(
        back_populates="emprestimos_solicitados",
        sa_relationship_kwargs={
            "foreign_keys": "[Emprestimo.id_usuario_solicitante]"
        },
    )
    aprovador: Usuario | None = Relationship(
        back_populates="emprestimos_aprovados",
        sa_relationship_kwargs={
            "foreign_keys": "[Emprestimo.id_usuario_aprovador]"
        },
    )
    equipamento: Equipamento | None = Relationship(back_populates="emprestimos")



class EmprestimoPublico(EmprestimoBase):
    pass


################################################################################################################################ 




