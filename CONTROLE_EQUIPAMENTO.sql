-- Script do banco CONTROLE_EQUIPAMENTO (MariaDB). Corrigido para bater com o código do projeto.
-- As linhas alteradas têm o comentário '-- ALTERADO'. Execute em um banco vazio (veja o README, item 4A).

create table usuario(
id_usuario int auto_increment primary key,
nome varchar (200) not null,
telefone varchar(20) not null,
login varchar (255) unique not null, -- ALTERADO: era varchar(20), pequeno demais para logins em formato de e-mail
senha varchar(255) not null,
data_criacao datetime default current_timestamp
);

create table nivel_acesso(
id_nivel_acesso int auto_increment primary key,
nivel varchar (20) unique not null,
data_criacao datetime default current_timestamp
);

create table acesso(
id_acesso int auto_increment primary key,
acesso_id_usuario int not null, -- ALTERADO: era id_usuario (o código Python usa este nome)
acesso_id_nivel_acesso int not null, -- ALTERADO: era id_nivel_acesso (o código Python usa este nome)
unique key uq_acesso_usuario_perfil (acesso_id_usuario, acesso_id_nivel_acesso), -- ALTERADO: antes cada coluna era "unique" sozinha (1 perfil por usuário e cada perfil para 1 usuário só)
foreign key (acesso_id_usuario) references usuario (id_usuario),
foreign key (acesso_id_nivel_acesso) references nivel_acesso (id_nivel_acesso));


create table categoria_equipamento(
id_categoria int auto_increment primary key,
nome varchar (100) not null,
data_criacao datetime default current_timestamp);


create table equipamento(
id_equipamento int auto_increment primary key,
nome varchar(100) not null,
id_categoria int not null,
patrimonio varchar(100) unique not null,
marca varchar(100),
modelo varchar(100),
status_equipamento enum ('disponivel', 'emprestado','manutencao','baixado') default 'disponivel',
data_cadastro datetime default current_timestamp,
foreign key (id_categoria) references categoria_equipamento (id_categoria));



create table emprestimo(
id_emprestimo int auto_increment primary key,
id_equipamento int not null,
id_usuario_solicitante int not null,
id_usuario_aprovador int null,
data_solicitacao timestamp default current_timestamp,
data_aprovacao datetime null,
prazo_devolucao datetime not null, -- ALTERADO: era date (perdia a hora limite)
data_devolucao datetime null,
status_solicitacao enum ('pendente','aprovada','negada','devolvido','atrasada') default 'pendente',
foreign key (id_equipamento) references equipamento (id_equipamento),
foreign key (id_usuario_solicitante) references usuario (id_usuario), -- ALTERADO: estava 'solicitanete' (erro de digitação que impedia criar a tabela emprestimo)
foreign key (id_usuario_aprovador) references usuario (id_usuario)
);


create table historico_emprestimo(
id_historico int auto_increment primary key,
id_emprestimo int not null,
id_usuario int not null,
acao varchar (50), #"solicitou","devolveu","negou","devolveu","retirou"#
data_cadastro timestamp,
foreign key (id_emprestimo) references emprestimo(id_emprestimo),
foreign key (id_usuario) references usuario(id_usuario)

);




