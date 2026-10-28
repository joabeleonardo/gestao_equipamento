# Front-end — Cadê o equipamento?

Somente HTML, CSS (Flexbox + Grid) e JavaScript puro. Abra `index.html` no navegador.

| Tela | Arquivo | Quem acessa |
|---|---|---|
| Login | `index.html` | todos |
| Equipamentos e meus pedidos | `usuario.html` | Solicitante |
| Empréstimos e devoluções | `admin.html` | Gestor e Administrador |
| Equipamentos (cadastrar, editar, excluir) | `equipamentos.html` | Gestor vê; só o Administrador altera |
| Usuários | `usuarios.html` | Gestor cadastra e edita; só o Administrador exclui |
| Perfis de acesso | `perfis.html` | somente Administrador |
| Meu perfil | `perfil.html` | qualquer usuário logado |

A navegação entre as telas é feita pelas abas no topo de cada página (mudam conforme o perfil).

- `js/app.js` → `CONFIG.MOCK = true` usa dados de demonstração (sem backend). Use `false` para a API real.
- As rotas ficam em `CONFIG.EP` e seguem o backend corrigido.
- Passo a passo para testar com o banco: veja o `README.md` na raiz do projeto.
