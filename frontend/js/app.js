/* =====================================================================
   CONFIGURAÇÃO — é aqui que o front é ligado ao seu backend/banco.
   CONFIG é uma constante (um objeto), e MOCK e API são propriedades dele.
     API  = endereço onde o backend está rodando (fastapi dev)
     MOCK = true  -> dados de teste, SEM backend e SEM banco (demonstração)
            false -> usa a API e o seu banco de verdade
   ===================================================================== */
const CONFIG = {
  API: "http://127.0.0.1:8000",
  MOCK: false, // false = usa a API e o seu banco  |  true = dados de teste, sem backend
  EP: { // rotas do backend
    login: "/auth/login",
    equip: "/equipamentos",
    emp: "/emprestimos",
    usr: "/usuario/usuarios",
    usuario: "/usuario",
    me: "/usuario/me",
    niveis: "/niveis-acesso/",
    vinc: "/perfil_usuario",
    vincNovo: "/usuarios-has-role",
    vincDel: "/perfis_usuario", // DELETE /perfis_usuario/{id_usuario}/{id_nivel_acesso}
    cat: "/categorias/"
  }
};
const EP = CONFIG.EP;
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmt = d => d ? new Date(d).toLocaleDateString("pt-BR") : "—";
const ROTULO = {pendente:"Pendente",aprovada:"Aprovado",negada:"Negado",devolvido:"Devolvido",atrasada:"Atrasado",
  disponivel:"Disponível",emprestado:"Emprestado",manutencao:"Manutenção",baixado:"Baixado (inativo)"};
const badge = s => `<span class="badge s-${s}">${ROTULO[s] || s}</span>`;
// "atrasada" é calculado aqui: aprovado e com prazo vencido
const statusEmp = e => e.status_solicitacao === "aprovada" && e.prazo_devolucao && new Date(e.prazo_devolucao) < new Date() ? "atrasada" : e.status_solicitacao;
const tag = p => `<span class="tag">${esc(p)}</span>`;

let _t;
function aviso(msg, erro) {
  const a = $("aviso"); a.textContent = msg; a.className = erro ? "erro-aviso" : ""; a.hidden = false;
  clearTimeout(_t); _t = setTimeout(() => a.hidden = true, 4000);
}

const Auth = {
  token: () => sessionStorage.getItem("tk"),
  user() {
    const t = this.token(); if (!t) return null;
    try {
      const p = JSON.parse(atob(t.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));
      return { id: Number(p.sub), roles: p.roles || [], nome: sessionStorage.getItem("nome") || "" };
    } catch { return null; }
  },
  isAdmin: u => u.roles.some(r => ["Administrador", "Admin", "Gestor"].includes(r)),
  // cadastrar/editar/excluir equipamento: somente o Administrador (o Gestor não pode)
  ehAdministrador: u => !!u && u.roles.some(r => ["Administrador", "Admin"].includes(r)), // só o Administrador
  podeGerirEquipamentos: u => !!u && u.roles.some(r => ["Administrador", "Admin"].includes(r)),
  // protege a página: manda para o login ou para o painel correto
  // guard(admin) {
  //   const u = this.user();
  //   if (!u) { location.href = "index.html"; return null; }
  //   if (this.isAdmin(u) !== admin) { location.href = this.isAdmin(u) ? "admin.html" : "usuario.html"; return null; }
  //   return u;
  // },
  
guard(admin) {
  const u = this.user();

  if (!u || !Number.isInteger(u.id) || u.id <= 0) {
    location.href = "index.html";
    return null;
  }

  // Páginas de gestão: Administrador e Gestor.
  if (admin && !this.isAdmin(u)) {
    location.href = "usuario.html";
    return null;
  }

  // Solicitante também pode acessar o catálogo.
  // Gestor e Administrador não devem ser redirecionados
  // para admin.html apenas por acessarem usuario.html.
  return u;
},

  logout() { sessionStorage.clear(); location.href = "index.html"; }
};
    

async function api(metodo, rota, corpo) {
  if (CONFIG.MOCK) return mock(metodo, rota, corpo);
  let r;
  try {
    r = await fetch(CONFIG.API + rota, { method: metodo, body: corpo && JSON.stringify(corpo),
      headers: { "Content-Type": "application/json", ...(Auth.token() && { Authorization: "Bearer " + Auth.token() }) } });
  } catch { throw new Error("Não foi possível conectar à API. Ela está rodando?"); }
  if (r.status === 401 && rota !== EP.login) { Auth.logout(); return; }
  if (r.status === 204) return null;
  const d = await r.json().catch(() => null);
  if (!r.ok) throw new Error(typeof d?.detail === "string" ? d.detail : "Não foi possível concluir a operação.");
  return d;
}

