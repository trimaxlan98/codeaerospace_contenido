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

const S = { info: null, view: 'estudio', svc: { state: 'stopped' } };

/* ─── Navegación ─────────────────────────────────────────── */
function show(view) {
  S.view = view;
  $$('.rail__btn').forEach((b) => b.classList.toggle('is-active', b.dataset.view === view));
  $$('.view').forEach((v) => v.classList.toggle('is-active', v.id === `view-${view}`));
  if (view === 'exports') Exports.ensure();
  if (view === 'terminal') Term.fitActive();
  if (view === 'sistema') Sistema.refreshInfo();
}
$$('[data-view]').forEach((b) => b.addEventListener('click', () => show(b.dataset.view)));
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && !e.shiftKey && ['1', '2', '3', '4'].includes(e.key)) {
    show(['estudio', 'exports', 'terminal', 'sistema'][Number(e.key) - 1]);
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
  background: '#05070a',
  foreground: '#e6eaf2',
  cursor: '#00d8f6',
  cursorAccent: '#05070a',
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

    const { id, titulo } = await window.studio.term.create({ ...opts, cols: xterm.cols, rows: xterm.rows });
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
      return !(e.ctrlKey && !e.shiftKey && ['1', '2', '3', '4'].includes(e.key));
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
})();
