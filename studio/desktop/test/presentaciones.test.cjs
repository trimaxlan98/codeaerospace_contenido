// npm test — presentaciones con temas y kit de marca (src/presentaciones.cjs), sin Electron.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const P = require('../src/presentaciones.cjs');
const { Terminals, TAREAS } = require('../src/terminal.cjs');

const REPO = path.resolve(__dirname, '..', '..', '..');

function write(file, content = 'x') {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, content);
}

test('ordenConstruir arma la línea de decks_espaciales con ids validados', () => {
  assert.equal(
    P.ordenConstruir({ deck: 'que_es_code', temas: ['orbita', 'solar', 'orbita'] }),
    'python3 animaciones/decks_espaciales.py orbita solar que_es_code'
  );
  assert.equal(
    P.ordenConstruir({ deck: 'seminario', temas: ['fisica'], idioma: 'en' }),
    'python3 animaciones/decks_espaciales.py fisica seminario --en'
  );
});

test('ordenConstruir rechaza inyecciones, vacíos y desconocidos', () => {
  const malos = [
    { deck: 'x; rm -rf ~', temas: ['orbita'] },
    { deck: 'que_es_code', temas: ['orbita && curl evil'] },
    { deck: 'que_es_code', temas: ['$(id)'] },
    { deck: 'Que_Es', temas: ['orbita'] },
    { deck: '../x', temas: ['orbita'] },
    { deck: 'que_es_code', temas: [] },
    {},
  ];
  for (const o of malos) assert.throws(() => P.ordenConstruir(o), undefined, JSON.stringify(o));
  const conocidos = { temas: ['orbita'], decks: ['que_es_code'] };
  assert.throws(() => P.ordenConstruir({ deck: 'que_es_code', temas: ['solar'] }, conocidos), /Tema desconocido/);
  assert.throws(() => P.ordenConstruir({ deck: 'otra', temas: ['orbita'] }, conocidos), /Presentación desconocida/);
  assert.doesNotThrow(() => P.ordenConstruir({ deck: 'que_es_code', temas: ['orbita'] }, conocidos));
});

test('ordenValidar solo acepta ids', () => {
  assert.match(P.ordenValidar('que_es_code'), /presentaciones_usuario\.py --validar que_es_code; .*--decks que_es_code$/);
  assert.throws(() => P.ordenValidar('a b'));
  assert.throws(() => P.ordenValidar('`id`'));
});

test('rutaEnRepo solo deja exports/, marca/ y animaciones/presentaciones/', () => {
  const repo = fs.mkdtempSync(path.join(os.tmpdir(), 'code-studio-pres-'));
  write(path.join(repo, 'exports', 'presentaciones', 'a.pptx'));
  write(path.join(repo, 'marca', 'logo.svg'));
  write(path.join(repo, 'animaciones', 'presentaciones', 'p.json'));
  write(path.join(repo, 'studio', 'backend', '.env'), 'SECRETO');
  fs.symlinkSync(path.join(repo, 'studio', 'backend', '.env'), path.join(repo, 'marca', 'atajo'));
  assert.ok(P.rutaEnRepo(repo, 'exports/presentaciones/a.pptx').endsWith('a.pptx'));
  assert.ok(P.rutaEnRepo(repo, 'marca/logo.svg'));
  assert.ok(P.rutaEnRepo(repo, 'animaciones/presentaciones/p.json'));
  assert.throws(() => P.rutaEnRepo(repo, 'studio/backend/.env'));
  assert.throws(() => P.rutaEnRepo(repo, 'marca/../studio/backend/.env'));
  assert.throws(() => P.rutaEnRepo(repo, 'marca/atajo'), /fuera/); // enlace que sale de marca/
  assert.throws(() => P.rutaEnRepo(repo, '/etc/passwd'));
});

test('marca() lista logos, paleta y animaciones del repo', () => {
  const repo = fs.mkdtempSync(path.join(os.tmpdir(), 'code-studio-marca-'));
  write(path.join(repo, 'marca', 'logo-codeaerospace.svg'), '<svg/>');
  write(path.join(repo, 'marca', 'paleta.json'), JSON.stringify({ colores: [{ id: 'cian', hex: '#00D9FF' }] }));
  write(path.join(repo, 'exports', 'marca-codeaerospace', 'LogoCoDeSting.mp4'), 'v');
  write(path.join(repo, 'exports', 'marca-codeaerospace', 'LogoCoDeIntro.mp4'), 'vv');
  write(path.join(repo, 'studio', 'content', 'manim_extensions', 'estelas.py'), '"""x"""');
  const m = P.marca(repo);
  assert.deepEqual(m.logos.map((l) => l.archivo), ['marca/logo-codeaerospace.svg']);
  assert.ok(m.logos[0].url.startsWith('file://'));
  assert.equal(m.paleta.colores[0].hex, '#00D9FF');
  assert.deepEqual(m.animaciones.map((a) => a.escena), ['LogoCoDeIntro', 'LogoCoDeSting']); // orden de ANIMACIONES
  assert.equal(m.animaciones[0].archivo, 'marca-codeaerospace/LogoCoDeIntro.mp4');
  assert.deepEqual(m.librerias, ['estelas.py']);
});

test('el kit de marca del repo real está completo', () => {
  for (const l of P.LOGOS) assert.ok(fs.existsSync(path.join(REPO, l.archivo)), l.archivo);
  const paleta = JSON.parse(fs.readFileSync(path.join(REPO, 'marca', 'paleta.json'), 'utf-8'));
  for (const c of paleta.colores) assert.match(c.hex, /^#[0-9A-F]{6}$/, c.id);
  for (const f of ['logo-codeaerospace.svg', 'emblema-codeaerospace.svg', 'Montserrat-Regular.ttf'])
    assert.ok(fs.existsSync(path.join(__dirname, '..', 'renderer', 'marca', f)), `renderer/marca/${f}`);
});

test('terminal: una orden de main crea su script; el renderer no puede colar `orden`', () => {
  const repo = fs.mkdtempSync(path.join(os.tmpdir(), 'code-studio-term-'));
  const t = new Terminals({ config: { get: (k) => (k === 'repoPath' ? repo : { mode: 'native' }) }, send() {} });
  const rel = t.writeScript('python3 animaciones/decks_espaciales.py orbita que_es_code');
  const cuerpo = fs.readFileSync(path.join(repo, rel), 'utf-8');
  assert.match(cuerpo, /decks_espaciales\.py orbita que_es_code/);
  for (const k of ['pres-pruebas', 'fuentes', 'marca-render', 'marca-sonda', 'marca-vector']) assert.ok(TAREAS[k], k);
  // main.cjs descarta `orden` de lo que llega por IPC antes de llamar a create().
  const main = fs.readFileSync(path.join(__dirname, '..', 'src', 'main.cjs'), 'utf-8');
  assert.match(main, /const \{ orden: _descartada, construir, validar, \.\.\.opts \} = raw/);
});