/* ---------- Modo demonstração: simula o backend no localStorage ---------- */
function mock(m, p, b) {
  const dia = n => new Date(Date.now() + n * 864e5).toISOString();
  let db = JSON.parse(localStorage.getItem("mockdb") || "null");
  if (!db) db = {
    users: [
      {id:1,nome:"Ana Souza",telefone:"47911110001",login:"ana.souza@escola.com",senha:"senha1234",roles:["Solicitante"]},
      {id:2,nome:"Carlos Gestor",telefone:"47911110002",login:"gestor@escola.com",senha:"senha1234",roles:["Gestor"]},
      {id:3,nome:"Admin Geral",telefone:"47911110003",login:"admin@escola.com",senha:"senha1234",roles:["Administrador"]}],
    cat: [{id_categoria:1,nome:"Notebooks"},{id_categoria:2,nome:"Projetores"},{id_categoria:3,nome:"Câmeras"}],
    equip: [
      ["PAT-0412","Notebook Dell","Latitude 3420","Dell",1,"disponivel"],["PAT-0413","Notebook Lenovo","ThinkPad E14","Lenovo",1,"disponivel"],
      ["PAT-0207","Projetor Epson","PowerLite X49","Epson",2,"disponivel"],["PAT-0208","Projetor BenQ","MS550 SVGA","BenQ",2,"emprestado"],
      ["PAT-0310","Câmera Canon","EOS Rebel T7","Canon",3,"manutencao"],["PAT-0311","Câmera Sony","Alpha ZV-E10","Sony",3,"emprestado"]
    ].map((e,i)=>({id_equipamento:i+1,patrimonio:e[0],nome:e[1],modelo:e[2],marca:e[3],id_categoria:e[4],status_equipamento:e[5]})),
    emp: [
      {id_emprestimo:1,id_equipamento:2,id_usuario_solicitante:1,id_usuario_aprovador:null,prazo_devolucao:dia(7),status_solicitacao:"pendente",data_solicitacao:dia(-1),data_aprovacao:null,data_devolucao:null},
      {id_emprestimo:2,id_equipamento:4,id_usuario_solicitante:1,id_usuario_aprovador:2,prazo_devolucao:dia(-2),status_solicitacao:"aprovada",data_solicitacao:dia(-9),data_aprovacao:dia(-8),data_devolucao:null},
      {id_emprestimo:3,id_equipamento:6,id_usuario_solicitante:1,id_usuario_aprovador:2,prazo_devolucao:dia(4),status_solicitacao:"aprovada",data_solicitacao:dia(-3),data_aprovacao:dia(-2),data_devolucao:null}]
  };
  const salvar = () => localStorage.setItem("mockdb", JSON.stringify(db));
  const base = p.replace(/\/\d+$/, ""), id = Number(p.split("/").pop());
  if (p === EP.niveis || p === EP.vinc || p === EP.vincNovo || p.startsWith(EP.vincDel + "/")) { // perfis de acesso (admin)
    if (!Auth.ehAdministrador(Auth.user())) throw new Error("Acesso negado. Você não tem permissão para realizar esta operação.");
    const NIVEIS = [{id_nivel_acesso:1,nivel:"Solicitante"},{id_nivel_acesso:2,nivel:"Gestor"},{id_nivel_acesso:3,nivel:"Administrador"}];
    if (p === EP.niveis) return NIVEIS;
    if (p === EP.vinc) return db.users.flatMap(u => u.roles.map(r => ({ acesso_id_usuario: u.id, acesso_id_nivel_acesso: NIVEIS.find(n => n.nivel === r).id_nivel_acesso })));
    const [uId, nId] = p === EP.vincNovo ? [b.acesso_id_usuario, b.acesso_id_nivel_acesso] : p.split("/").slice(-2).map(Number);
    const usr = db.users.find(x => x.id === uId), nv = NIVEIS.find(n => n.id_nivel_acesso === nId);
    if (m === "POST") {
      if (!usr) throw new Error("Usuário informado não está cadastrado no sistema.");
      if (usr.roles.includes(nv.nivel)) throw new Error("Este vínculo já existe ou os dados são inválidos.");
      usr.roles.push(nv.nivel); salvar(); return b;
    }
    if (uId === Auth.user().id) throw new Error("Você não pode remover os seus próprios perfis de acesso.");
    if (!usr || !usr.roles.includes(nv.nivel)) throw new Error(`Vínculo usuário ${uId} x role ${nId} não encontrado.`);
    usr.roles = usr.roles.filter(r => r !== nv.nivel); salvar(); return null;
  }
  if (base === EP.login) {
    const u = db.users.find(x => x.login === b.login && x.senha === b.senha);
    if (!u) throw new Error("Login ou senha incorretos.");
    return { access_token: `x.${btoa(JSON.stringify({sub:String(u.id),roles:u.roles}))}.x`, usuario: { nome: u.nome } };
  }
  if (base === EP.equip && m !== "GET" && !Auth.podeGerirEquipamentos(Auth.user()))
    throw new Error("Acesso negado. Você não tem permissão para realizar esta operação.");
  if (base === EP.me) { // meu perfil: sempre o usuário do token
    const u = db.users.find(x => x.id === Auth.user().id);
    if (m === "PUT") {
      if (b.login && db.users.some(x => x.login === b.login && x.id !== u.id))
        throw new Error("Erro de integridade. Verifique se o login já existe.");
      if (b.nova_senha) {
        if (b.senha_atual !== u.senha) throw new Error("Senha atual incorreta.");
        u.senha = b.nova_senha;
      }
      for (const c of ["nome", "telefone", "login"]) if (b[c]) u[c] = b[c];
      salvar();
    }
    return { id_usuario: u.id, nome: u.nome, telefone: u.telefone || "", login: u.login };
  }
  if (base === EP.usuario) { // cadastro: Gestor e Administrador; exclusão: só Administrador
    if (m === "DELETE" && !Auth.podeGerirEquipamentos(Auth.user()))
      throw new Error("Acesso negado. Você não tem permissão para realizar esta operação.");
    if (m === "POST") {
      if (db.users.some(x => x.login === b.login)) throw new Error("Usuario indisponivel");
      const novo = { id: Date.now() % 1e6, ...b, roles: [] }; // como no backend: sem perfil até o administrador vincular
      db.users.push(novo); salvar();
      return { id_usuario: novo.id, nome: novo.nome, telefone: novo.telefone, login: novo.login };
    }
    if (m === "PUT") {
      const i = db.users.findIndex(x => x.id === id);
      if (i < 0) throw new Error(`Usuário de ID ${id} não encontrado.`);
      const { senha, ...resto } = b;
      db.users[i] = { ...db.users[i], ...resto, ...(senha ? { senha } : {}) }; salvar();
      const u = db.users[i];
      return { id_usuario: u.id, nome: u.nome, telefone: u.telefone, login: u.login };
    }
    if (m === "DELETE") {
      if (db.emp.some(x => x.id_usuario_solicitante === id || x.id_usuario_aprovador === id))
        throw new Error("Usuário possui empréstimos registrados e não pode ser excluído.");
      db.users = db.users.filter(x => x.id !== id); salvar(); return null;
    }
  }
  if (base === EP.usr) return db.users.map(({senha, ...u}) => u);
  if (base === EP.cat) return db.cat;
  const k = base === EP.equip ? "equip" : "emp", chave = k === "equip" ? "id_equipamento" : "id_emprestimo";
  let saida = db[k];
  if (m === "POST") { saida = { ...b, [chave]: Date.now() % 1e6, data_solicitacao: new Date().toISOString() }; db[k].push(saida); }
  if (m === "PUT") {
    const i = db[k].findIndex(x => x[chave] === id); saida = db[k][i] = { ...db[k][i], ...b };
    if (k === "emp") { // o backend deveria atualizar o status do equipamento sozinho
      const q = db.equip.find(e => e.id_equipamento === saida.id_equipamento);
      if (q) q.status_equipamento = { aprovada: "emprestado", devolvido: "disponivel" }[saida.status_solicitacao] || q.status_equipamento;
    }
  }
  if (m === "DELETE" && k === "equip" && db.emp.some(x => x.id_equipamento === id))
    throw new Error("Equipamento possui empréstimos registrados e não pode ser excluído.");
  if (m === "DELETE") { db[k] = db[k].filter(x => x[chave] !== id); saida = null; }
  salvar();
  return saida && JSON.parse(JSON.stringify(saida));
}

// cabeçalho comum aos dashboards


function montarTopo(u) {
  if (CONFIG.MOCK) $("demo").hidden = false;

  $("nome").textContent = u.nome || "Usuário #" + u.id;
  $("sair").onclick = () => Auth.logout();

  const abas = Auth.isAdmin(u)
    ? [
        ["usuario.html", "Catálogo e solicitações"],
        ["admin.html", "Gerenciar empréstimos"],
        ["equipamentos.html", "Equipamentos"],
        ["usuarios.html", "Usuários"],
        ...(Auth.ehAdministrador(u)
          ? [["perfis.html", "Perfis de acesso"]]
          : []),
        ["perfil.html", "Meu perfil"]
      ]
    : [
        ["usuario.html", "Equipamentos"],
        ["perfil.html", "Meu perfil"]
      ];

  const atual = decodeURIComponent(location.pathname.split("/").pop());
  const container = $("abas");

  container.innerHTML = abas
    .map(([href, texto]) =>
      `<a href="${href}"${href === atual ? ' aria-current="page"' : ""}>${texto}</a>`
    )
    .join("");
}
