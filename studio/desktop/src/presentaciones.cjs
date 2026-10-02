// Presentaciones con temas y kit de marca de Co.De Aerospace.
//
// El sistema de presentaciones vive en animaciones/ (decks_espaciales.py, presentaciones_usuario.py,
// temas_espaciales.py, 18 temas). La app NO lo reimplementa: pide el catalogo a
// animaciones/catalogo_app.py (JSON) y construye con los mismos CLI, en una pestaña de la Terminal.
// El kit de marca es marca/ (logos, paleta.json) + exports/marca-codeaerospace/ (animaciones).
//
// Solo LEE archivos. Lo unico que ejecuta son los scripts del propio repo, con argumentos validados
// contra /^[a-z0-9_]+$/ (ids de tema y de presentacion): nunca texto libre en una linea de comandos.
const fs = require('node:fs');
const path = require('node:path');
const { execFile, spawn } = require('node:child_process');
const { pathToFileURL } = require('node:url');

const ID = /^[a-z0-9][a-z0-9_]{0,40}$/;
// Lo que la app puede abrir o mostrar del repo (fuera de exports/, que tiene su propio jail).
const RAICES = ['exports', 'marca', 'animaciones/presentaciones'];

/** Resuelve `rel` dentro del repo, solo bajo RAICES (sigue enlaces y rechaza escapes). */
function rutaEnRepo(repo, rel) {
  const base = fs.realpathSync(repo);
  const full = fs.realpathSync(path.resolve(base, String(rel || '')));
  const ok = RAICES.some((r) => {
    let raiz;
    try {
      raiz = fs.realpathSync(path.join(base, r));
    } catch {
      return false;
    }
    return full === raiz || full.startsWith(raiz + path.sep);
  });
  if (!ok) throw new Error('Ruta fuera de exports/, marca/ o animaciones/presentaciones/');
  return full;
}

/** Ejecuta `python3 <script> ...args` en el repo (nativo o dentro de WSL). Resuelve stdout. */
function python(config, script, args = [], timeout = 90000) {
  const rt = config.get('runtime');
  const [file, argv, cwd] =
    rt.mode === 'wsl'
      ? ['wsl.exe', ['-d', rt.distro, '--cd', rt.linuxRepo, '--', 'python3', script, ...args], undefined]
      : ['python3', [script, ...args], config.get('repoPath')];
  return new Promise((resolve, reject) => {
    execFile(file, argv, { cwd, timeout, maxBuffer: 32 * 1024 * 1024, windowsHide: true }, (err, stdout, stderr) => {
      if (err) reject(new Error(String(stderr || err.message).trim().split('\n').slice(-6).join('\n')));
      else resolve(String(stdout));
    });
  });
}

async function catalogo(config) {
  const out = await python(config, 'animaciones/catalogo_app.py', ['--validar']);
  return JSON.parse(out);
}

/**
 * Orden de construccion validada -> linea de bash para la Terminal.
 *   { deck: 'que_es_code', temas: ['orbita', 'solar'], idioma: 'es' | 'en' }
 * Lanza Error si algo no es un id valido (no se construye nada a medias).
 */
function ordenConstruir({ deck, temas, idioma } = {}, conocidos = null) {
  if (!ID.test(String(deck || ''))) throw new Error('Presentación no válida');
  const lista = [...new Set((temas || []).map(String))];
  if (!lista.length) throw new Error('Elige al menos un tema');
  for (const t of lista) {
    if (!ID.test(t)) throw new Error(`Tema no válido: ${t}`);
    if (conocidos && !conocidos.temas.includes(t)) throw new Error(`Tema desconocido: ${t}`);
  }
  if (conocidos && !conocidos.decks.includes(deck)) throw new Error(`Presentación desconocida: ${deck}`);
  const en = idioma === 'en' ? ' --en' : '';
  return `python3 animaciones/decks_espaciales.py ${lista.join(' ')} ${deck}${en}`;
}

function ordenValidar(deck) {
  if (!ID.test(String(deck || ''))) throw new Error('Presentación no válida');
  return `python3 animaciones/presentaciones_usuario.py --validar ${deck}; python3 animaciones/pruebas_presentaciones.py --decks ${deck}`;
}

