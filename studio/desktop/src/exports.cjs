// Catalogo de exports/ por TEMA y PROYECTO.
//
// La vista Entregas de produccion (studio/backend/app/entregas.py) es un
// explorador de carpetas: enseña el arbol tal como esta en disco, donde los
// 170 cursos son hermanos en un mismo nivel. Aqui se clasifican con la misma
// regla que la vista Proyectos (studio/docs/CATALOGO-CURSOS.md): el nombre de
// cada curso es "Area · N Titulo", y la carpeta exports/<slug> coincide con
// el directorio studio/content/cursos/<slug> que guarda ese nombre en su
// curso.json. Asi que:
//
//   tema     = lo que va antes del primer " · "   (Aerodinamica, Comunicaciones...)
//   proyecto = cada curso, ordenado por su numero (1.1, 1.2, 2.1...)
//
// Lo que el propio Estudio produce fuera de los cursos (verticales, promos,
// peliculas, presentaciones, marca, bancos de audio) va en colecciones
// propias. Una carpeta sin curso.json no se pierde: cae en "Sin catalogo".
//
// Solo LEE. No borra, no mueve, no escribe.
const fs = require('node:fs');
const fsp = require('node:fs/promises');
const path = require('node:path');

const COLECCIONES = {
  verticales: { nombre: 'Verticales 9:16', meta: ['studio/content/verticales', 'curso.json'] },
  promos: { nombre: 'Promos de redes', meta: ['studio/content/promos', 'promo.json'] },
  peliculas: { nombre: 'Películas de curso', meta: null },
  presentaciones: { nombre: 'Presentaciones', meta: ['studio/content/presentaciones', null] },
  'marca-intro-y-cierre': { nombre: 'Marca', plano: true },
  musica: { nombre: 'Banco de música', plano: true },
  sfx: { nombre: 'Banco de efectos', plano: true },
};
const IGNORAR = new Set(['inventario']);

const TIPO = {
  video: ['.mp4', '.mov', '.webm', '.mkv'],
  audio: ['.wav', '.mp3', '.m4a', '.flac', '.ogg'],
  imagen: ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'],
  documento: ['.pptx', '.pdf', '.docx', '.zip'],
  texto: ['.txt', '.md', '.json', '.srt', '.csv', '.sh'],
};
function tipoDe(nombre) {
  const ext = path.extname(nombre).toLowerCase();
  for (const [t, exts] of Object.entries(TIPO)) if (exts.includes(ext)) return t;
  return 'otro';
}

function leerJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf-8'));
  } catch {
    return null;
  }
}

/** "Aerodinámica · 1.2 Repaso de..." -> { area, numero: [1,2], titulo } */
function partirNombre(nombre) {
  const i = nombre.indexOf(' · ');
  if (i < 0) return { area: null, numero: [], titulo: nombre };
  const area = nombre.slice(0, i).trim();
  const resto = nombre.slice(i + 3).trim();
  const m = /^(\d+(?:\.\d+)*)\s+(.*)$/.exec(resto);
  return m
    ? { area, numero: m[1].split('.').map(Number), titulo: m[2] }
    : { area, numero: [], titulo: resto };
}

function compararNumero(a, b) {
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    const d = (a[i] ?? -1) - (b[i] ?? -1);
    if (d) return d;
  }
  return 0;
}

/** slug -> nombre legible, leido de los .json de studio/content. */
function cargarCatalogo(repo) {
  const cat = new Map();
  const dir = path.join(repo, 'studio', 'content', 'cursos');
  for (const slug of safeReaddir(dir)) {
    const j = leerJson(path.join(dir, slug, 'curso.json'));
    if (j?.name) cat.set(slug, j.name);
  }
  return cat;
}

function nombreColeccion(repo, clave, slug, carpeta) {
  const c = COLECCIONES[clave];
  if (clave === 'peliculas') {
    return leerJson(path.join(carpeta, 'pelicula.json'))?.proyecto || slug;
  }
  if (c.meta) {
    const [base, archivo] = c.meta;
    if (archivo) {
      const j = leerJson(path.join(repo, base, slug, archivo));
      if (j?.name) return j.name;
    }
  }
  return humanizar(slug);
}

