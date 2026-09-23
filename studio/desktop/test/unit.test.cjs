// npm test   (sin Electron: solo la logica pura y el servidor local)
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const http = require('node:http');

const { catalogar, listar, partirNombre, compararNumero, elegirEntrega } = require('../src/exports.cjs');
const { createLocalServer, jail } = require('../src/localServer.cjs');
const { uncToLinux } = require('../src/config.cjs');

function write(file, content = 'x') {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, content);
}

/** Repo minimo: dos cursos de un area, uno suelto sin curso.json, colecciones. */
function fixture() {
  const repo = fs.mkdtempSync(path.join(os.tmpdir(), 'code-studio-'));
  const cursos = path.join(repo, 'studio', 'content', 'cursos');
  write(path.join(cursos, 'aero-2-1-choque', 'curso.json'), JSON.stringify({ name: 'Aerodinámica · 2.1 El choque' }));
  write(path.join(cursos, 'aero-1-10-mach', 'curso.json'), JSON.stringify({ name: 'Aerodinámica · 1.10 Mach' }));
  write(path.join(cursos, 'aero-1-2-termo', 'curso.json'), JSON.stringify({ name: 'Aerodinámica · 1.2 Termo' }));
  write(path.join(repo, 'studio', 'content', 'verticales', 'calculo', 'curso.json'), JSON.stringify({ name: 'Cálculo visible' }));

  const ex = path.join(repo, 'exports');
  write(path.join(ex, 'aero-2-1-choque', '001-a.mp4'), 'a'.repeat(50));
  write(path.join(ex, 'aero-2-1-choque', 'curso_narrado.mp4'), 'b'.repeat(10));
  write(path.join(ex, 'aero-1-10-mach', 'curso_narrado.mp4'));
  write(path.join(ex, 'aero-1-2-termo', 'con_audio', 'curso_narrado.mp4'));
  write(path.join(ex, 'huerfano-sin-json', 'x.mp4'));
  write(path.join(ex, 'verticales', 'calculo', 'calculo_vertical.mp4'));
  write(path.join(ex, 'verticales', 'calculo', 'piezas', '01.mp4'));
  write(path.join(ex, 'sfx', 'blip.wav'));
  write(path.join(ex, 'inventario', 'manifest.tsv'));
  write(path.join(ex, 'mux.sh'));
  return { repo, ex };
}

test('partirNombre separa area, numero y titulo', () => {
  assert.deepEqual(partirNombre('Aerodinámica · 1.2 Repaso de termo'), {
    area: 'Aerodinámica',
    numero: [1, 2],
    titulo: 'Repaso de termo',
  });
  assert.deepEqual(partirNombre('Comunicaciones · 4 Apuntar a un satélite'), {
    area: 'Comunicaciones',
    numero: [4],
    titulo: 'Apuntar a un satélite',
  });
  assert.deepEqual(partirNombre('Promo · El efecto mariposa').numero, []);
  assert.equal(partirNombre('Sin separador').area, null);
});

test('compararNumero ordena numericamente, no como texto', () => {
  const l = [[1, 10], [2, 1], [1, 2]].sort(compararNumero);
  assert.deepEqual(l, [[1, 2], [1, 10], [2, 1]]);
});

test('elegirEntrega prefiere el curso narrado al video mas pesado', () => {
  const v = (rel, size, depth = 0) => ({ rel, size, depth });
  assert.equal(elegirEntrega([v('001.mp4', 99), v('curso_narrado.mp4', 1)]), 'curso_narrado.mp4');
  assert.equal(elegirEntrega([v('x_vertical_sin_voz.mp4', 9), v('x_vertical.mp4', 1)]), 'x_vertical.mp4');
  assert.equal(elegirEntrega([v('a.mp4', 1), v('b.mp4', 5)]), 'b.mp4');
  assert.equal(elegirEntrega([]), null);
});

