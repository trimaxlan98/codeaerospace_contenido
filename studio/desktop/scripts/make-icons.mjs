// Iconos y marca de la app, a partir del logo de Co.De Aerospace (marca/ en la raiz del repo):
//   build/icon.svg        el emblema (logo sin AEROSPACE) en plata sobre una placa #080F15
//   build/icon.png        512 px (ventana y Linux)
//   build/icons/NxN.png   juego de tamaños que usa electron-builder en Linux
//   build/icon.ico        Windows (entradas PNG de 16 a 256 px)
//   renderer/marca/       logo, emblema y Montserrat para la interfaz (van dentro del paquete)
//
// marca/*.svg los genera marca/vectorizar_logo.py desde el PNG oficial: si el logo cambia, se
// vuelve a vectorizar y a correr este script; nada del logo se edita a mano aqui.
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const desk = path.join(import.meta.dirname, '..');
const repo = path.join(desk, '..', '..');
const dir = path.join(desk, 'build');
const marca = path.join(repo, 'marca');
const fuentes = path.join(repo, 'studio', 'content', 'manim_extensions', 'fonts');

// ── Placa con el emblema ────────────────────────────────────────────────────────
const emblema = fs.readFileSync(path.join(marca, 'emblema-codeaerospace.svg'), 'utf-8');
const vb = /viewBox="0 0 ([\d.]+) ([\d.]+)"/.exec(emblema);
const [ew, eh] = [Number(vb[1]), Number(vb[2])];
const cuerpo = emblema.replace(/^[\s\S]*?<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '').replace(/<title>.*?<\/title>/, '');
const lado = 760; // el emblema ocupa ~74 % de la placa: legible a 48 px, con aire en el borde
const k = lado / Math.max(ew, eh);
const tx = 512 - (ew * k) / 2;
const ty = 512 - (eh * k) / 2 + 6;
const icono = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">
  <defs>
    <radialGradient id="placa" cx="0.32" cy="0.22" r="0.95">
      <stop offset="0" stop-color="#14202b"/>
      <stop offset="0.6" stop-color="#080F15"/>
      <stop offset="1" stop-color="#04080c"/>
    </radialGradient>
  </defs>
  <rect x="32" y="32" width="960" height="960" rx="216" fill="url(#placa)"/>
  <rect x="32.5" y="32.5" width="959" height="959" rx="215.5" fill="none" stroke="#ffffff" stroke-opacity="0.09" stroke-width="3"/>
  <g transform="translate(${tx.toFixed(1)} ${ty.toFixed(1)}) scale(${k.toFixed(5)})">${cuerpo}</g>
</svg>
`;
fs.writeFileSync(path.join(dir, 'icon.svg'), icono);

const svg = Buffer.from(icono);
const render = (size) => sharp(svg, { density: Math.max(72, (72 * size) / 1024 * 4) }).resize(size, size).png().toBuffer();

fs.mkdirSync(path.join(dir, 'icons'), { recursive: true });
for (const size of [16, 24, 32, 48, 64, 128, 256, 512, 1024]) {
  fs.writeFileSync(path.join(dir, 'icons', `${size}x${size}.png`), await render(size));
}
fs.writeFileSync(path.join(dir, 'icon.png'), await render(512));

// ICO con PNG embebidos (valido desde Windows Vista).
const sizes = [16, 24, 32, 48, 64, 128, 256];
const pngs = await Promise.all(sizes.map(render));
const header = Buffer.alloc(6);
header.writeUInt16LE(0, 0);
header.writeUInt16LE(1, 2);
header.writeUInt16LE(sizes.length, 4);
let offset = 6 + 16 * sizes.length;
const entries = sizes.map((s, i) => {
  const e = Buffer.alloc(16);
  e.writeUInt8(s >= 256 ? 0 : s, 0);
  e.writeUInt8(s >= 256 ? 0 : s, 1);
  e.writeUInt16LE(1, 4); // planos
  e.writeUInt16LE(32, 6); // bits por pixel
  e.writeUInt32LE(pngs[i].length, 8);
  e.writeUInt32LE(offset, 12);
  offset += pngs[i].length;
  return e;
});
fs.writeFileSync(path.join(dir, 'icon.ico'), Buffer.concat([header, ...entries, ...pngs]));

// ── Marca para la interfaz ──────────────────────────────────────────────────────
const destino = path.join(desk, 'renderer', 'marca');
fs.mkdirSync(destino, { recursive: true });
for (const f of ['logo-codeaerospace.svg', 'emblema-codeaerospace.svg']) {
  fs.copyFileSync(path.join(marca, f), path.join(destino, f));
}
for (const f of ['Montserrat-Regular.ttf', 'Montserrat-Medium.ttf', 'Montserrat-SemiBold.ttf', 'OFL-Montserrat.txt']) {
  fs.copyFileSync(path.join(fuentes, f), path.join(destino, f));
}
console.log('iconos generados en', dir, '· marca copiada a', destino);
