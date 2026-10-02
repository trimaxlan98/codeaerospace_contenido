// npm test — estudio de contenido (src/estudio.cjs): lista blanca de ./codeae, ids y subida confirmada. Sin Electron.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const E = require('../src/estudio.cjs');

const REPO = path.resolve(__dirname, '..', '..', '..');
const write = (file, c = 'x') => {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, c);
};

test('lista blanca: solo los subcomandos de codeae', () => {
  assert.deepEqual(
    Object.keys(E.SUBCOMANDOS).sort(),
    ['audio', 'estado', 'indice', 'paquete', 'piezas', 'render', 'subir', 'validar', 'verificar']
  );
  for (const cmd of ['rm', 'bash', 'sh', '--help', '__proto__', 'constructor', 'toString', '', undefined, 'Render', 'render; ls'])
    assert.throws(() => E.argsCodeae({ cmd, ids: ['a'] }), /Subcomando no permitido/, String(cmd));
  assert.throws(() => E.argsCodeae(), /Subcomando/);
});

test('argsCodeae arma arreglos de argumentos por subcomando', () => {
  assert.deepEqual(E.argsCodeae({ cmd: 'piezas', json: true }), ['piezas', '--json']);
  assert.deepEqual(E.argsCodeae({ cmd: 'render', ids: ['a', 'b', 'a'], sinAudio: true, png: true }), ['render', 'a', 'b', '--sin-audio', '--png']);
  assert.deepEqual(E.argsCodeae({ cmd: 'verificar', ids: ['LogoCoDeIntro'], pruebas: true }), ['verificar', 'LogoCoDeIntro', '--pruebas']);
  assert.deepEqual(E.argsCodeae({ cmd: 'validar', todo: true }), ['validar', '--todo']);
  assert.deepEqual(E.argsCodeae({ cmd: 'indice' }), ['indice']);
  assert.deepEqual(E.argsCodeae({ cmd: 'paquete', ids: ['x', 'y'], nombre: '2026-10-02' }), ['paquete', 'x', 'y', '--nombre', '2026-10-02']);
  // banderas que el subcomando no admite se ignoran, no se cuelan
  assert.deepEqual(E.argsCodeae({ cmd: 'indice', png: true, pruebas: true, confirmo: true }), ['indice']);
  assert.throws(() => E.argsCodeae({ cmd: 'render', ids: [] }), /al menos una pieza/);
  assert.throws(() => E.argsCodeae({ cmd: 'indice', ids: ['a'] }), /no recibe piezas/);
});

test('ids: solo [A-Za-z0-9._-]+ y nunca una bandera', () => {
  for (const ok of ['cifras-con-fecha-b', 'LogoCoDeIntro', 'a.b_c-d', '2026-10-02', 'x']) assert.ok(E.idValido(ok), ok);
  const malos = ['', ' ', 'a b', 'a;b', 'a&&b', '$(id)', '`id`', 'a|b', 'a>b', '../x', 'a/b', 'serie/id', '--confirmo', '-x', 'a\nb', 'ñ', "a'b", '"', 'a'.repeat(200), null, 5, {}, ['a']];
  for (const m of malos) {
    assert.equal(E.idValido(m), false, JSON.stringify(m));
    assert.throws(() => E.argsCodeae({ cmd: 'render', ids: [m] }), /Id no válido/, JSON.stringify(m));
  }
  assert.throws(() => E.argsCodeae({ cmd: 'paquete', ids: ['a'], nombre: 'x; rm -rf ~' }), /Nombre/);
  assert.throws(() => E.argsCodeae({ cmd: 'paquete', ids: ['a'], nombre: '--confirmo' }), /Nombre/);
  assert.throws(() => E.argsCodeae({ cmd: 'subir', paquete: '../etc' }), /paquete/);
  assert.throws(() => E.argsCodeae({ cmd: 'subir' }), /paquete/);
});

test('subir sin confirmación NUNCA lleva --confirmo', () => {
  assert.deepEqual(E.argsCodeae({ cmd: 'subir', paquete: 'p1' }), ['subir', 'p1']);
  // ni pidiéndolo en el spec (confirmo/confirmado/--confirmo en cualquier campo)
  assert.deepEqual(E.argsCodeae({ cmd: 'subir', paquete: 'p1', confirmo: true, confirmado: true }), ['subir', 'p1']);
  assert.throws(() => E.argsCodeae({ cmd: 'subir', paquete: 'p1', ids: ['--confirmo'] }), /no recibe piezas/);
  const auth = new E.Autorizaciones();
  // sin token: la orden de terminal es la del listado
  assert.equal(E.ordenTerminal({ cmd: 'subir', paquete: 'p1' }, auth).orden, "./codeae 'subir' 'p1'");
  // con un token inventado, de otro paquete o ya usado: rechazada
  assert.throws(() => E.ordenTerminal({ cmd: 'subir', paquete: 'p1', token: 'inventado' }, auth), /no está confirmada/);
  const t = auth.emitir('p1', 3);
  assert.throws(() => E.ordenTerminal({ cmd: 'subir', paquete: 'p2', token: t }, auth), /no está confirmada/);
  const t2 = auth.emitir('p1', 3);
  const ok = E.ordenTerminal({ cmd: 'subir', paquete: 'p1', token: t2 }, auth);
  assert.match(ok.orden, / '--confirmo'$/);
  assert.throws(() => E.ordenTerminal({ cmd: 'subir', paquete: 'p1', token: t2 }, auth), /no está confirmada/); // un solo uso
  assert.throws(() => E.ordenTerminal({ cmd: 'subir', paquete: 'p1', token: 'x' }, null), /no está confirmada/);
});