test('catalogar agrupa por tema y proyecto, con colecciones aparte', async () => {
  const { repo, ex } = fixture();
  const cat = await catalogar(repo, ex);
  const ids = cat.temas.map((t) => t.id);
  assert.equal(ids[0], 'area:Aerodinámica', 'las areas van primero');
  assert.equal(ids.at(-1), 'sin-catalogo', '"Sin catalogo" va al final');
  assert.ok(!ids.some((id) => id.includes('inventario')), 'inventario/ no es un tema');

  const aero = cat.temas[0];
  assert.deepEqual(
    aero.proyectos.map((p) => p.etiqueta),
    ['1.2', '1.10', '2.1'],
    '1.10 va despues de 1.2'
  );
  assert.equal(aero.proyectos[2].entrega, 'curso_narrado.mp4');
  assert.equal(aero.proyectos[0].entrega, 'con_audio/curso_narrado.mp4');
  assert.equal(aero.proyectos[2].bytes, 60);

  const vert = cat.temas.find((t) => t.id === 'col:verticales');
  assert.equal(vert.proyectos[0].nombre, 'Cálculo visible');
  assert.equal(vert.proyectos[0].entrega, 'calculo_vertical.mp4');
  assert.equal(cat.temas.find((t) => t.id === 'sin-catalogo').proyectos[0].id, 'huerfano-sin-json');
  assert.ok(cat.temas.find((t) => t.id === 'col:bancos'));
});

test('listar no sale de exports/', async () => {
  const { ex } = fixture();
  const items = await listar(ex, 'aero-2-1-choque');
  assert.equal(items[0].tipo, 'video');
  await assert.rejects(() => listar(ex, '../studio'), /fuera de exports/);
});

test('jail rechaza escapes por .. y por enlace simbolico', () => {
  const { repo, ex } = fixture();
  assert.ok(jail(ex, 'sfx/blip.wav'));
  assert.equal(jail(ex, '../studio/content'), null);
  fs.symlinkSync(path.join(repo, 'studio'), path.join(ex, 'fuga'));
  assert.equal(jail(ex, 'fuga/content'), null);
});

test('servidor local: token, Range, proxy caido y SPA', async () => {
  const { repo, ex } = fixture();
  const dist = path.join(repo, 'dist');
  write(path.join(dist, 'index.html'), '<h1>spa</h1>');
  write(path.join(ex, 'v.mp4'), '0123456789');
  const srv = createLocalServer({ getDist: () => dist, getExports: () => ex, apiPort: () => 1 });
  const port = await srv.listen(0);
  const get = (p, headers = {}) =>
    new Promise((resolve) =>
      http.get({ host: '127.0.0.1', port, path: p, headers }, (res) => {
        let body = '';
        res.on('data', (c) => (body += c));
        res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body }));
      })
    );
  try {
    assert.equal((await get('/__media/v.mp4')).status, 403);
    const r = await get(`/__media/v.mp4?t=${srv.token}`, { Range: 'bytes=2-4' });
    assert.equal(r.status, 206);
    assert.equal(r.body, '234');
    assert.equal(r.headers['content-range'], 'bytes 2-4/10');
    assert.equal((await get(`/__media/..%2Fdist%2Findex.html?t=${srv.token}`)).status, 404);
    assert.equal((await get('/api/health')).status, 502);
    assert.equal((await get('/%E0%A4%A')).status, 400);
    assert.equal((await get(`/__media/v.mp4?t=${srv.token}`)).status, 200, 'sigue vivo tras la URL rota');
    assert.match((await get('/proyectos/abc')).body, /spa/);
  } finally {
    srv.close();
  }
});

test('uncToLinux traduce rutas de WSL', () => {
  assert.deepEqual(uncToLinux('\\\\wsl.localhost\\Ubuntu\\home\\alan\\repo'), {
    distro: 'Ubuntu',
    path: '/home/alan/repo',
  });
  assert.deepEqual(uncToLinux('\\\\wsl$\\Ubuntu-24.04\\home\\a'), { distro: 'Ubuntu-24.04', path: '/home/a' });
  assert.equal(uncToLinux('C:\\Users\\alan'), null);
});
