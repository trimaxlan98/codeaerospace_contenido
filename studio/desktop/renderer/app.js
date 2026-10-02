/* global Terminal, FitAddon, WebLinksAddon */
'use strict';

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const esc = (s) =>
  String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

function bytes(n) {
  if (n == null) return '—';
  const u = ['B', 'KB', 'MB', 'GB', 'TB'];
  let i = 0;
  while (n >= 1024 && i < u.length - 1) {
    n /= 1024;
    i++;
  }
  return `${n.toFixed(n >= 100 || i === 0 ? 0 : 1)} ${u[i]}`;
}
function fecha(ms) {
  if (!ms) return '—';
  return new Date(ms).toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' });
}
function toast(msg) {
  const t = $('#toast');
  t.textContent = msg;
  t.classList.add('is-on');
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => t.classList.remove('is-on'), 2600);
}

const S = { info: null, view: 'inicio', svc: { state: 'stopped' } };
const VISTAS = ['inicio', 'estudio', 'presentaciones', 'marca', 'exports', 'terminal', 'sistema', 'contenido'];

/* ─── Navegación ─────────────────────────────────────────── */
function show(view) {
  S.view = view;
  $$('.rail__btn').forEach((b) => b.classList.toggle('is-active', b.dataset.view === view));
  $$('.view').forEach((v) => v.classList.toggle('is-active', v.id === `view-${view}`));
  if (view === 'inicio') Inicio.refresh();
  if (view === 'estudio') Estudio.select(Estudio.target);
  if (view === 'presentaciones') Pres.ensure();
  if (view === 'marca') Marca.ensure();
  if (view === 'exports') Exports.ensure();
  if (view === 'terminal') Term.fitActive();
  if (view === 'sistema') Sistema.refreshInfo();
  if (view === 'contenido') Contenido.ensure();
}
$$('[data-view]').forEach((b) => b.addEventListener('click', () => show(b.dataset.view)));
document.addEventListener('keydown', (e) => {
  const n = Number(e.key);
  if (e.ctrlKey && !e.shiftKey && n >= 1 && n <= VISTAS.length) {
    show(VISTAS[n - 1]);
    e.preventDefault();
  }
  if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 't') {
    show('terminal');
    Term.open({});
    e.preventDefault();
  }
  if (e.key === 'F5' && S.view === 'estudio') {
    Estudio.reload();
    e.preventDefault();
  }
  if (e.key === 'Escape' && S.view === 'exports') Exports.closeDetail();
});

/* ─── Estudio (webview local / producción) ───────────────── */
const Estudio = {
  target: 'local',
  views: {},
  ready: false,

  url(target) {
    return target === 'prod' ? S.info.prodUrl : S.info.uiUrl;
  },

  mount(target) {
    if (this.views[target]) return this.views[target];
    const wv = document.createElement('webview');
    wv.setAttribute('partition', target === 'prod' ? 'persist:prod' : 'persist:local');
    wv.setAttribute('src', this.url(target));
    wv.addEventListener('did-navigate', () => this.syncUrl());
    wv.addEventListener('did-navigate-in-page', () => this.syncUrl());
    $('#stFrames').appendChild(wv);
    this.views[target] = wv;
    return wv;
  },

  select(target) {
    this.target = target;
    $$('#view-estudio .seg__btn').forEach((b) => b.classList.toggle('is-active', b.dataset.target === target));
    if (target === 'local' && !this.ready) {
      this.syncWait();
      return;
    }
    const wv = this.mount(target);
    Object.entries(this.views).forEach(([k, v]) => v.classList.toggle('is-active', k === target));
    $('#stWait').hidden = true;
    this.syncUrl(wv);
  },

  active() {
    return this.views[this.target];
  },

  syncUrl() {
    const wv = this.active();
    let url = this.url(this.target);
    try {
      url = wv?.getURL() || url;
    } catch {
      /* el webview aun no esta listo */
    }
    $('#stUrl').textContent = url;
  },

  reload() {
    this.active()?.reload();
  },

  syncWait() {
    const st = S.svc.state;
    const wait = $('#stWait');
    if (this.target !== 'local') return;
    wait.hidden = this.ready;
    $('.spinner', wait).style.display = st === 'starting' || st === 'stopped' ? '' : 'none';
    $('#stWaitText').textContent = !S.info.repo
      ? 'Falta elegir el checkout de codeaerospace_contenido.'
      : st === 'error'
        ? `Los servicios no arrancaron: ${S.svc.detail || 'revisa el registro'}`
        : st === 'stopped'
          ? 'Los servicios están detenidos.'
          : 'Levantando runner y backend…';
    $('#stWaitSistema').hidden = st !== 'error' && st !== 'stopped' && !!S.info.repo;
  },

  onServices(s) {
    const up = s.state === 'running' || s.state === 'external';
    if (up && !this.ready) {
      this.ready = true;
      // Si el Estudio ya estaba montado, vuelve de una caida o un reinicio:
      // su conexion SSE murio con el backend anterior.
      this.views.local?.reload();
      if (this.target === 'local') this.select('local');
    }
    if (!up) this.ready = false;
    if (!up && this.target === 'local') {
      Object.values(this.views).forEach((v) => v.classList.remove('is-active'));
    }
    this.syncWait();
  },
};
$$('#view-estudio .seg__btn').forEach((b) => b.addEventListener('click', () => Estudio.select(b.dataset.target)));
$('#stReload').addEventListener('click', () => Estudio.reload());
$('#stBack').addEventListener('click', () => {
  const wv = Estudio.active();
  if (wv?.canGoBack()) wv.goBack();
});
$('#stExternal').addEventListener('click', () => window.studio.openExternal(Estudio.url(Estudio.target)));
$('#stDevtools').addEventListener('click', () => Estudio.active()?.openDevTools());
$('#stWaitSistema').addEventListener('click', () => show('sistema'));

/* ─── Exports ────────────────────────────────────────────── */
const ICONOS = {
  video: '<path d="M4 6h11v12H4z"/><path d="m15 10 5-3v10l-5-3"/>',
  audio: '<path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>',
  imagen: '<rect x="4" y="4" width="16" height="16" rx="2"/><circle cx="9" cy="9" r="1.6"/><path d="m20 15-5-5-9 9"/>',
  documento: '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/>',
  texto: '<path d="M6 3h8l4 4v14H6z"/><path d="M9 12h6M9 16h6"/>',
  otro: '<path d="M6 3h8l4 4v14H6z"/>',
  dir: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
};
// Un color por tema, repartido por posicion para que dos vecinos no coincidan.
const PALETA = ['#00d8f6', '#f59e0b', '#10b981', '#a78bfa', '#f65670', '#3b82f6', '#eab308', '#2dd4bf', '#fb923c', '#e879f9', '#84cc16', '#60a5fa'];
const colorDe = (i) => PALETA[i % PALETA.length];

