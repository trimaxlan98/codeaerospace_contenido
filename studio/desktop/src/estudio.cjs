// Estudio de contenido: la app como frente de la CLI unica `./codeae` (studio/tools/codeae.py).
//
// La app NO reimplementa nada: lista piezas con `codeae piezas --json` y lanza el resto de
// subcomandos en una pestaña de la Terminal. Reglas de seguridad:
//   - lista BLANCA de subcomandos y de banderas por subcomando;
//   - ids/nombres con /^[A-Za-z0-9][A-Za-z0-9._-]*$/ (el primer caracter no puede ser «-»: nada de banderas);
//   - los procesos que lanza el proceso principal usan execFile con arreglo de argumentos (sin shell);
//     la linea para la Terminal solo se arma con argumentos ya validados;
//   - `subir` NUNCA lleva --confirmo salvo que antes se listara ese paquete y la app (con su dialogo
//     «¿Subir N archivos a Drive?») pidiera confirmar: la lista entrega un token de un solo uso;
//   - la vista previa solo resuelve archivos dentro de exports/estudio y exports/marca-codeaerospace.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execFile } = require('node:child_process');

// Estricto: [A-Za-z0-9._-]+ y sin «-» al inicio (evita que un id pase como bandera).
const ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$/;

// subcomando -> { ids: 'ninguno' | 'opcional' | 'requerido', flags: banderas booleanas permitidas }
const SUBCOMANDOS = {
  piezas: { ids: 'ninguno', flags: ['json'] },
  estado: { ids: 'ninguno', flags: ['json'] },
  validar: { ids: 'opcional', flags: ['todo'] },
  render: { ids: 'requerido', flags: ['sinAudio', 'png'] },
  audio: { ids: 'requerido', flags: [] },
  verificar: { ids: 'opcional', flags: ['todo', 'pruebas'] },
  indice: { ids: 'ninguno', flags: [] },
  paquete: { ids: 'requerido', flags: [], nombre: true },
  subir: { ids: 'ninguno', flags: [], paquete: true },
};
const BANDERA = { json: '--json', todo: '--todo', sinAudio: '--sin-audio', png: '--png', pruebas: '--pruebas' };

// Dentro de exports/ (la app ya sirve exports/ con token): solo estas dos carpetas se previsualizan.
const RAICES_PREVIEW = ['estudio', 'marca-codeaerospace'];

function idValido(x) {
  return typeof x === 'string' && ID.test(x);
}

/**
 * spec -> arreglo de argumentos para `codeae`. Lanza Error ante cualquier cosa fuera de la lista blanca.
 *   { cmd, ids?, nombre?, paquete?, <banderas> }
 * `confirmado` solo lo pasan las funciones de este modulo tras validar el token de `subir`.
 */
function argsCodeae(spec, confirmado = false) {
  const s = spec || {};
  const def = Object.prototype.hasOwnProperty.call(SUBCOMANDOS, s.cmd) ? SUBCOMANDOS[s.cmd] : null;
  if (!def) throw new Error(`Subcomando no permitido: ${String(s.cmd).slice(0, 30)}`);
  const args = [s.cmd];
  const ids = [...new Set(s.ids || [])];
  if (def.ids === 'ninguno' && ids.length) throw new Error(`${s.cmd} no recibe piezas`);
  if (def.ids === 'requerido' && !ids.length) throw new Error('Elige al menos una pieza');
  for (const i of ids) {
    if (!idValido(i)) throw new Error(`Id no válido: ${String(i).slice(0, 40)}`);
    args.push(i);
  }
  if (def.paquete) {
    if (!idValido(s.paquete)) throw new Error('Nombre de paquete no válido');
    args.push(s.paquete);
  }
  for (const f of def.flags) if (s[f]) args.push(BANDERA[f]);
  if (def.nombre && s.nombre != null && s.nombre !== '') {
    if (!idValido(s.nombre)) throw new Error('Nombre de paquete no válido');
    args.push('--nombre', s.nombre);
  }
  if (s.cmd === 'subir' && confirmado === true) args.push('--confirmo');
  return args;
}

/** Tokens de un solo uso: un listado de `subir` autoriza UNA subida de ese paquete, durante `ttl` ms. */
class Autorizaciones {
  constructor(ttl = 10 * 60 * 1000, ahora = Date.now) {
    this.ttl = ttl;
    this.ahora = ahora;
    this.map = new Map(); // token -> { paquete, n, vence }
  }

  emitir(paquete, n) {
    const token = crypto.randomBytes(16).toString('hex');
    this.map.set(token, { paquete, n, vence: this.ahora() + this.ttl });
    return token;
  }

  consumir(paquete, token) {
    const a = this.map.get(String(token));
    this.map.delete(String(token));
    return !!a && a.paquete === paquete && a.n > 0 && a.vence >= this.ahora();
  }
}

