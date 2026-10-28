"""
Prepara o SEU banco para testar o sistema. Rode dentro da pasta app/:

    python preparar_banco.py              -> tabelas + perfis + primeiro administrador
    python preparar_banco.py --exemplos   -> o mesmo + categorias, equipamentos e usuários de teste

Para descobrir por que o login não funciona (mostra tabelas, colunas e senhas, sem expor senha nenhuma):
    python preparar_banco.py --diagnosticar

Para usuários que JÁ existem no banco:
    python preparar_banco.py --migrar-senhas           -> criptografa as senhas que estão em texto puro (a mesma senha continua valendo)
    python preparar_banco.py --redefinir-senha LOGIN   -> grava uma senha nova, criptografada (corrige "Credenciais inválidas")
    python preparar_banco.py --vincular LOGIN PERFIL   -> dá um perfil ao usuário (Solicitante, Gestor ou Administrador)

Pode rodar mais de uma vez: só cria o que ainda não existe e nunca apaga dados.
"""
import sys
import getpass
from sqlmodel import SQLModel, Session, select

from dependencies.database import database
from entidades.models import (Usuario, NivelDeAcesso, PerfilDeUsuario,
                              CategoriaEquipamento, Equipamento)
from core.security import criptografar_senha

NIVEIS = ["Solicitante", "Gestor", "Administrador"]


def perguntar(texto, padrao=None, minimo=1, segredo=False):
    while True:
        dica = f" [{padrao}]" if padrao else ""
        valor = (getpass.getpass if segredo else input)(f"{texto}{dica}: ").strip() or (padrao or "")
        if len(valor) >= minimo:
            return valor
        print(f"  Informe pelo menos {minimo} caracteres.")


def garantir_usuario(db, nome, telefone, login, senha, nivel):
    """Cria o usuário (se o login não existir) e garante o vínculo com o perfil."""
    usuario = db.exec(select(Usuario).where(Usuario.login == login)).first()
    if not usuario:
        usuario = Usuario(nome=nome, telefone=telefone, login=login, senha=criptografar_senha(senha))
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        print(f"  usuário criado: {login}")
    perfil = db.exec(select(NivelDeAcesso).where(NivelDeAcesso.nivel == nivel)).one()
    if not db.get(PerfilDeUsuario, (usuario.id_usuario, perfil.id_nivel_acesso)):
        db.add(PerfilDeUsuario(acesso_id_usuario=usuario.id_usuario, acesso_id_nivel_acesso=perfil.id_nivel_acesso))
        db.commit()
        print(f"  perfil {nivel} vinculado a {login}")


def diagnosticar(engine):
    from sqlalchemy import inspect
    print(f"Banco: {engine.url.database}")
    insp = inspect(engine)
    existentes = set(insp.get_table_names())
    problemas = 0
    print("\n1) Tabelas e colunas (o que o código espera x o que existe no banco):")
    for tabela in SQLModel.metadata.sorted_tables:
        if tabela.name not in existentes:
            print(f"  [FALTA]  a tabela '{tabela.name}' não existe"); problemas += 1; continue
        colunas = {c["name"] for c in insp.get_columns(tabela.name)}
        faltam = [c.name for c in tabela.columns if c.name not in colunas]
        if faltam:
            print(f"  [DIFERE] '{tabela.name}': o código espera as colunas {faltam}; no banco existem {sorted(colunas)}"); problemas += 1
        else:
            print(f"  [OK]     '{tabela.name}'")
    print("\n2) Usuários e senhas (a senha nunca é mostrada):")
    try:
        with Session(engine) as db:
            usuarios = db.exec(select(Usuario)).all()
            if not usuarios:
                print("  nenhum usuário cadastrado")
            for u in usuarios:
                s = u.senha or ""
                tipo = ("OK (argon2)" if s.startswith("$argon2") else
                        "hash de OUTRO tipo: não funciona, use --redefinir-senha" if s.startswith("$") else
                        "TEXTO PURO: não funciona, use --migrar-senhas ou --redefinir-senha")
                print(f"  {u.login}: senha {tipo}")
                if not s.startswith("$argon2"): problemas += 1
            print("\n3) Perfis cadastrados (o código exige exatamente estes nomes):")
            nomes = [n.nivel for n in db.exec(select(NivelDeAcesso)).all()]
            print(f"  encontrados: {nomes or 'nenhum'}")
            for esperado in NIVEIS:
                if esperado not in nomes:
                    print(f"  [FALTA]  perfil '{esperado}' (rode: python preparar_banco.py)"); problemas += 1
            print("\n4) Perfil de cada usuário:")
            for u in usuarios:
                perfis = db.exec(select(NivelDeAcesso.nivel).join(PerfilDeUsuario,
                    NivelDeAcesso.id_nivel_acesso == PerfilDeUsuario.acesso_id_nivel_acesso)
                    .where(PerfilDeUsuario.acesso_id_usuario == u.id_usuario)).all()
                print(f"  {u.login}: {list(perfis) or 'SEM PERFIL (use --vincular)'}")
    except Exception as e:  # mostra o erro real do banco em vez de esconder
        print(f"  [ERRO] não consegui ler: {str(e).splitlines()[0][:230]}")
        problemas += 1
    print("\n" + ("Tudo certo." if not problemas else f"{problemas} problema(s) encontrado(s): corrija os itens marcados e rode de novo."))