const Exports = {
  cat: null,
  tema: null,
  sort: 'orden',
  query: '',
  proyecto: null,
  ruta: '',
  loading: null,

  async ensure(refresh = false) {
    if (this.cat && !refresh) return;
    if (!S.info.repo) {
      $('#expProyectos').innerHTML = '<p class="vacio">Configura el repositorio en Sistema.</p>';
      return;
    }
    $('#expTotal').textContent = 'escaneando…';
    this.loading = window.studio.exports.catalog(refresh);
    this.cat = await this.loading;
    if (!this.cat) return;
    if (!this.tema || !this.cat.temas.some((t) => t.id === this.tema)) this.tema = this.cat.temas[0]?.id;
    this.renderTemas();
    this.renderProyectos();
    $('#areasList').innerHTML = this.cat.temas
      .filter((t) => t.tipo === 'area')
      .map((t) => `<option value="${esc(t.nombre)}">`)
      .join('');
  },

  renderTemas() {
    const c = this.cat;
    const cursos = c.temas.filter((t) => t.tipo === 'area').reduce((n, t) => n + t.proyectos.length, 0);
    $('#expTotal').textContent = `${bytes(c.bytes)} · ${c.archivos.toLocaleString('es-MX')} archivos · ${cursos} cursos`;
    let html = '<li class="temas__sep">Temas</li>';
    let sep = false;
    c.temas.forEach((t, i) => {
      if (t.tipo !== 'area' && !sep) {
        html += '<li class="temas__sep">Colecciones</li>';
        sep = true;
      }
      html += `<li><button class="tema ${t.id === this.tema && !this.query ? 'is-active' : ''}" data-id="${esc(t.id)}">
        <i class="tema__swatch" style="background:${colorDe(i)}"></i>
        <span class="tema__name">${esc(t.nombre)}</span><span class="tema__n">${t.proyectos.length}</span></button></li>`;
    });
    $('#expTemas').innerHTML = html;
    $$('#expTemas .tema').forEach((b) =>
      b.addEventListener('click', () => {
        this.tema = b.dataset.id;
        this.query = '';
        $('#expSearch').value = '';
        this.renderTemas();
        this.renderProyectos();
      })
    );
  },

  ordenar(lista) {
    const l = [...lista];
    if (this.sort === 'reciente') l.sort((a, b) => b.mtime - a.mtime);
    if (this.sort === 'peso') l.sort((a, b) => b.bytes - a.bytes);
    return l;
  },

  card(p, t) {
    const num = p.etiqueta || '';
    return `<div class="proy ${this.proyecto?.id === p.id ? 'is-active' : ''}" tabindex="0" data-id="${esc(p.id)}" data-tema="${esc(t.id)}">
      <div class="proy__top">${num ? `<span class="proy__num">${esc(num)}</span>` : ''}<span class="proy__name">${esc(p.nombre)}</span></div>
      <div class="proy__meta"><span>${bytes(p.bytes)}</span><span>${p.archivos} arch.</span><span>${fecha(p.mtime)}</span></div>
      ${p.entrega ? '<button class="proy__play" title="Reproducir la entrega"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button>' : '<span class="proy__noentrega">sin video de entrega</span>'}
    </div>`;
  },

  renderProyectos() {
    const host = $('#expProyectos');
    const q = this.query.trim().toLowerCase();
    let html = '';
    if (q) {
      $('#expEyebrow').textContent = 'Búsqueda';
      $('#expTitle').textContent = `“${this.query}”`;
      let n = 0;
      for (const t of this.cat.temas) {
        const hits = t.proyectos.filter(
          (p) => `${t.nombre} ${p.nombre} ${p.id} ${p.etiqueta || ''}`.toLowerCase().includes(q)
        );
        if (!hits.length) continue;
        n += hits.length;
        html += `<h3 class="proyectos__grupo">${esc(t.nombre)}</h3>` + this.ordenar(hits).map((p) => this.card(p, t)).join('');
      }
      if (!n) html = '<p class="vacio">Nada coincide.</p>';
    } else {
      const t = this.cat.temas.find((x) => x.id === this.tema);
      if (!t) return;
      $('#expEyebrow').textContent = t.tipo === 'area' ? `Tema · ${t.proyectos.length} cursos · ${bytes(t.bytes)}` : `Colección · ${bytes(t.bytes)}`;
      $('#expTitle').textContent = t.nombre;
      // En un area numerada se agrupa por modulo (el primer numero: 1.x, 2.x...).
      const modular = this.sort === 'orden' && t.proyectos.some((p) => (p.numero || []).length > 1);
      if (modular) {
        const grupos = new Map();
        for (const p of t.proyectos) {
          const k = p.numero[0] ?? '—';
          if (!grupos.has(k)) grupos.set(k, []);
          grupos.get(k).push(p);
        }
        for (const [k, ps] of grupos) html += `<h3 class="proyectos__grupo">Módulo ${esc(k)}</h3>` + ps.map((p) => this.card(p, t)).join('');
      } else {
        html = this.ordenar(t.proyectos).map((p) => this.card(p, t)).join('') || '<p class="vacio">Vacío.</p>';
      }
    }
    host.innerHTML = html;
    host.scrollTop = 0;
    $$('.proy', host).forEach((el) => {
      const pick = (play) => {
        const t = this.cat.temas.find((x) => x.id === el.dataset.tema);
        const p = t.proyectos.find((x) => x.id === el.dataset.id);
        this.openDetail(p, t, play);
      };
      el.addEventListener('click', (e) => pick(!!e.target.closest('.proy__play')));
      el.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') pick(false);
      });
    });
  },

  async abrir(rel) {
    const r = await window.studio.exports.open(rel);
    if (!r.ok) toast(r.error || 'No se pudo abrir');
  },

  mediaUrl(rel) {
    const path = rel.split('/').map(encodeURIComponent).join('/');
    return `${S.info.uiUrl}/__media/${path}?t=${S.info.mediaToken}`;
  },

  async openDetail(p, t, play) {
    this.proyecto = p;
    $$('.proy').forEach((el) => el.classList.toggle('is-active', el.dataset.id === p.id));
    $('#expDetail').hidden = false;
    $('#detEyebrow').textContent = t.nombre + (p.etiqueta ? ` · ${p.etiqueta}` : '');
    $('#detTitle').textContent = p.nombre;
    $('#detMeta').textContent = `${bytes(p.bytes)} · ${p.archivos} archivos · ${fecha(p.mtime)} · exports/${p.rel}`;
    $('#detOpen').disabled = !p.entrega;
    $('#detPlayer').innerHTML = '';
    if (p.entrega) this.preview(`${p.rel}/${p.entrega}`, 'video', play);
    await this.browse(p.rel);
  },

  closeDetail() {
    $('#detPlayer').innerHTML = '';
    $('#expDetail').hidden = true;
    this.proyecto = null;
    $$('.proy').forEach((el) => el.classList.remove('is-active'));
  },

  preview(rel, tipo, autoplay = false) {
    const host = $('#detPlayer');
    const url = this.mediaUrl(rel);
    if (tipo === 'video') host.innerHTML = `<video controls preload="metadata" src="${esc(url)}"></video>`;
    else if (tipo === 'audio') host.innerHTML = `<audio controls src="${esc(url)}"></audio>`;
    else if (tipo === 'imagen') host.innerHTML = `<img alt="" src="${esc(url)}">`;
    else return false;
    if (autoplay) host.querySelector('video,audio')?.play().catch(() => {});
    return true;
  },

  async browse(rel) {
    this.ruta = rel;
    const base = this.proyecto.rel;
    const partes = rel.slice(base.length).split('/').filter(Boolean);
    let acc = base;
    $('#detCrumbs').innerHTML =
      `<button data-rel="${esc(base)}">${esc(base.split('/').pop())}</button>` +
      partes
        .map((x) => {
          acc += `/${x}`;
          return ` / <button data-rel="${esc(acc)}">${esc(x)}</button>`;
        })
        .join('');
    $$('#detCrumbs button').forEach((b) => b.addEventListener('click', () => this.browse(b.dataset.rel)));

    const items = await window.studio.exports.list(rel);
    const entrega = `${this.proyecto.rel}/${this.proyecto.entrega}`;
    $('#detFiles').innerHTML = items
      .map(
        (f) => `<li><button class="file" data-rel="${esc(f.rel)}" data-dir="${f.dir ? 1 : ''}" data-tipo="${esc(f.tipo || '')}" title="${esc(f.nombre)}">
        <span class="file__ico" data-t="${f.dir ? 'dir' : esc(f.tipo)}"><svg viewBox="0 0 24 24">${ICONOS[f.dir ? 'dir' : f.tipo] || ICONOS.otro}</svg></span>
        <span class="file__name">${esc(f.nombre)}</span>
        ${f.rel === entrega ? '<span class="file__star">ENTREGA</span>' : ''}
        <span class="file__size">${f.dir ? `${f.n} elem.` : bytes(f.size)}</span></button></li>`
      )
      .join('');
    $$('#detFiles .file').forEach((b) => {
      b.addEventListener('click', () => {
        if (b.dataset.dir) return this.browse(b.dataset.rel);
        $$('#detFiles .file').forEach((x) => x.classList.toggle('is-active', x === b));
        if (!this.preview(b.dataset.rel, b.dataset.tipo, true)) this.abrir(b.dataset.rel);
      });
      b.addEventListener('dblclick', () => !b.dataset.dir && this.abrir(b.dataset.rel));
    });
  },
};
$('#expSearch').addEventListener('input', (e) => {
  Exports.query = e.target.value;
  Exports.renderTemas();
  Exports.renderProyectos();
});
$$('#view-exports [data-sort]').forEach((b) =>
  b.addEventListener('click', () => {
    Exports.sort = b.dataset.sort;
    $$('#view-exports [data-sort]').forEach((x) => x.classList.toggle('is-active', x === b));
    Exports.renderProyectos();
  })
);
$('#expRefresh').addEventListener('click', async () => {
  await Exports.ensure(true);
  toast('Exports escaneados de nuevo');
});
$('#expRevealTema').addEventListener('click', () => {
  const t = Exports.cat?.temas.find((x) => x.id === Exports.tema);
  const rel = Exports.proyecto?.rel || (t?.id.startsWith('col:') && !t.id.endsWith('bancos') ? t.id.slice(4) : '');
  window.studio.exports.reveal(rel);
});
$('#detClose').addEventListener('click', () => Exports.closeDetail());
$('#detOpen').addEventListener('click', async () => {
  const p = Exports.proyecto;
  const r = await window.studio.exports.open(`${p.rel}/${p.entrega}`);
  if (!r.ok) toast(r.error || 'No se pudo abrir');
});
$('#detReveal').addEventListener('click', () => {
  const p = Exports.proyecto;
  window.studio.exports.reveal(p.entrega ? `${p.rel}/${p.entrega}` : p.rel);
});
$('#detCopy').addEventListener('click', async () => {
  const full = await window.studio.exports.copyPath(Exports.ruta || Exports.proyecto.rel);
  toast(`Copiado: ${full}`);
});