const q = (a) => `'${String(a).replace(/'/g, `'\\''`)}'`;

/**
 * Linea de bash para la Terminal (render, verificar, paquete...). `subir` solo con token valido.
 * Devuelve { orden, titulo }.
 */
function ordenTerminal(spec, auth) {
  let confirmado = false;
  if (spec?.cmd === 'subir' && spec.token != null) {
    if (!idValido(spec.paquete) || !auth || !auth.consumir(spec.paquete, spec.token)) {
      throw new Error('La subida no está confirmada: lista el paquete y confirma de nuevo.');
    }
    confirmado = true;
  }
  const args = argsCodeae(spec, confirmado);
  const n = args.filter((a, i) => i > 0 && !a.startsWith('--') && args[i - 1] !== '--nombre').length;
  const titulo = `codeae · ${spec.cmd}${confirmado ? ' --confirmo' : ''}${n === 1 ? ` · ${args[1]}` : n > 1 ? ` · ${n} piezas` : ''}`;
  return { orden: ['./codeae', ...args].map((a, i) => (i === 0 ? a : q(a))).join(' '), titulo };
}

/** Ejecuta `python3 codeae <args>` en el repo (nativo o WSL), sin shell. Resuelve { code, stdout, stderr }. */
function codeae(config, args, timeout = 120000) {
  const rt = config.get('runtime');
  const [file, argv, cwd] =
    rt.mode === 'wsl'
      ? ['wsl.exe', ['-d', rt.distro, '--cd', rt.linuxRepo, '--', 'python3', 'codeae', ...args], undefined]
      : ['python3', ['codeae', ...args], config.get('repoPath')];
  return new Promise((resolve) => {
    execFile(file, argv, { cwd, timeout, maxBuffer: 32 * 1024 * 1024, windowsHide: true, encoding: 'utf8' }, (err, stdout, stderr) =>
      resolve({ code: err ? (typeof err.code === 'number' ? err.code : 1) : 0, stdout: String(stdout || ''), stderr: String(stderr || '') })
    );
  });
}

async function json(config, spec) {
  const r = await codeae(config, argsCodeae({ ...spec, json: true }));
  if (r.code !== 0) throw new Error(r.stderr.trim().split('\n').slice(-6).join('\n') || `codeae terminó con código ${r.code}`);
  return JSON.parse(r.stdout);
}

const piezas = (config) => json(config, { cmd: 'piezas' });
const estado = (config) => json(config, { cmd: 'estado' });

/** `codeae subir PAQUETE` (SIN --confirmo): solo lista. Si hay archivos entrega un token para confirmar. */
async function subirListar(config, paquete, auth) {
  const r = await codeae(config, argsCodeae({ cmd: 'subir', paquete }, false));
  if (r.code !== 0) return { ok: false, error: (r.stderr || r.stdout).trim().split('\n').slice(-4).join('\n') };
  const m = /Se subirían (\d+) archivos \(([\d.]+) MB\)/.exec(r.stdout);
  const n = m ? Number(m[1]) : 0;
  return { ok: true, paquete, n, mb: m ? Number(m[2]) : 0, texto: r.stdout, token: n > 0 ? auth.emitir(paquete, n) : null };
}

/** Busca `con_sonido/<id>.mp4` bajo las raices (sin entrar a carruseles/, que tiene miles de PNG). */
function buscarVideo(base, id) {
  const walk = (dir, prof) => {
    let ents;
    try {
      ents = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return null;
    }
    const hit = ents.find((e) => e.isFile() && e.name === `${id}.mp4` && path.basename(dir) === 'con_sonido');
    if (hit) return path.join(dir, hit.name);
    if (prof >= 5) return null;
    for (const e of ents) {
      if (e.isDirectory() && e.name !== 'carruseles' && e.name !== 'paquetes') {
        const r = walk(path.join(dir, e.name), prof + 1);
        if (r) return r;
      }
    }
    return null;
  };
  return walk(base, 0);
}

/**
 * Vista previa de una pieza: { kind: 'imagen' | 'video', rel } con `rel` relativo a exports/
 * (la app lo sirve con su token), o null si aun no esta renderizada. Comprueba que el real
 * (sin enlaces) quede dentro de exports/estudio o exports/marca-codeaerospace.
 */
function previewRel(repo, { tipo, id, grupo }) {
  if (!idValido(id)) throw new Error('Id no válido');
  const exp = fs.realpathSync(path.join(repo, 'exports'));
  let cand = null;
  let kind;
  if (tipo === 'carrusel') {
    if (!idValido(grupo)) throw new Error('Serie no válida');
    cand = path.join(exp, 'estudio', 'carruseles', grupo, id, `${id}_hoja.jpg`);
    kind = 'imagen';
  } else if (tipo === 'video') {
    kind = 'video';
    for (const r of RAICES_PREVIEW) {
      cand = buscarVideo(path.join(exp, r), id);
      if (cand) break;
    }
  } else throw new Error('Tipo no válido');
  if (!cand || !fs.existsSync(cand)) return null;
  const real = fs.realpathSync(cand);
  const dentro = RAICES_PREVIEW.some((r) => {
    let raiz;
    try {
      raiz = fs.realpathSync(path.join(exp, r));
    } catch {
      return false;
    }
    return real.startsWith(raiz + path.sep);
  });
  if (!dentro) throw new Error('Ruta fuera de exports/estudio y exports/marca-codeaerospace');
  return { kind, rel: path.relative(exp, real).split(path.sep).join('/') };
}

module.exports = { ID, SUBCOMANDOS, argsCodeae, idValido, Autorizaciones, ordenTerminal, codeae, piezas, estado, subirListar, previewRel };
