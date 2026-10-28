-- =====================================================================
-- AJUSTE DO SEU BANCO PARA O CÓDIGO DO PROJETO (somente MariaDB)
--
-- Pode ser executado mais de uma vez: usa "IF EXISTS / IF NOT EXISTS", então
-- funciona tanto com as colunas antigas quanto com as já corrigidas.
-- NENHUMA linha de dados é apagada.
--
-- O que ele faz:
--   1) acesso     : colunas viram acesso_id_usuario e acesso_id_nivel_acesso, e as
--                   chaves únicas passam a valer para o PAR (usuário, perfil). Hoje
--                   cada usuário só poderia ter 1 perfil e cada perfil só 1 usuário
--   2) emprestimo : cria a tabela se ela não existe (no CONTROLE_EQUIPAMENTO.sql
--                   original o comando falhava por erro de digitação em
--                   "id_usuario_solicitanete"); ajusta nomes das colunas;
--                   prazo_devolucao passa de DATE para DATETIME
--   3) historico_emprestimo: cria se não existe (o código ainda não usa)
--   4) usuario    : login passa de VARCHAR(20) para VARCHAR(255)
--
-- ANTES DE RODAR, FAÇA BACKUP (no PowerShell):
--     mysqldump -u SEU_USUARIO -p NOME_DO_BANCO > backup.sql
--
-- COMO RODAR: selecione o banco certo (o do seu .env, DB_NAME) no HeidiSQL/Workbench
-- e execute este arquivo; ou no terminal:
--     mysql -u SEU_USUARIO -p NOME_DO_BANCO < ajustar_banco.sql
-- Se der erro, pare e me envie a mensagem completa.
-- =====================================================================

-- ---------- 1) ACESSO ----------
ALTER TABLE acesso DROP FOREIGN KEY IF EXISTS acesso_ibfk_1;
ALTER TABLE acesso DROP FOREIGN KEY IF EXISTS acesso_ibfk_2;
ALTER TABLE acesso DROP INDEX IF EXISTS id_usuario;           -- UNIQUE só no usuário (errado)
ALTER TABLE acesso DROP INDEX IF EXISTS id_nivel_acesso;      -- UNIQUE só no perfil (errado)
ALTER TABLE acesso CHANGE COLUMN IF EXISTS id_usuario      acesso_id_usuario      INT NOT NULL;
ALTER TABLE acesso CHANGE COLUMN IF EXISTS id_nivel_acesso acesso_id_nivel_acesso INT NOT NULL;
ALTER TABLE acesso DROP INDEX IF EXISTS uq_acesso_usuario_perfil;
ALTER TABLE acesso ADD UNIQUE KEY uq_acesso_usuario_perfil (acesso_id_usuario, acesso_id_nivel_acesso);
ALTER TABLE acesso ADD CONSTRAINT acesso_ibfk_1 FOREIGN KEY (acesso_id_usuario)      REFERENCES usuario (id_usuario);
ALTER TABLE acesso ADD CONSTRAINT acesso_ibfk_2 FOREIGN KEY (acesso_id_nivel_acesso) REFERENCES nivel_acesso (id_nivel_acesso);

-- ---------- 2) EMPRESTIMO ----------
CREATE TABLE IF NOT EXISTS emprestimo (
    id_emprestimo          INT AUTO_INCREMENT PRIMARY KEY,
    id_equipamento         INT NOT NULL,
    id_usuario_solicitante INT NOT NULL,
    id_usuario_aprovador   INT NULL,
    data_solicitacao       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_aprovacao         DATETIME NULL,
    prazo_devolucao        DATETIME NOT NULL,
    data_devolucao         DATETIME NULL,
    status_solicitacao     ENUM('pendente','aprovada','negada','devolvido','atrasada') DEFAULT 'pendente',
    CONSTRAINT emprestimo_ibfk_1 FOREIGN KEY (id_equipamento)         REFERENCES equipamento (id_equipamento),
    CONSTRAINT emprestimo_ibfk_2 FOREIGN KEY (id_usuario_solicitante) REFERENCES usuario (id_usuario),
    CONSTRAINT emprestimo_ibfk_3 FOREIGN KEY (id_usuario_aprovador)   REFERENCES usuario (id_usuario)
);
ALTER TABLE emprestimo DROP FOREIGN KEY IF EXISTS emprestimo_ibfk_2;
ALTER TABLE emprestimo DROP FOREIGN KEY IF EXISTS emprestimo_ibfk_3;
ALTER TABLE emprestimo CHANGE COLUMN IF EXISTS id_solicitante id_usuario_solicitante INT NOT NULL;
ALTER TABLE emprestimo CHANGE COLUMN IF EXISTS id_aprovador   id_usuario_aprovador   INT NULL DEFAULT NULL;
ALTER TABLE emprestimo MODIFY prazo_devolucao DATETIME NOT NULL;
ALTER TABLE emprestimo ADD CONSTRAINT emprestimo_ibfk_2 FOREIGN KEY (id_usuario_solicitante) REFERENCES usuario (id_usuario);
ALTER TABLE emprestimo ADD CONSTRAINT emprestimo_ibfk_3 FOREIGN KEY (id_usuario_aprovador)   REFERENCES usuario (id_usuario);

-- ---------- 3) HISTORICO_EMPRESTIMO ----------
CREATE TABLE IF NOT EXISTS historico_emprestimo (
    id_historico  INT AUTO_INCREMENT PRIMARY KEY,
    id_emprestimo INT NOT NULL,
    id_usuario    INT NOT NULL,
    acao          VARCHAR(50),
    data_cadastro TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (id_emprestimo) REFERENCES emprestimo (id_emprestimo),
    FOREIGN KEY (id_usuario)    REFERENCES usuario (id_usuario)
);

-- ---------- 4) USUARIO ----------
ALTER TABLE usuario MODIFY login VARCHAR(255) NOT NULL;

-- ---------- CONFERÊNCIA (opcional) ----------
-- SHOW COLUMNS FROM acesso;
-- SHOW COLUMNS FROM emprestimo;
-- SHOW INDEX   FROM acesso;
-- SELECT * FROM nivel_acesso;   -- o código exige exatamente: Solicitante, Gestor, Administrador