function humanizar(slug) {
  const s = slug.replace(/[-_]+/g, ' ').trim();
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function safeReaddir(dir) {
  try {
    return fs.readdirSync(dir);
  } catch {
    return [];
  }
}

/** Recorre una carpeta: bytes, n.º de archivos, ultima modificacion y la entrega principal. */
async function resumir(carpeta) {
  let bytes = 0;
  let archivos = 0;
  let mtime = 0;
  const videos = [];
  async function walk(dir, rel, depth) {
    let entries;
    try {
      entries = await fsp.readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const e of entries) {
      const full = path.join(dir, e.name);
      const r = rel ? `${rel}/${e.name}` : e.name;
      let st;
      try {
        st = await fsp.stat(full); // stat y no lstat: exports/ vive tras un enlace
      } catch {
        continue;
      }
      if (st.isDirectory()) {
        if (depth < 6) await walk(full, r, depth + 1);
      } else {
        bytes += st.size;
        archivos += 1;
        mtime = Math.max(mtime, st.mtimeMs);
        if (tipoDe(e.name) === 'video') videos.push({ rel: r, size: st.size, depth });
      }
    }
  }
  await walk(carpeta, '', 0);
  return { bytes, archivos, mtime, entrega: elegirEntrega(videos) };
}

// La entrega es el video que se publica, no el clip mas grande: el curso
// narrado si existe, el montaje vertical, la pelicula, y solo como ultimo
// recurso el video mas pesado de la raiz de la carpeta.
function elegirEntrega(videos) {
  const reglas = [
    (v) => /(^|\/)curso_narrado\.mp4$/.test(v.rel),
    (v) => v.depth === 0 && /_vertical\.mp4$/.test(v.rel) && !/sin_voz/.test(v.rel),
    (v) => /(^|\/)pelicula\.mp4$/.test(v.rel),
    (v) => /(^|\/)vertical\.mp4$/.test(v.rel),
  ];
  for (const regla of reglas) {
    const v = videos.find(regla);
    if (v) return v.rel;
  }
  const raiz = videos.filter((v) => v.depth === 0).sort((a, b) => b.size - a.size);
  return raiz[0]?.rel || null;
}

async function catalogar(repo, exportsDir) {
  const cat = cargarCatalogo(repo);
  const temas = new Map(); // id -> { id, nombre, tipo, proyectos: [] }
  const tema = (id, nombre, tipo) => {
    if (!temas.has(id)) temas.set(id, { id, nombre, tipo, proyectos: [] });
    return temas.get(id);
  };

  const trabajos = [];
  for (const nombre of safeReaddir(exportsDir)) {
    const carpeta = path.join(exportsDir, nombre);
    let st;
    try {
      st = fs.statSync(carpeta);
    } catch {
      continue;
    }
    if (!st.isDirectory() || IGNORAR.has(nombre) || nombre.startsWith('.')) continue;

    const col = COLECCIONES[nombre];
    if (col && !col.plano) {
      const t = tema(`col:${nombre}`, col.nombre, 'coleccion');
      for (const slug of safeReaddir(carpeta)) {
        const sub = path.join(carpeta, slug);
        if (!fs.statSync(sub).isDirectory()) continue;
        trabajos.push(
          resumir(sub).then((r) =>
            t.proyectos.push({
              id: `${nombre}/${slug}`,
              rel: `${nombre}/${slug}`,
              nombre: nombreColeccion(repo, nombre, slug, sub),
              numero: [],
              ...r,
            })
          )
        );
      }
      continue;
    }
    if (col?.plano) {
      const t = tema('col:bancos', 'Marca y bancos de audio', 'coleccion');
      trabajos.push(
        resumir(carpeta).then((r) =>
          t.proyectos.push({ id: nombre, rel: nombre, nombre: col.nombre, numero: [], ...r })
        )
      );
      continue;
    }

    const nombreCurso = cat.get(nombre);
    const p = nombreCurso ? partirNombre(nombreCurso) : null;
    const t = p?.area
      ? tema(`area:${p.area}`, p.area, 'area')
      : tema('sin-catalogo', 'Sin catálogo', 'coleccion');
    trabajos.push(
      resumir(carpeta).then((r) =>
        t.proyectos.push({
          id: nombre,
          rel: nombre,
          nombre: p ? p.titulo : humanizar(nombre),
          etiqueta: p?.numero.length ? p.numero.join('.') : null,
          numero: p?.numero || [],
          ...r,
        })
      )
    );
  }
  await Promise.all(trabajos);

  const lista = [...temas.values()];
  for (const t of lista) {
    t.proyectos.sort((a, b) => compararNumero(a.numero, b.numero) || a.nombre.localeCompare(b.nombre, 'es'));
    t.bytes = t.proyectos.reduce((s, p) => s + p.bytes, 0);
    t.archivos = t.proyectos.reduce((s, p) => s + p.archivos, 0);
    t.mtime = Math.max(0, ...t.proyectos.map((p) => p.mtime));
  }
  // Areas primero (alfabetico, como la vista Proyectos), luego colecciones.
  const peso = (t) => (t.tipo === 'area' ? 0 : t.id === 'sin-catalogo' ? 2 : 1);
  lista.sort((a, b) => peso(a) - peso(b) || a.nombre.localeCompare(b.nombre, 'es'));

  return {
    root: exportsDir,
    generado: Date.now(),
    bytes: lista.reduce((s, t) => s + t.bytes, 0),
    archivos: lista.reduce((s, t) => s + t.archivos, 0),
    temas: lista,
  };
}

/** Lista el contenido de una carpeta de exports (un nivel), dentro de la raiz. */
async function listar(exportsDir, rel) {
  const base = fs.realpathSync(exportsDir);
  const dir = path.resolve(base, rel || '.');
  const real = fs.realpathSync(dir);
  if (real !== base && !real.startsWith(base + path.sep)) throw new Error('Ruta fuera de exports');
  const entries = await fsp.readdir(real, { withFileTypes: true });
  const out = [];
  for (const e of entries) {
    if (e.name.startsWith('.')) continue;
    const full = path.join(real, e.name);
    let st;
    try {
      st = await fsp.stat(full);
    } catch {
      continue;
    }
    const r = rel ? `${rel}/${e.name}` : e.name;
    out.push(
      st.isDirectory()
        ? { nombre: e.name, rel: r, dir: true, n: safeReaddir(full).length, mtime: st.mtimeMs }
        : { nombre: e.name, rel: r, dir: false, tipo: tipoDe(e.name), size: st.size, mtime: st.mtimeMs }
    );
  }
  const orden = { video: 0, documento: 1, imagen: 2, audio: 3, texto: 4, otro: 5 };
  out.sort(
    (a, b) =>
      (a.dir === b.dir ? 0 : a.dir ? 1 : -1) ||
      (orden[a.tipo] ?? 9) - (orden[b.tipo] ?? 9) ||
      a.nombre.localeCompare(b.nombre, 'es', { numeric: true })
  );
  return out;
}

module.exports = { catalogar, listar, partirNombre, compararNumero, elegirEntrega, tipoDe };
