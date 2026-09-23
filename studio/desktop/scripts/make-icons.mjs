// Genera los iconos de la app a partir de build/icon.svg:
//   build/icon.png        512 px (ventana y Linux)
//   build/icons/NxN.png   juego de tamaños que usa electron-builder en Linux
//   build/icon.ico        Windows (entradas PNG de 16 a 256 px)
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const dir = path.join(import.meta.dirname, '..', 'build');
const svg = fs.readFileSync(path.join(dir, 'icon.svg'));
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
console.log('iconos generados en', dir);
