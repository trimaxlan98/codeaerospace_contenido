#!/usr/bin/env node
// Genera los iconos de marca de ManimStudio en studio/frontend/public/.
//
//   cd studio/frontend && node tools/brand_icons.mjs
//
// Vive dentro del paquete del frontend porque node resuelve los imports desde
// la carpeta del propio archivo: en studio/tools/ no encontraria playwright.
//
// Fuente unica de la geometria del glifo CO.DE Academy (teja oscura, "C"
// geometrica, punto ambar): de aqui salen favicon.svg y todos los PNG. La
// version JSX de la misma marca esta en src/components/Brand.jsx — si cambia
// una, cambia la otra.
//
// El rasterizado lo hace el Chromium de Playwright (ya instalado como
// devDependency del frontend): la maquina no tiene rsvg/inkscape/magick y no
// merece la pena añadir dependencias para cuatro PNG que casi nunca cambian.
//
// Trampa del repo: `*.png` esta en .gitignore globalmente. public/*.png tiene
// una excepcion explicita; si se pierde, los iconos no llegan al VPS y en
// produccion falta el favicon (sin error visible en el build).

import { writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const PUBLIC_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'public')

const TILE = '#05070a'      // fondo casi negro de la marca
const INK = '#e8edf3'
const AMBAR = '#f59e0b'
const NARANJA = '#ea580c'

/** El glifo dentro de un viewBox 64x64.
 *  @param rx  radio de la teja (0 = a sangre, para iconos enmascarables)
 *  @param pad margen interior en unidades del viewBox (zona segura de Android) */
function glifo({ rx = 14, pad = 0 } = {}) {
  const e = 64 - 2 * pad // lado util
  const k = e / 64
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <defs>
    <linearGradient id="a" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${AMBAR}"/>
      <stop offset="100%" stop-color="${NARANJA}"/>
    </linearGradient>
  </defs>
  <rect x="${pad ? 0 : 0}" y="0" width="64" height="64" rx="${rx}" fill="${TILE}"/>
  <g transform="translate(${pad} ${pad}) scale(${k})">
    <g stroke="${AMBAR}" stroke-opacity="0.45" stroke-width="2" fill="none" stroke-linecap="round">
      <path d="M8 15V8h7M49 8h7v7M56 49v7h-7M15 56H8v-7"/>
    </g>
    <path d="M35.03 20.53A14 14 0 1 0 35.03 43.47" fill="none" stroke="${INK}"
          stroke-width="8" stroke-linecap="round"/>
    <circle cx="50" cy="43.5" r="5.5" fill="url(#a)"/>
  </g>
</svg>
`
}

// El SVG que sirve de favicon: teja redondeada, glifo a tamaño completo.
const FAVICON = glifo({ rx: 14 })
// Los PNG de sistema operativo van a sangre y con zona segura: iOS y Android
// recortan/enmascaran por su cuenta y las esquinas HUD se perderian.
const FULL_BLEED = glifo({ rx: 0, pad: 8 })

const PNGS = [
  { file: 'favicon-32.png', size: 32, svg: FAVICON },
  { file: 'apple-touch-icon.png', size: 180, svg: FULL_BLEED },
  { file: 'icon-192.png', size: 192, svg: FULL_BLEED },
  { file: 'icon-512.png', size: 512, svg: FULL_BLEED },
]

writeFileSync(join(PUBLIC_DIR, 'favicon.svg'), FAVICON)

const browser = await chromium.launch()
const page = await browser.newPage()
for (const { file, size, svg } of PNGS) {
  await page.setViewportSize({ width: size, height: size })
  await page.setContent(
    `<style>html,body{margin:0;padding:0}svg{display:block;width:${size}px;height:${size}px}</style>${svg}`,
  )
  await page.locator('svg').screenshot({ path: join(PUBLIC_DIR, file), omitBackground: true })
  console.log(`${file} ${size}x${size}`)
}
await browser.close()
console.log('favicon.svg')