test('los tokens caducan y un listado vacío no autoriza nada', () => {
  let t = 1000;
  const auth = new E.Autorizaciones(500, () => t);
  const tok = auth.emitir('p', 2);
  t += 501;
  assert.equal(auth.consumir('p', tok), false);
  assert.equal(auth.consumir('p', auth.emitir('p', 0)), false);
});

test('subirListar ejecuta `subir PAQUETE` sin --confirmo y entrega token solo si hay archivos', async () => {
  const repo = fs.mkdtempSync(path.join(os.tmpdir(), 'code-studio-est-'));
  // codeae falso: imprime lo que recibe, como el real al listar
  write(path.join(repo, 'codeae'), [
    'import sys',
    'a = sys.argv[1:]',
    'print(f"Se subirían {0 if a[1] == \'vacio\' else 3} archivos (1.5 MB) a gdrive:x/{a[1]}:")',
    'print("ARGS", a)',
  ].join('\n'));
  const config = { get: (k) => (k === 'repoPath' ? repo : { mode: 'native' }) };
  const auth = new E.Autorizaciones();
  const r = await E.subirListar(config, 'p1', auth);
  assert.equal(r.ok, true);
  assert.equal(r.n, 3);
  assert.match(r.texto, /ARGS \['subir', 'p1'\]/);
  assert.doesNotMatch(r.texto, /confirmo/);
  assert.ok(auth.consumir('p1', r.token));
  const v = await E.subirListar(config, 'vacio', auth);
  assert.equal(v.n, 0);
  assert.equal(v.token, null);
  await assert.rejects(() => E.subirListar(config, 'p; rm -rf ~', auth), /paquete/i);
});

test('previewRel: hoja de contacto del carrusel y mp4 con sonido, solo dentro de exports/estudio y marca', () => {
  const repo = fs.mkdtempSync(path.join(os.tmpdir(), 'code-studio-prev-'));
  write(path.join(repo, 'exports/estudio/carruseles/serie/pieza/pieza_hoja.jpg'));
  write(path.join(repo, 'exports/estudio/logo_vivo/con_sonido/VivoA.mp4'));
  write(path.join(repo, 'exports/marca-codeaerospace/vertical/con_sonido/MarcaV.mp4'));
  write(path.join(repo, 'exports/otro/con_sonido/Fuera.mp4'));
  write(path.join(repo, 'secreto.txt'), 's');
  assert.deepEqual(E.previewRel(repo, { tipo: 'carrusel', id: 'pieza', grupo: 'serie' }), {
    kind: 'imagen',
    rel: 'estudio/carruseles/serie/pieza/pieza_hoja.jpg',
  });
  assert.equal(E.previewRel(repo, { tipo: 'video', id: 'VivoA' }).rel, 'estudio/logo_vivo/con_sonido/VivoA.mp4');
  assert.equal(E.previewRel(repo, { tipo: 'video', id: 'MarcaV' }).rel, 'marca-codeaerospace/vertical/con_sonido/MarcaV.mp4');
  assert.equal(E.previewRel(repo, { tipo: 'video', id: 'Fuera' }), null); // exports/otro no se previsualiza
  assert.equal(E.previewRel(repo, { tipo: 'carrusel', id: 'nada', grupo: 'serie' }), null);
  for (const mal of [
    { tipo: 'carrusel', id: '../../../secreto', grupo: 'serie' },
    { tipo: 'carrusel', id: 'pieza', grupo: '..' },
    { tipo: 'carrusel', id: 'pieza', grupo: '../../..' },
    { tipo: 'video', id: '../x' },
    { tipo: 'otro', id: 'x' },
  ])
    assert.throws(() => E.previewRel(repo, mal), undefined, JSON.stringify(mal));
  // un enlace que sale de exports/estudio se rechaza
  fs.symlinkSync(path.join(repo, 'secreto.txt'), path.join(repo, 'exports/estudio/carruseles/serie/pieza/ln_hoja.jpg'));
  fs.mkdirSync(path.join(repo, 'exports/estudio/carruseles/serie/ln'), { recursive: true });
  fs.symlinkSync(path.join(repo, 'secreto.txt'), path.join(repo, 'exports/estudio/carruseles/serie/ln/ln_hoja.jpg'));
  assert.throws(() => E.previewRel(repo, { tipo: 'carrusel', id: 'ln', grupo: 'serie' }), /fuera/);
});

test('main.cjs: la orden del estudio sale de ordenTerminal y la preview de la lista blanca', () => {
  const main = fs.readFileSync(path.join(__dirname, '..', 'src', 'main.cjs'), 'utf-8');
  assert.match(main, /E\.ordenTerminal\(raw\.estudio, subidas\)/);
  assert.match(main, /new E\.Autorizaciones\(\)/);
  assert.doesNotMatch(main, /--confirmo/); // el proceso principal nunca escribe la bandera a mano
  const app = fs.readFileSync(path.join(__dirname, '..', 'renderer', 'app.js'), 'utf-8');
  assert.doesNotMatch(app, /--confirmo/); // ni el renderer
});

test('con el repo real: piezas --json y estado --json (si hay python3)', async (t) => {
  if (!fs.existsSync(path.join(REPO, 'codeae'))) return t.skip('sin ./codeae');
  const config = { get: (k) => (k === 'repoPath' ? REPO : { mode: 'native' }) };
  let piezas;
  try {
    piezas = await E.piezas(config);
  } catch (e) {
    return t.skip(`codeae no corre aquí: ${e.message.slice(0, 80)}`);
  }
  assert.ok(piezas.length > 0);
  for (const p of piezas) {
    assert.ok(['carrusel', 'video'].includes(p.tipo));
    assert.ok(E.idValido(p.id), p.id);
    assert.ok(E.idValido(p.grupo), p.grupo);
  }
  const est = await E.estado(config);
  assert.ok(Array.isArray(est.paquetes));
});