/** Abre el editor PySide6 de presentaciones (app/render_launcher.py), desacoplado de la app. */
function abrirEditor(config, deck) {
  const args = ['app/render_launcher.py', '--pestana', 'nueva'];
  if (deck) {
    if (!ID.test(deck)) throw new Error('Presentación no válida');
    args.push('--abrir', deck);
  }
  const rt = config.get('runtime');
  const [file, argv, cwd] =
    rt.mode === 'wsl'
      ? ['wsl.exe', ['-d', rt.distro, '--cd', rt.linuxRepo, '--', 'python3', ...args], undefined]
      : ['python3', args, config.get('repoPath')];
  const p = spawn(file, argv, { cwd, detached: true, stdio: 'ignore', windowsHide: true });
  p.unref();
  return true;
}

// ── Kit de marca ────────────────────────────────────────────────────────────────

const LOGOS = [
  { archivo: 'marca/logo-codeaerospace.svg', nombre: 'Logo plata', fondo: 'oscuro', uso: 'Fondos oscuros (vector)' },
  { archivo: 'marca/logo-codeaerospace-blanco.svg', nombre: 'Logo blanco', fondo: 'oscuro', uso: 'Una tinta sobre oscuro' },
  { archivo: 'marca/logo-codeaerospace-negro.svg', nombre: 'Logo negro', fondo: 'claro', uso: 'Fondos claros y documentos' },
  { archivo: 'marca/emblema-codeaerospace.svg', nombre: 'Emblema', fondo: 'oscuro', uso: 'Sin AEROSPACE: íconos y avatares' },
  { archivo: 'marca/originales/logo-plata-transparente.png', nombre: 'Original plata (PNG)', fondo: 'oscuro', uso: 'Archivo oficial' },
  { archivo: 'marca/originales/logo-fondo-oscuro.png', nombre: 'Original con fondo (PNG)', fondo: 'oscuro', uso: 'Archivo oficial' },
  { archivo: 'marca/originales/logo-negro-fondo-blanco.png', nombre: 'Original negro (PNG)', fondo: 'claro', uso: 'Archivo oficial' },
];

// Descripcion de cada animacion de exports/marca-codeaerospace (el nombre del archivo es la escena).
const ANIMACIONES = {
  LogoCoDeIntro: 'Entrada orbital · oscuro',
  LogoCoDeIntroClaro: 'Entrada orbital · claro',
  LogoCoDeVertical: 'Entrada orbital · 9:16',
  LogoCoDeTrazo: 'Entrada «trazo»',
  LogoCoDeEnsamble: 'Entrada «ensamble»',
  LogoCoDeSting: 'Sting de 2 s',
  LogoCoDeCierre: 'Cierre con el sitio',
  LogoCoDeMarcaDeAgua: 'Marca de agua sobre contenido',
  RotulosAerospace: 'Rótulos: título, tercio, capítulo y cierre',
};

function marca(repo) {
  const existe = (rel) => fs.existsSync(path.join(repo, rel));
  let paleta = null;
  try {
    paleta = JSON.parse(fs.readFileSync(path.join(repo, 'marca', 'paleta.json'), 'utf-8'));
  } catch {
    /* sin paleta: la vista lo dice */
  }
  const dirAnim = path.join(repo, 'exports', 'marca-codeaerospace');
  let animaciones = [];
  try {
    animaciones = fs
      .readdirSync(dirAnim)
      .filter((f) => f.endsWith('.mp4'))
      .map((f) => {
        const st = fs.statSync(path.join(dirAnim, f));
        const escena = f.replace(/\.mp4$/, '');
        return { archivo: `marca-codeaerospace/${f}`, escena, nombre: ANIMACIONES[escena] || escena, bytes: st.size, fecha: st.mtimeMs };
      })
      .sort((a, b) => Object.keys(ANIMACIONES).indexOf(a.escena) - Object.keys(ANIMACIONES).indexOf(b.escena));
  } catch {
    /* aun no se renderizan */
  }
  return {
    logos: LOGOS.filter((l) => existe(l.archivo)).map((l) => ({ ...l, url: pathToFileURL(path.join(repo, l.archivo)).href })),
    paleta,
    animaciones,
    librerias: ['marca_aerospace.py', 'estelas.py', 'rotulos_aerospace.py'].filter((f) =>
      existe(path.join('studio', 'content', 'manim_extensions', f))
    ),
  };
}

module.exports = { rutaEnRepo, python, catalogo, ordenConstruir, ordenValidar, abrirEditor, marca, ID, LOGOS };