def migrar_senhas(db):
    n = 0
    for u in db.exec(select(Usuario)).all():
        s = u.senha or ""
        if s and not s.startswith("$"):  # texto puro: criptografa com a MESMA senha
            u.senha = criptografar_senha(s)
            db.add(u)
            n += 1
            print(f"  senha de {u.login} criptografada")
        elif s and not s.startswith("$argon2"):
            print(f"  {u.login}: tem um hash de outro tipo; use --redefinir-senha")
    db.commit()
    print(f"{n} senha(s) convertida(s). Entre com a MESMA senha que estava no banco.")


def redefinir_senha(db, login):
    usuario = db.exec(select(Usuario).where(Usuario.login == login)).first()
    if not usuario:
        print(f"Login '{login}' não encontrado na tabela usuario.")
        return
    usuario.senha = criptografar_senha(perguntar(f"  Nova senha para {login} (mín. 8)", None, 8, segredo=True))
    db.add(usuario)
    db.commit()
    print("Senha atualizada e criptografada. Já pode entrar com ela.")


def vincular(db, login, nivel):
    usuario = db.exec(select(Usuario).where(Usuario.login == login)).first()
    perfil = db.exec(select(NivelDeAcesso).where(NivelDeAcesso.nivel == nivel)).first()
    if not usuario:
        print(f"Login '{login}' não encontrado na tabela usuario.")
    elif not perfil:
        print(f"Perfil '{nivel}' não existe. Rode primeiro: python preparar_banco.py")
    elif db.get(PerfilDeUsuario, (usuario.id_usuario, perfil.id_nivel_acesso)):
        print(f"{login} já tem o perfil {nivel}.")
    else:
        db.add(PerfilDeUsuario(acesso_id_usuario=usuario.id_usuario, acesso_id_nivel_acesso=perfil.id_nivel_acesso))
        db.commit()
        print(f"Perfil {nivel} vinculado a {login}.")


def main():
    args = sys.argv[1:]
    exemplos = "--exemplos" in args
    engine = database._engine

    # comandos para o banco que já existe
    if "--diagnosticar" in args:
        diagnosticar(engine)
        return
    if "--migrar-senhas" in args:
        with Session(engine) as db:
            migrar_senhas(db)
        return
    if "--redefinir-senha" in args:
        with Session(engine) as db:
            redefinir_senha(db, args[args.index("--redefinir-senha") + 1])
        return
    if "--vincular" in args:
        i = args.index("--vincular")
        with Session(engine) as db:
            vincular(db, args[i + 1], args[i + 2])
        return

    print("1) Criando as tabelas que ainda não existem...")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as db:
        print("2) Garantindo os perfis de acesso...")
        for nome in NIVEIS:
            if not db.exec(select(NivelDeAcesso).where(NivelDeAcesso.nivel == nome)).first():
                db.add(NivelDeAcesso(nivel=nome))
                print(f"  perfil criado: {nome}")
        db.commit()

        print("3) Administrador...")
        admin = db.exec(select(NivelDeAcesso).where(NivelDeAcesso.nivel == "Administrador")).one()
        if db.exec(select(PerfilDeUsuario).where(PerfilDeUsuario.acesso_id_nivel_acesso == admin.id_nivel_acesso)).first():
            print("  já existe um administrador. Nada a fazer.")
        else:
            nome = perguntar("  Nome completo (mín. 6)", "Administrador do Sistema", 6)
            telefone = perguntar("  Telefone com DDD (mín. 11)", "47999999999", 11)
            login = perguntar("  Login (mín. 10)", "admin@escola.com", 10)
            senha = perguntar("  Senha (mín. 8)", None, 8, segredo=True)
            garantir_usuario(db, nome, telefone, login, senha, "Administrador")

        if exemplos:
            print("4) Dados de exemplo...")
            for nome in ["Notebooks", "Projetores", "Câmeras"]:
                if not db.exec(select(CategoriaEquipamento).where(CategoriaEquipamento.nome == nome)).first():
                    db.add(CategoriaEquipamento(nome=nome))
            db.commit()
            cat = {c.nome: c.id_categoria for c in db.exec(select(CategoriaEquipamento)).all()}
            for pat, nome, modelo, marca, categoria in [
                ("PAT-0412", "Notebook Dell", "Latitude 3420", "Dell", "Notebooks"),
                ("PAT-0413", "Notebook Lenovo", "ThinkPad E14", "Lenovo", "Notebooks"),
                ("PAT-0207", "Projetor Epson", "PowerLite X49", "Epson", "Projetores"),
                ("PAT-0310", "Câmera Canon", "EOS Rebel T7", "Canon", "Câmeras")]:
                if not db.exec(select(Equipamento).where(Equipamento.patrimonio == pat)).first():
                    db.add(Equipamento(patrimonio=pat, nome=nome, modelo=modelo, marca=marca, id_categoria=cat[categoria]))
            db.commit()
            garantir_usuario(db, "Carlos Gestor Teste", "47988888888", "gestor@escola.com", "senha1234", "Gestor")
            garantir_usuario(db, "Ana Solicitante Teste", "47977777777", "solicitante@escola.com", "senha1234", "Solicitante")
            print("  usuários de teste (senha: senha1234): gestor@escola.com e solicitante@escola.com")
            print("  ATENÇÃO: apague esses usuários de teste antes de usar o sistema de verdade.")

    print("Pronto! Agora suba a API com: fastapi dev")


if __name__ == "__main__":
    main()