/* ─── Terminal ───────────────────────────────────────────── */
const TEMA_XTERM = {
  background: '#080f15',
  foreground: '#e6eaf2',
  cursor: '#00d9ff',
  cursorAccent: '#080f15',
  selectionBackground: 'rgba(0, 216, 246, 0.28)',
  black: '#1b2130', red: '#f65670', green: '#10b981', yellow: '#f59e0b',
  blue: '#3b82f6', magenta: '#a78bfa', cyan: '#00d8f6', white: '#c9d2e0',
  brightBlack: '#5d6a80', brightRed: '#ff7b90', brightGreen: '#34d399', brightYellow: '#fbbf24',
  brightBlue: '#60a5fa', brightMagenta: '#c4b5fd', brightCyan: '#67e8f9', brightWhite: '#ffffff',
};

const Term = {
  tabs: new Map(), // id -> { xterm, fit, pane, tab, dead }
  active: null,

  async open(opts) {
    const xterm = new Terminal({
      fontFamily: getComputedStyle(document.documentElement).getPropertyValue('--mono'),
      fontSize: 13.5,
      lineHeight: 1.2,
      cursorBlink: true,
      scrollback: 20000,
      allowProposedApi: true,
      theme: TEMA_XTERM,
    });
    const fit = new FitAddon.FitAddon();
    xterm.loadAddon(fit);
    xterm.loadAddon(new WebLinksAddon.WebLinksAddon((_e, url) => window.studio.openExternal(url)));

    const pane = document.createElement('div');
    pane.className = 'term__pane';
    $('#termHost').appendChild(pane);
    xterm.open(pane);
    $('#termEmpty').hidden = true;
    pane.classList.add('is-active');
    fit.fit();

    let creada;
    try {
      creada = await window.studio.term.create({ ...opts, cols: xterm.cols, rows: xterm.rows });
    } catch (err) {
      // Orden rechazada por el proceso principal (p. ej. un tema que no existe): sin pestaña huérfana.
      xterm.dispose();
      pane.remove();
      if (!this.tabs.size) $('#termEmpty').hidden = false;
      else this.focus(this.active);
      toast(String(err.message || err).replace(/^Error invoking remote method '[^']+': (Error: )?/, ''));
      return null;
    }
    const { id, titulo } = creada;
    const tab = document.createElement('button');
    tab.className = 'tab';
    tab.innerHTML = `<span>${esc(opts.titulo || titulo)}</span><span class="tab__x" title="Cerrar"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg></span>`;
    tab.addEventListener('click', (e) => (e.target.closest('.tab__x') ? this.close(id) : this.focus(id)));
    $('#termTabs').appendChild(tab);

    xterm.onData((d) => window.studio.term.write(id, d));
    xterm.onResize(({ cols, rows }) => window.studio.term.resize(id, cols, rows));
    // Ctrl+Shift+C / Ctrl+Shift+V como en cualquier terminal de Linux.
    xterm.attachCustomKeyEventHandler((e) => {
      if (e.type === 'keydown' && e.ctrlKey && e.shiftKey && e.code === 'KeyC') {
        navigator.clipboard.writeText(xterm.getSelection());
        return false;
      }
      if (e.type === 'keydown' && e.ctrlKey && e.shiftKey && e.code === 'KeyV') {
        navigator.clipboard.readText().then((t) => window.studio.term.write(id, t));
        return false;
      }
      return !(e.ctrlKey && !e.shiftKey && /^[1-8]$/.test(e.key));
    });

    this.tabs.set(id, { xterm, fit, pane, tab, dead: false });
    this.focus(id);
    return id;
  },

  focus(id) {
    this.active = id;
    for (const [k, t] of this.tabs) {
      t.pane.classList.toggle('is-active', k === id);
      t.tab.classList.toggle('is-active', k === id);
    }
    this.fitActive();
    this.tabs.get(id)?.xterm.focus();
  },

  fitActive() {
    const t = this.tabs.get(this.active);
    if (t && S.view === 'terminal') requestAnimationFrame(() => t.fit.fit());
  },

  close(id) {
    const t = this.tabs.get(id);
    if (!t) return;
    if (!t.dead) window.studio.term.kill(id);
    t.xterm.dispose();
    t.pane.remove();
    t.tab.remove();
    this.tabs.delete(id);
    const next = [...this.tabs.keys()].pop();
    if (next) this.focus(next);
    else {
      this.active = null;
      $('#termEmpty').hidden = false;
    }
  },

  onData(id, data) {
    this.tabs.get(id)?.xterm.write(data);
  },

  onExit(id, code) {
    const t = this.tabs.get(id);
    if (!t) return;
    t.dead = true;
    t.tab.classList.add('is-dead');
    t.xterm.write(`\r\n\x1b[2m[proceso terminado · código ${code}]\x1b[0m\r\n`);
  },
};
window.studio.term.onData((id, d) => Term.onData(id, d));
window.studio.term.onExit((id, c) => Term.onExit(id, c));
new ResizeObserver(() => Term.fitActive()).observe($('#termHost'));

const abrir = {
  shell: () => Term.open({}),
  claude: () => Term.open({ tarea: 'claude' }),
  continue: () => Term.open({ tarea: 'claude-continue' }),
  curso: () => Curso.open(),
};
$('#termShell').addEventListener('click', abrir.shell);
$('#termClaude').addEventListener('click', abrir.claude);
$('#termContinue').addEventListener('click', abrir.continue);
$('#termCurso').addEventListener('click', abrir.curso);
$$('.card-btn').forEach((b) => b.addEventListener('click', () => abrir[b.dataset.act]()));

/* ─── Asistente de nuevo curso ───────────────────────────── */
const Curso = {
  dlg: $('#cursoDlg'),
  form: $('#cursoForm'),

  open() {
    Exports.ensure();
    this.form.reset();
    // Sin esto, cerrar con Esc heredaria el "ok" del envio anterior.
    this.dlg.returnValue = '';
    this.render();
    this.dlg.showModal();
    this.form.elements.tema.focus();
  },

  prompt() {
    const f = Object.fromEntries(new FormData(this.form));
    const formato = f.formato === 'vertical' ? 'vertical 9:16 (piezas sueltas de 30–45 s)' : 'horizontal 16:9 (familia de lecciones de 4 clips)';
    const lineas = [
      'Usa la skill `curso-de-video` para producir un curso completo, de punta a punta, en este repo.',
      '',
      `- Tema: ${f.tema || '(por definir)'}`,
      f.area ? `- Área / familia: ${f.area} (el nombre de cada proyecto sigue la regla «${f.area} · N.M Título» del catálogo)` : '- Área / familia: propón una que encaje con el catálogo de studio/docs/CATALOGO-CURSOS.md',
      `- Formato: ${formato}`,
      `- Estilo: ${f.estilo || 'el de por defecto para este formato'}`,
      `- Sonido: ${f.sonido || 'el de por defecto para este formato'}`,
      f.tamano ? `- Tamaño: ${f.tamano}` : null,
      `- Subtítulos narrativos en pantalla: ${f.subtitulos ? 'sí, los pido' : 'no (formato mudo en pantalla)'}`,
      f.notas ? `\nIndicaciones del dueño:\n${f.notas}` : null,
      '',
      'Antes de escribir código: invoca también la skill `manimstudio`, lee las memorias y documentos que la skill indica, y preséntame el arco del curso (módulos, lecciones y qué capa ocupa frente a los cursos ya publicados) para que lo apruebe. Los videos finales van a exports/ como siempre.',
    ];
    return lineas.filter((l) => l !== null).join('\n');
  },

  render() {
    $('#cursoPreview').textContent = this.prompt();
  },

  async submit() {
    const f = new FormData(this.form);
    const tema = String(f.get('tema') || '').trim();
    await Term.open({ prompt: this.prompt(), modo: f.get('modo'), titulo: `Curso · ${tema.slice(0, 28)}` });
    show('terminal');
  },
};
Curso.form.addEventListener('input', () => Curso.render());
Curso.dlg.addEventListener('close', () => {
  if (Curso.dlg.returnValue === 'ok') Curso.submit();
});

/* ─── Sistema ────────────────────────────────────────────── */
const ESTADOS = {
  stopped: 'detenidos',
  starting: 'arrancando',
  running: 'en marcha',
  external: 'en marcha (externos)',
  error: 'error',
};
const Sistema = {
  logLines: [],

  renderState(s) {
    S.svc = s;
    $('#sysState').textContent = ESTADOS[s.state] || s.state;
    $('#sysState').dataset.state = s.state;
    $('#railStatus .dot').dataset.state = s.state;
    $('#railStatusText').textContent = s.state === 'running' || s.state === 'external' ? 'en línea' : ESTADOS[s.state];
    $('#sysDetail').textContent =
      s.detail ||
      (s.state === 'external'
        ? `Se reutiliza un backend que ya corría en :${s.apiPort} (p. ej. studio/dev.sh). La app no lo detendrá.`
        : 'runner (Docker) + backend FastAPI, como en producción pero en esta máquina.');
    $('#sysStart').disabled = s.state === 'running' || s.state === 'external' || s.state === 'starting';
    $('#sysStop').disabled = !s.owned;
    Estudio.onServices(s);
    if (S.view === 'inicio') Inicio.refresh();
  },

  appendLog(line) {
    const el = $('#sysLog');
    const pegado = el.scrollTop + el.clientHeight >= el.scrollHeight - 8;
    el.textContent += `${line}\n`;
    if (el.textContent.length > 200000) el.textContent = el.textContent.slice(-150000);
    if (pegado) el.scrollTop = el.scrollHeight;
  },

  async refreshInfo() {
    const i = await window.studio.system();
    const ok = (v, txt) => (v ? `<span class="ok">${esc(txt)}</span>` : `<span class="bad">no disponible</span>`);
    $('#sysInfo').innerHTML = `
      <dt>Docker</dt><dd>${ok(i.docker, `v${i.docker}`)}</dd>
      <dt>Imagen de render</dt><dd>${i.imagen ? `<span class="ok">codeaerospace_contenido-manim · ${bytes(i.imagen)}</span>` : '<span class="bad">no construida</span> — Tareas → Construir imagen'}</dd>
      <dt>GPU</dt><dd>${esc(i.gpu || 'sin GPU NVIDIA detectada')}</dd>
      <dt>CPU</dt><dd>${esc(i.cpu)} · ${i.nucleos} hilos</dd>
      <dt>Memoria</dt><dd>${bytes(i.memoria)}</dd>
      <dt>Disco de exports</dt><dd>${i.disco ? `${bytes(i.disco.libre)} libres de ${bytes(i.disco.total)}` : '—'}</dd>
      <dt>Interfaz compilada</dt><dd>${
        !i.uiCompilada
          ? '<span class="bad">no</span> — Tareas → Recompilar interfaz'
          : i.uiFuente > i.uiCompilada
            ? `${new Date(i.uiCompilada).toLocaleString('es-MX')} · <span class="bad">desactualizada</span> — el código cambió después; Tareas → Recompilar interfaz`
            : `<span class="ok">${new Date(i.uiCompilada).toLocaleString('es-MX')} · al día</span>`
      }</dd>
      <dt>Sistema</dt><dd>${esc(i.so)}</dd>`;
  },
};
window.studio.services.onState((s) => Sistema.renderState(s));
window.studio.services.onLog((l) => Sistema.appendLog(l));
$('#sysStart').addEventListener('click', () => window.studio.services.start());
$('#sysStop').addEventListener('click', () => window.studio.services.stop());
$('#sysRestart').addEventListener('click', () => window.studio.services.restart());
$('#sysCheck').addEventListener('click', async () => {
  const out = $('#sysCheckOut');
  out.hidden = false;
  out.textContent = 'verificando…';
  const r = await window.studio.services.check();
  out.textContent = r.output || (r.ok ? 'OK' : 'falló sin salida');
});
$('#sysLogClear').addEventListener('click', () => ($('#sysLog').textContent = ''));
$('#cfgChoose').addEventListener('click', async () => {
  const r = await window.studio.chooseRepo();
  if (r && !r.ok && r.error) toast(r.error);
});
$('#cfgOpenRepo').addEventListener('click', () => window.studio.openRepo());
$('#cfgStopOnQuit').addEventListener('change', (e) => window.studio.setConfig({ stopServicesOnQuit: e.target.checked }));

/* ─── Utilidades de repo y exports ───────────────────────── */
// El catalogo de presentaciones da rutas relativas al REPO; las de exports/ se sirven por /__media.
const enExports = (rel) => (rel && rel.startsWith('exports/') ? rel.slice('exports/'.length) : null);
const media = (rel) => (enExports(rel) ? Exports.mediaUrl(enExports(rel)) : '');
async function abrirRel(rel) {
  const r = await window.studio.repo.open(rel);
  if (r && !r.ok) toast(r.error);
}
const mostrarRel = (rel) => window.studio.repo.reveal(rel);
async function copiarRel(rel) {
  toast(`Copiado: ${await window.studio.repo.copyPath(rel)}`);
}
function tarea(opts) {
  show('terminal');
  return Term.open(opts);
}

/** Markdown de los guiones → HTML. Escapa TODO primero; solo reconoce lo que usan los guiones:
 *  #/##, citas >, tablas |, listas -, **negrita**, *cursiva*, `código` y párrafos. */
function md(texto) {
  const inline = (t) =>
    esc(t)
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/(^|[^*])\*([^*\s][^*]*?)\*/g, '$1<em>$2</em>');
  const out = [];
  const lineas = String(texto).replace(/\r/g, '').split('\n');
  for (let i = 0; i < lineas.length; i++) {
    const l = lineas[i];
    if (/^\s*$/.test(l)) continue;
    let m;
    if ((m = /^(#{1,3})\s+(.*)$/.exec(l))) out.push(`<h${m[1].length}>${inline(m[2])}</h${m[1].length}>`);
    else if (l.startsWith('>')) {
      const bloque = [];
      while (i < lineas.length && lineas[i].startsWith('>')) bloque.push(lineas[i++].replace(/^>\s?/, ''));
      i--;
      out.push(`<blockquote>${bloque.map(inline).join('<br>')}</blockquote>`);
    } else if (l.startsWith('|')) {
      const filas = [];
      while (i < lineas.length && lineas[i].startsWith('|')) filas.push(lineas[i++]);
      i--;
      const celdas = (f) => f.replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
      const cuerpo = filas.filter((f) => !/^\|[\s:|-]+\|$/.test(f));
      out.push(`<div class="guion__tabla"><table>${cuerpo
        .map((f, k) => `<tr>${celdas(f).map((c) => (k === 0 ? `<th>${inline(c)}</th>` : `<td>${inline(c)}</td>`)).join('')}</tr>`)
        .join('')}</table></div>`);
    } else if (/^\s*[-*]\s+/.test(l)) {
      const items = [];
      while (i < lineas.length && /^\s*[-*]\s+/.test(lineas[i])) items.push(lineas[i++].replace(/^\s*[-*]\s+/, ''));
      i--;
      out.push(`<ul>${items.map((x) => `<li>${inline(x)}</li>`).join('')}</ul>`);
    } else out.push(`<p>${inline(l)}</p>`);
  }
  return out.join('\n');
}

/* ─── Inicio ─────────────────────────────────────────────── */
const Inicio = {
  async refresh() {
    $('#inicioRepo').textContent = S.info?.repo ? ` · ${S.info.repo}` : '';
    const chips = [];
    const st = S.svc.state;
    const vivo = st === 'running' || st === 'external';
    chips.push(`<span class="chip ${vivo ? 'chip--ok' : st === 'error' ? 'chip--err' : 'chip--warn'}">Estudio ${esc(ESTADOS[st] || st)}</span>`);
    if (Pres.cat?.ok) {
      const decks = Pres.cat.presentaciones.reduce((n, p) => n + p.decks.length, 0);
      chips.push(`<span class="chip chip--accent">${Pres.cat.presentaciones.length} presentaciones · ${decks} decks · ${Pres.cat.temas.length} temas</span>`);
    }
    if (Marca.cat) chips.push(`<span class="chip">${Marca.cat.animaciones.length} animaciones de marca</span>`);
    $('#inicioEstado').innerHTML = chips.join('');
    if (!Pres.cat) Pres.ensure().then(() => S.view === 'inicio' && this.refresh());
    if (!Marca.cat) Marca.ensure(false, false).then(() => S.view === 'inicio' && this.refresh());
  },
};
$$('.acceso').forEach((b) =>
  b.addEventListener('click', () => {
    const ir = b.dataset.ir;
    if (ir === 'editor') Pres.editor();
    else if (ir === 'curso') {
      show('terminal');
      Curso.open();
    } else show(ir);
  })
);

/* ─── Presentaciones (animaciones/: decks con temas) ─────── */
const Pres = {
  cat: null,
  sel: null,
  tab: 'lista',
  carga: null,

  async ensure(refresh = false) {
    if (this.cat && !refresh) return this.render();
    if (!S.info?.repo) return;
    if (!this.carga) {
      $('#presResumen').textContent = 'leyendo animaciones/…';
      this.carga = window.studio.pres.catalog(refresh).finally(() => (this.carga = null));
    }
    this.cat = await this.carga;
    this.render();
  },

  tema(id) {
    return this.cat.temas.find((t) => t.id === id);
  },

  render() {
    const c = this.cat;
    if (!c) return;
    if (!c.ok) {
      $('#presMain').innerHTML = `<div class="aviso-caja aviso-caja--err"><b>No se pudo leer el catálogo de presentaciones.</b><pre class="check">${esc(c.error)}</pre></div>`;
      $('#presResumen').textContent = '';
      return;
    }
    const decks = c.presentaciones.reduce((n, p) => n + p.decks.length, 0);
    $('#presResumen').textContent = `${c.presentaciones.length} presentaciones · ${decks} decks · ${c.temas.length} temas`;
    if (!this.sel || !c.presentaciones.some((p) => p.id === this.sel)) this.sel = c.presentaciones[0]?.id;
    $('#presItems').innerHTML = c.presentaciones
      .map(
        (p) => `<li><button class="pitem ${p.id === this.sel ? 'is-active' : ''}" data-id="${esc(p.id)}">
          <b>${esc(p.titulo)}</b>
          <small>${p.diapositivas} diap. · ${p.minutos} min · ${p.decks.length} decks${p.propia ? ' · propia' : ''}${p.errores.length ? ' · ⚠ errores' : ''}</small>
        </button></li>`
      )
      .join('');
    $$('#presItems .pitem').forEach((b) =>
      b.addEventListener('click', () => {
        this.sel = b.dataset.id;
        this.render();
      })
    );
    this.renderDetalle();
    this.renderTemas();
  },

  renderDetalle() {
    const p = this.cat.presentaciones.find((x) => x.id === this.sel);
    const host = $('#presMain');
    if (!p) {
      host.innerHTML = '<p class="vacio">No hay presentaciones todavía. Crea una con «Nueva presentación».</p>';
      return;
    }
    const porTema = new Map();
    for (const d of p.decks) porTema.set(`${d.tema}·${d.idioma}`, d);
    const tarjetas = [...porTema.values()]
      .sort((a, b) => (a.tema === this.cat.oficial ? -1 : b.tema === this.cat.oficial ? 1 : a.tema.localeCompare(b.tema)))
      .map((d) => {
        const t = this.tema(d.tema) || { nombre: d.tema, color: {} };
        return `<article class="deck">
          <div class="deck__img" data-abrir="${esc(d.hoja || d.pptx)}" style="background-image:url('${esc(media(d.hoja))}')" title="Hoja de contactos"></div>
          <div class="deck__pie">
            <div class="deck__tit"><span class="sw" style="background:${esc(t.color.acento || '#888')}"></span>${esc(t.nombre)}${d.idioma === 'en' ? ' <span class="chip">EN</span>' : ''}<small>${fecha(d.fecha)}</small></div>
            <div class="deck__btns">
              <button class="btn btn--sm" data-abrir="${esc(d.pptx)}">PPTX</button>
              ${d.pdf ? `<button class="btn btn--ghost btn--sm" data-abrir="${esc(d.pdf)}">PDF</button>` : ''}
              <button class="btn btn--ghost btn--sm" data-mostrar="${esc(d.pptx)}">Carpeta</button>
              <button class="btn btn--ghost btn--sm" data-reconstruir="${esc(d.tema)}" data-idioma="${esc(d.idioma)}" title="Volver a construir en este tema">↻</button>
            </div>
          </div>
        </article>`;
      })
      .join('');
    const errores = p.errores.length
      ? `<div class="aviso-caja aviso-caja--err"><b>${p.errores.length} errores</b> — no se puede construir hasta corregirlos:<ul>${p.errores.map((e) => `<li>${esc(e)}</li>`).join('')}</ul></div>`
      : '';
    const avisos = p.avisos.length
      ? `<details class="aviso-caja"><summary>${p.avisos.length} avisos de diseño</summary><ul>${p.avisos.map((e) => `<li>${esc(e)}</li>`).join('')}</ul></details>`
      : '';
    host.innerHTML = `
      <header class="pres__head">
        <div>
          <p class="eyebrow">${p.propia ? 'Presentación propia' : 'Incluida'} · ${esc(p.id)}</p>
          <h1>${esc(p.titulo)}</h1>
          <div class="pres__meta">
            <span class="chip">${p.diapositivas} diapositivas</span>
            <span class="chip">${p.minutos} min de guion</span>
            <span class="chip">${p.idiomas.map((x) => x.toUpperCase()).join(' · ')}</span>
            <span class="chip ${p.decks.length ? 'chip--ok' : 'chip--warn'}">${p.decks.length ? `${p.decks.length} decks construidos` : 'sin construir'}</span>
          </div>
        </div>
        <div class="pres__acciones">
          <button class="btn btn--accent" id="pConstruir" ${p.errores.length ? 'disabled' : ''}>Construir…</button>
          <button class="btn" id="pGuion" ${p.guion ? '' : 'disabled title="Se escribe al construir"'}>Guion</button>
          ${p.propia ? '<button class="btn btn--ghost" id="pEditar">Editar</button><button class="btn btn--ghost" id="pValidar">Validar y probar</button>' : '<button class="btn btn--ghost" disabled title="Las incluidas se editan en su módulo .py de animaciones/">Editar</button>'}
          ${p.json ? '<button class="btn btn--ghost" id="pJson">JSON</button>' : ''}
        </div>
      </header>
      ${errores}${avisos}
      <p class="seccion-tit">Decks por tema</p>
      ${tarjetas ? `<div class="decks">${tarjetas}</div>` : '<p class="vacio">Todavía no se construye en ningún tema. «Construir…» lo hace en la Terminal (≈1 min por tema).</p>'}`;
    $('#pConstruir')?.addEventListener('click', () => Construir.open(p));
    $('#pGuion')?.addEventListener('click', () => Guion.open(p));
    $('#pEditar')?.addEventListener('click', () => this.editor(p.id));
    $('#pValidar')?.addEventListener('click', () => tarea({ validar: p.id }));
    $('#pJson')?.addEventListener('click', () => mostrarRel(p.json));
    $$('[data-abrir]', host).forEach((b) => b.addEventListener('click', () => abrirRel(b.dataset.abrir)));
    $$('[data-mostrar]', host).forEach((b) => b.addEventListener('click', () => mostrarRel(b.dataset.mostrar)));
    $$('[data-reconstruir]', host).forEach((b) =>
      b.addEventListener('click', () => tarea({ construir: { deck: p.id, temas: [b.dataset.reconstruir], idioma: b.dataset.idioma } }))
    );
  },

  renderTemas() {
    const usados = new Map();
    for (const p of this.cat.presentaciones) for (const d of p.decks) usados.set(d.tema, (usados.get(d.tema) || 0) + 1);
    $('#temasGrid').innerHTML = this.cat.temas
      .map(
        (t) => `<article class="tema-card">
          <div class="tema-card__img" style="background-image:url('${esc(media(t.vista))}')">${t.oficial ? '<span class="chip chip--accent">oficial</span>' : ''}</div>
          <div class="tema-card__cuerpo">
            <b>${esc(t.nombre)}</b>
            <p>${esc(t.descripcion)}</p>
            <div class="sw-fila">${Object.entries(t.color)
              .map(([k, v]) => `<span class="sw" title="${esc(k)} ${esc(v)}" style="background:${esc(v)}"></span>`)
              .join('')}</div>
            <span class="tema-card__fuentes">${esc([...new Set(Object.values(t.fuentes))].join(' · '))} · ${t.modo} · ${usados.get(t.id) || 0} decks</span>
          </div>
        </article>`
      )
      .join('');
  },

  setTab(tab) {
    this.tab = tab;
    $$('[data-pres-tab]').forEach((b) => b.classList.toggle('is-active', b.dataset.presTab === tab));
    $('#presLista').hidden = tab !== 'lista';
    $('#presTemas').hidden = tab !== 'temas';
  },

  async editor(deck) {
    try {
      await window.studio.pres.editor(deck || null);
      toast('Abriendo el editor de presentaciones…');
    } catch (err) {
      toast(`No se pudo abrir el editor: ${err.message}`);
    }
  },
};
$$('[data-pres-tab]').forEach((b) => b.addEventListener('click', () => Pres.setTab(b.dataset.presTab)));
$('#presRefrescar').addEventListener('click', () => Pres.ensure(true));
$('#presNueva').addEventListener('click', () => Pres.editor());
$('#presFuentes').addEventListener('click', () => tarea({ tarea: 'fuentes' }));
$('#presPruebas').addEventListener('click', () => tarea({ tarea: 'pres-pruebas' }));

const Construir = {
  dlg: $('#construirDlg'),
  p: null,

  open(p) {
    this.p = p;
    $('#construirTitulo').textContent = `Construir «${p.titulo}»`;
    const hechos = new Set(p.decks.map((d) => d.tema));
    $('#construirTemas').innerHTML = Pres.cat.temas
      .map(
        (t) => `<label title="${esc(t.descripcion)}"><input type="checkbox" value="${esc(t.id)}" ${t.oficial ? 'checked' : ''}>
          <span class="sw" style="background:${esc(t.color.acento)}"></span>${esc(t.nombre)}${hechos.has(t.id) ? ' <small class="muted">✓</small>' : ''}</label>`
      )
      .join('');
    $('#construirIdioma').innerHTML = p.idiomas.map((x) => `<option value="${x}">${x === 'en' ? 'Inglés' : 'Español'}</option>`).join('');
    $('#construirIdiomaCampo').hidden = p.idiomas.length < 2;
    this.dlg.returnValue = '';
    this.render();
    this.dlg.showModal();
  },

  orden() {
    const temas = $$('#construirTemas input:checked').map((i) => i.value);
    return { deck: this.p.id, temas, idioma: $('#construirIdioma').value || this.p.idiomas[0] };
  },

  render() {
    const o = this.orden();
    $('#construirOrden').textContent = o.temas.length
      ? `python3 animaciones/decks_espaciales.py ${o.temas.join(' ')} ${o.deck}${o.idioma === 'en' ? ' --en' : ''}\n≈ ${o.temas.length} min · PPTX + PDF + hoja de contactos por tema`
      : 'Elige al menos un tema.';
    $('#construirDlg [value=ok]').disabled = !o.temas.length;
  },
};
$('#construirForm').addEventListener('change', () => Construir.render());
$('#construirTodos').addEventListener('click', () => {
  $$('#construirTemas input').forEach((i) => (i.checked = true));
  Construir.render();
});
$('#construirNinguno').addEventListener('click', () => {
  $$('#construirTemas input').forEach((i) => (i.checked = false));
  Construir.render();
});
Construir.dlg.addEventListener('close', () => {
  if (Construir.dlg.returnValue === 'ok') tarea({ construir: Construir.orden() });
});

const Guion = {
  dlg: $('#guionDlg'),
  rel: null,
  async open(p) {
    this.rel = p.guion;
    $('#guionTitulo').textContent = p.titulo;
    $('#guionCuerpo').innerHTML = '<p class="muted">Leyendo…</p>';
    this.dlg.showModal();
    try {
      $('#guionCuerpo').innerHTML = md(await window.studio.pres.guion(p.guion));
    } catch (err) {
      $('#guionCuerpo').innerHTML = `<p class="bad">${esc(err.message)}</p>`;
    }
  },
};
$('#guionCerrar').addEventListener('click', () => Guion.dlg.close());
$('#guionAbrir').addEventListener('click', () => Guion.rel && abrirRel(Guion.rel));

/* ─── Marca (marca/ + exports/marca-codeaerospace) ───────── */
const LIBRERIAS = {
  'marca_aerospace.py': 'El logo como VGroup por partes (órbitas, luna, satélite, CO.DE, AEROSPACE) y sus entradas: orbital, trazo, ensamble, sting y salida.',
  'estelas.py': 'Dibujar con cometa, recorrer con estela, destellos y remuestreo por longitud de arco. Genérica: órbitas, enlaces, logos.',
  'rotulos_aerospace.py': 'Tarjeta de título, tercio inferior, capítulo, cortinilla orbital y cierre de marca, en Montserrat y plata.',
};
const Marca = {
  cat: null,

  async ensure(refresh = false, pintar = true) {
    if (!this.cat || refresh) this.cat = await window.studio.marca();
    if (pintar) this.render();
  },

  render() {
    const c = this.cat;
    const host = $('#marcaBody');
    if (!c) {
      host.innerHTML = '<p class="vacio">Configura el repositorio en Sistema.</p>';
      return;
    }
    const logos = c.logos
      .map(
        (l) => `<article class="logo-card">
          <div class="logo-card__img" data-fondo="${l.fondo}"><img alt="${esc(l.nombre)}" src="${esc(l.url)}"></div>
          <div class="logo-card__pie"><b>${esc(l.nombre)}</b><small>${esc(l.uso)}</small>
            <div class="deck__btns">
              <button class="btn btn--sm" data-abrir="${esc(l.archivo)}">Abrir</button>
              <button class="btn btn--ghost btn--sm" data-mostrar="${esc(l.archivo)}">Carpeta</button>
              <button class="btn btn--ghost btn--sm" data-copiar="${esc(l.archivo)}">Copiar ruta</button>
            </div></div>
        </article>`
      )
      .join('');
    const paleta = (c.paleta?.colores || [])
      .map(
        (k) => `<button class="color" data-hex="${esc(k.hex)}" title="Copiar ${esc(k.hex)}">
          <span class="color__sw" style="background:${esc(k.hex)}"></span>
          <span class="color__info"><b>${esc(k.nombre)}</b><code>${esc(k.hex)}</code><small>${esc(k.uso)}</small></span>
        </button>`
      )
      .join('');
    const anims = c.animaciones.length
      ? c.animaciones
          .map(
            (a) => `<article class="anim">
              <video preload="metadata" muted loop playsinline src="${esc(Exports.mediaUrl(a.archivo))}"></video>
              <div class="anim__pie"><b>${esc(a.nombre)}</b><small>${bytes(a.bytes)}</small>
                <button class="icon-btn" data-abrir="exports/${esc(a.archivo)}" title="Abrir"><svg viewBox="0 0 24 24"><path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6"/></svg></button></div>
            </article>`
          )
          .join('')
      : '<p class="vacio">Aún no hay animaciones renderizadas: «Renderizar animaciones» las genera en exports/marca-codeaerospace (≈ 10 min).</p>';
    const libs = c.librerias
      .map((f) => `<div class="lib"><code>${esc(f)}</code><p>${esc(LIBRERIAS[f] || '')}</p></div>`)
      .join('');
    host.innerHTML = `
      <div class="marca__intro">
        <p>El logo vectorial sale del PNG oficial (<code>marca/vectorizar_logo.py</code>, coincide en un 99 % con el original). La misma geometría alimenta los SVG, el ícono de esta app y la librería Manim que anima el logo. La paleta es <code>marca/paleta.json</code>.</p>
      </div>
      <section><h2>Logos</h2></section><div class="logos">${logos}</div>
      <section><h2>Paleta</h2><p class="muted">Clic en un color para copiar su HEX.</p></section><div class="paleta">${paleta}</div>
      <section><h2>Logo animado</h2><p class="muted">Pasa el cursor sobre un video para reproducirlo. Escenas en <code>studio/content/animations/experimentacion/30-logo-co-de-aerospace.py</code>.</p></section>
      <div class="anims">${anims}</div>
      <section><h2>Librerías Manim</h2><p class="muted">En <code>studio/content/manim_extensions/</code>, con su sonda en <code>studio/tools/sonda_marca.py</code>.</p></section>
      <div class="libs">${libs}</div>`;
    $$('[data-abrir]', host).forEach((b) => b.addEventListener('click', () => abrirRel(b.dataset.abrir)));
    $$('[data-mostrar]', host).forEach((b) => b.addEventListener('click', () => mostrarRel(b.dataset.mostrar)));
    $$('[data-copiar]', host).forEach((b) => b.addEventListener('click', () => copiarRel(b.dataset.copiar)));
    $$('.color', host).forEach((b) =>
      b.addEventListener('click', async () => {
        await window.studio.copiar(b.dataset.hex);
        toast(`Copiado: ${b.dataset.hex}`);
      })
    );
    $$('.anim video', host).forEach((v) => {
      v.addEventListener('mouseenter', () => v.play().catch(() => {}));
      v.addEventListener('mouseleave', () => v.pause());
    });
  },
};
$('#marcaRender').addEventListener('click', () => tarea({ tarea: 'marca-render' }));
$('#marcaSonda').addEventListener('click', () => tarea({ tarea: 'marca-sonda' }));
$('#marcaCarpeta').addEventListener('click', () => mostrarRel('marca/vectorizar_logo.py'));

/* ─── Contenido (./codeae: carruseles y reels) ───────────── */
// Todo se hace con `./codeae`: la lista sale de `piezas --json`; las acciones se abren en una pestaña de la
// Terminal (log en vivo). El proceso principal valida subcomando e ids; aquí solo se arman las órdenes.
const Contenido = {
  datos: null, // { piezas, estado }
  sel: new Set(), // ids marcados
  actual: null, // id de la pieza abierta
  filtro: '',
  tipo: '',
  estadoF: '',
  carga: null,

  async ensure(refresh = false) {
    if (this.datos && !refresh) return this.render();
    if (!S.info?.repo) return;
    if (!this.carga) {
      $('#estResumen').textContent = 'leyendo ./codeae piezas…';
      this.carga = window.studio.estudio.piezas().finally(() => (this.carga = null));
    }
    const r = await this.carga;
    if (!r.ok) {
      this.datos = null;
      $('#estResumen').textContent = '';
      $('#estMain').innerHTML = `<div class="aviso-caja aviso-caja--err"><b>No se pudo leer ./codeae piezas.</b><pre class="check">${esc(r.error)}</pre></div>`;
      return;
    }
    this.datos = r;
    this.render();
  },

  pieza(id) {
    return this.datos?.piezas.find((p) => p.id === id);
  },

  visibles() {
    const f = this.filtro.trim().toLowerCase();
    return this.datos.piezas.filter((p) => {
      if (this.tipo && p.tipo !== this.tipo) return false;
      if (this.estadoF === 'hechas' && !p.renderizado) return false;
      if (this.estadoF === 'faltan' && p.renderizado) return false;
      return !f || `${p.id} ${p.grupo} ${p.detalle} ${p.tipo}`.toLowerCase().includes(f);
    });
  },

  /** A qué se aplican las acciones: lo marcado o, si no hay marcas, la pieza abierta. */
  objetivo() {
    const ids = this.sel.size ? [...this.sel] : this.actual ? [this.actual] : [];
    return ids.filter((i) => this.pieza(i));
  },

  render() {
    const d = this.datos;
    if (!d) return;
    const hechas = d.piezas.filter((p) => p.renderizado).length;
    $('#estResumen').textContent = `${d.piezas.length} piezas · ${hechas} renderizadas · ${d.estado.paquetes.length} paquetes`;
    const lista = this.visibles();
    const grupos = new Map();
    for (const p of [...lista].sort((a, b) => `${a.tipo}|${a.grupo}|${a.id}`.localeCompare(`${b.tipo}|${b.grupo}|${b.id}`))) {
      const k = `${p.tipo} · ${p.grupo}`;
      if (!grupos.has(k)) grupos.set(k, []);
      grupos.get(k).push(p);
    }
    $('#estItems').innerHTML = lista.length
      ? [...grupos]
          .map(
            ([k, ps]) => `<div class="est__grupo">${esc(k)} <span class="muted">(${ps.length})</span></div>` +
              ps
                .map(
                  (p) => `<div class="est__item ${p.id === this.actual ? 'is-active' : ''}" data-id="${esc(p.id)}" title="${esc(p.detalle)}">
                    <input type="checkbox" ${this.sel.has(p.id) ? 'checked' : ''} aria-label="Seleccionar ${esc(p.id)}">
                    <b>${esc(p.id)}</b>
                    ${p.estado === 'no_publicar' ? '<span class="est__no" title="Marcada como no publicar">⛔</span>' : ''}
                    <span class="${p.renderizado ? 'est__hecho' : 'muted'}" title="${p.renderizado ? 'Renderizada' : 'Sin renderizar'}">${p.renderizado ? '✓' : '·'}</span>
                  </div>`
                )
                .join('')
          )
          .join('')
      : '<p class="vacio">Ninguna pieza coincide.</p>';
    $$('#estItems .est__item').forEach((el) =>
      el.addEventListener('click', (e) => {
        const id = el.dataset.id;
        if (e.target.matches('input')) {
          e.target.checked ? this.sel.add(id) : this.sel.delete(id);
          this.panel();
          return;
        }
        this.actual = id;
        this.render();
      })
    );
    this.panel();
  },

  async panel() {
    const host = $('#estMain');
    const p = this.pieza(this.actual);
    const objetivo = this.objetivo();
    const videos = objetivo.filter((i) => this.pieza(i).tipo === 'video').length;
    const n = objetivo.length;
    const sobre = this.sel.size ? `${this.sel.size} marcadas` : p ? 'esta pieza' : 'nada seleccionado';
    host.innerHTML = `
      <div class="est__sel">
        <b>Acciones sobre ${esc(sobre)}</b>
        <button class="btn btn--accent btn--sm" data-act="render" ${n ? '' : 'disabled'}>Renderizar</button>
        <button class="btn btn--sm" data-act="verificar" ${videos ? '' : 'disabled'} title="Loops y costura de audio de los videos">Verificar loops</button>
        <button class="btn btn--sm" data-act="validar" ${n ? '' : 'disabled'}>Validar</button>
        <span class="bar__spacer"></span>
        <button class="btn btn--ghost btn--sm" data-act="todas">Marcar visibles</button>
        <button class="btn btn--ghost btn--sm" data-act="ninguna" ${this.sel.size ? '' : 'disabled'}>Quitar marcas</button>
      </div>
      ${
        p
          ? `<div class="pres__head"><div><p class="eyebrow">${esc(p.tipo)} · ${esc(p.grupo)}</p><h1>${esc(p.id)}</h1>
              <div class="pres__meta"><span class="chip">${esc(p.detalle)}</span>
              <span class="chip ${p.renderizado ? 'chip--ok' : 'chip--warn'}">${p.renderizado ? '✓ renderizada' : 'sin renderizar'}</span>
              ${p.estado === 'no_publicar' ? '<span class="chip chip--err">⛔ no publicar</span>' : ''}</div></div></div>
            <div class="est__preview" id="estPreview"><span class="muted">Leyendo vista previa…</span></div>`
          : '<p class="vacio">Elige una pieza de la lista para ver su vista previa.</p>'
      }`;
    $$('[data-act]', host).forEach((b) => b.addEventListener('click', () => this.accion(b.dataset.act)));
    if (p) {
      const id = p.id;
      let r = null;
      try {
        r = await window.studio.estudio.preview({ tipo: p.tipo, id: p.id, grupo: p.grupo });
      } catch (err) {
        r = { error: String(err.message || err) };
      }
      const el = $('#estPreview');
      if (!el || this.actual !== id) return; // ya cambió la pieza
      if (r?.rel) {
        const url = Exports.mediaUrl(r.rel);
        el.innerHTML =
          r.kind === 'video'
            ? `<video controls loop preload="metadata" src="${esc(url)}"></video>`
            : `<img alt="Hoja de contacto de ${esc(id)}" src="${esc(url)}">`;
      } else el.innerHTML = `<span class="muted">${r?.error ? esc(r.error) : 'Aún sin renderizar: usa «Renderizar».'}</span>`;
    }
  },

  accion(act) {
    if (act === 'todas') this.visibles().forEach((p) => this.sel.add(p.id));
    else if (act === 'ninguna') this.sel.clear();
    if (act === 'todas' || act === 'ninguna') return this.render();
    const ids = this.objetivo();
    if (!ids.length) return toast('Elige una pieza');
    this.correr({ cmd: act, ids: act === 'verificar' ? ids.filter((i) => this.pieza(i).tipo === 'video') : ids });
  },

  correr(spec) {
    // La terminal muestra el log en vivo; al volver a la vista se relee el estado (✓).
    return Promise.resolve(tarea({ estudio: spec })).then((id) => {
      this.datos = null; // se vuelve a leer al regresar a esta vista
      return id;
    });
  },
};
$('#estFiltro').addEventListener('input', (e) => {
  Contenido.filtro = e.target.value;
  if (Contenido.datos) Contenido.render();
});
$$('[data-est-tipo]').forEach((b) =>
  b.addEventListener('click', () => {
    Contenido.tipo = b.dataset.estTipo;
    $$('[data-est-tipo]').forEach((x) => x.classList.toggle('is-active', x === b));
    if (Contenido.datos) Contenido.render();
  })
);
$$('[data-est-estado]').forEach((b) =>
  b.addEventListener('click', () => {
    Contenido.estadoF = b.dataset.estEstado;
    $$('[data-est-estado]').forEach((x) => x.classList.toggle('is-active', x === b));
    if (Contenido.datos) Contenido.render();
  })
);
$('#estRefrescar').addEventListener('click', () => Contenido.ensure(true));
$('#estIndice').addEventListener('click', () => Contenido.correr({ cmd: 'indice' }));

/* Crear paquete de entrega */
const Paquete = {
  dlg: $('#estPaqueteDlg'),
  ids: [],
  open() {
    this.ids = Contenido.objetivo();
    if (!this.ids.length) return toast('Marca las piezas del paquete (o abre una)');
    $('#estPaqueteTitulo').textContent = `Crear paquete con ${this.ids.length} pieza${this.ids.length === 1 ? '' : 's'}`;
    $('#estPaqueteNombre').value = new Date().toISOString().slice(0, 10);
    this.dlg.returnValue = '';
    this.render();
    this.dlg.showModal();
  },
  render() {
    $('#estPaqueteOrden').textContent = `./codeae paquete ${this.ids.slice(0, 6).join(' ')}${this.ids.length > 6 ? ` … (+${this.ids.length - 6})` : ''} --nombre ${$('#estPaqueteNombre').value}\nLos ⛔ no publicar se omiten solos.`;
  },
};
$('#estPaquete').addEventListener('click', () => Paquete.open());
$('#estPaqueteNombre').addEventListener('input', () => Paquete.render());
Paquete.dlg.addEventListener('close', () => {
  if (Paquete.dlg.returnValue !== 'ok') return;
  const nombre = $('#estPaqueteNombre').value.trim();
  Contenido.correr({ cmd: 'paquete', ids: Paquete.ids, nombre });
});

/* Subir a Drive: la lista sale de `subir PAQUETE` (no sube nada); subir exige este diálogo. */
const Subir = {
  dlg: $('#estSubirDlg'),
  sel: $('#estSubirPaquete'),
  listado: null, // { paquete, n, token }

  async open() {
    this.listado = null;
    $('#estSubirOk').disabled = true;
    $('#estSubirOk').textContent = 'Subir';
    $('#estSubirTitulo').textContent = 'Subir a Drive';
    $('#estSubirLista').textContent = 'Leyendo paquetes…';
    this.dlg.returnValue = '';
    this.dlg.showModal();
    await Contenido.ensure(true);
    const paquetes = Contenido.datos?.estado.paquetes || [];
    this.sel.innerHTML = paquetes.map((p) => `<option value="${esc(p)}">${esc(p)}</option>`).join('');
    if (!paquetes.length) {
      $('#estSubirLista').textContent = 'No hay paquetes. Marca piezas y usa «Crear paquete» primero.';
      return;
    }
    this.listar();
  },

  async listar() {
    const paquete = this.sel.value;
    this.listado = null;
    $('#estSubirOk').disabled = true;
    $('#estSubirLista').textContent = 'Listando (no se sube nada)…';
    const r = await window.studio.estudio.subirListar(paquete);
    if (this.sel.value !== paquete) return; // eligió otro mientras tanto
    if (!r.ok || !r.n) {
      $('#estSubirLista').textContent = r.ok ? 'El paquete está vacío.' : r.error;
      return;
    }
    this.listado = r;
    $('#estSubirTitulo').textContent = `¿Subir ${r.n} archivo${r.n === 1 ? '' : 's'} a Drive?`;
    $('#estSubirLista').textContent = `${r.texto.replace(/\nNo se subió nada\..*$/s, '').trim()}\n\nNo se sube nada hasta que confirmes con el botón.`;
    $('#estSubirOk').textContent = `Subir ${r.n} archivo${r.n === 1 ? '' : 's'}`;
    $('#estSubirOk').disabled = false;
  },
};
$('#estSubir').addEventListener('click', () => Subir.open());
Subir.sel.addEventListener('change', () => Subir.listar());
Subir.dlg.addEventListener('close', () => {
  // Solo el botón «Subir N archivos» (returnValue 'ok') llega aquí; Esc y Cancelar no suben.
  if (Subir.dlg.returnValue !== 'ok' || !Subir.listado) return;
  const { paquete, token } = Subir.listado;
  Subir.listado = null;
  Contenido.correr({ cmd: 'subir', paquete, token });
});

/* ─── Arranque ───────────────────────────────────────────── */
(async function boot() {
  S.info = await window.studio.info();
  const i = S.info;
  $('#cfgRepo').textContent = i.repo || 'sin configurar';
  $('#cfgExports').textContent = i.exportsDir || '—';
  $('#cfgRuntime').textContent =
    i.runtime.mode === 'wsl' ? `WSL2 · ${i.runtime.distro} · ${i.runtime.linuxRepo || '?'}` : 'nativo (Linux)';
  $('#cfgStopOnQuit').checked = i.stopServicesOnQuit;
  $('#termRepo').textContent = i.repo || '—';

  const tareas = ['ui-build', 'docker-build', 'check', 'inventario', 'tests', 'git'];
  $('#sysTasks').innerHTML = tareas.map((k) => `<button class="btn btn--ghost" data-tarea="${k}">${esc(i.tareas[k])}</button>`).join('');
  $$('#sysTasks [data-tarea]').forEach((b) =>
    b.addEventListener('click', () => {
      show('terminal');
      Term.open({ tarea: b.dataset.tarea });
    })
  );

  // La foto del registro ya incluye las lineas que llegaron por evento antes
  // de que respondiera: se reemplaza, no se suma.
  const st = await window.studio.services.status();
  $('#sysLog').textContent = st.log.map((l) => `${l}\n`).join('');
  Sistema.renderState(st);
  if (!i.repo) show('sistema');
  else show('inicio');
})();
