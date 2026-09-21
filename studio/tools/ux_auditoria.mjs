#!/usr/bin/env node
// Auditoria automatica de la interfaz de ManimStudio.
//
// Mide EL PIXEL QUE SE PINTA. El metodo del sprint 10 componia el fondo
// subiendo por los ancestros; eso ve los velos apilados, pero no ve un
// degradado (el lienzo lo tiene), ni un `backdrop-filter`, ni una imagen.
// Aqui el fondo real se obtiene de una captura de la propia pagina con TODO
// el texto en `color: transparent`: lo que queda es exactamente el fondo
// sobre el que se pintan las letras, con sus velos, desenfoques y degradados.
//
// En cada combinacion tema x escena x viewport comprueba:
//   - contraste AA de cada nodo de texto visible (4,5:1; 3:1 si es grande),
//   - oclusion: ningun texto visible queda tapado por otro elemento,
//   - desborde horizontal de la pagina,
//   - errores de consola,
//   - anillo de foco visible en cada parada de tabulacion,
//   - overlays: dentro del viewport y cierre con Escape.
//
// Uso (con la app servida en local y una cookie de sesion firmada):
//   node studio/tools/ux_auditoria.mjs \
//     --base http://127.0.0.1:4173 --cookie "$(cat cookie.txt)" \
//     [--temas orbital,daylight] [--vistas estudio,proyectos] \
//     [--overlays paleta,guion|ninguno] [--viewports escritorio,movil] \
//     [--json informe.json] [--capturas dir/] [--con-ornamento]
//
// El instrumento vive en el repo a proposito: cada sprint del rediseno vuelve
// a medir con el mismo criterio (ver studio/docs/UX-AUDITORIA.md).

import { chromium } from '../frontend/node_modules/playwright/index.mjs'
import { mkdirSync, writeFileSync } from 'node:fs'

// ── Argumentos ────────────────────────────────────────────────────────────
const args = Object.fromEntries(
  process.argv.slice(2).flatMap((a, i, all) =>
    a.startsWith('--') ? [[a.slice(2), all[i + 1] && !all[i + 1].startsWith('--') ? all[i + 1] : true]] : []),
)
const BASE = args.base || 'http://127.0.0.1:4173'
const COOKIE = args.cookie || ''
const TEMAS = String(args.temas || 'orbital,ion,nebula,daylight').split(',')
const VIEWPORTS = {
  escritorio: { width: 1440, height: 900 },
  movil: { width: 390, height: 844 },
}
const VP_ELEGIDOS = String(args.viewports || 'escritorio,movil').split(',')

// Las vistas del shell (mas el detalle de un curso, que es una vista propia).
const VISTAS = [
  { id: 'estudio', hash: '#/estudio' },
  { id: 'proyectos', hash: '#/proyectos' },
  { id: 'proyecto-detalle', detalle: 'curso' },
  { id: 'promo-detalle', detalle: 'promo' },
  { id: 'renders', hash: '#/renders' },
  { id: 'biblioteca', hash: '#/biblioteca' },
  { id: 'aprender', hash: '#/aprender' },
  { id: 'laboratorio', hash: '#/laboratorio' },
  { id: 'admin', hash: '#/admin' },
  { id: 'configuracion', hash: '#/configuracion' },
]
const VISTAS_ELEGIDAS = args.vistas ? String(args.vistas).split(',') : VISTAS.map((v) => v.id)

// Overlays: se abren sobre una vista y se miden como una escena mas.
const OVERLAYS = [
  { id: 'paleta', hash: '#/estudio', tecla: 'Control+k' },
  { id: 'atajos', hash: '#/estudio', tecla: '?' },
  { id: 'importar', hash: '#/proyectos', boton: 'Importar…' },
  { id: 'nuevo-proyecto', hash: '#/proyectos', boton: 'Nuevo proyecto' },
  { id: 'estilo', detalle: 'curso', boton: 'Editar estilo' },
  { id: 'duplicar', detalle: 'curso', boton: 'Duplicar proyecto' },
  { id: 'anadir-clip', detalle: 'curso', boton: 'Añadir clip' },
  { id: 'render-lote', detalle: 'curso', boton: 'Render en lote…' },
  { id: 'guion', detalle: 'curso', boton: /^voz/ },
  { id: 'mezcla', detalle: 'curso', boton: /^música/ },
  { id: 'audio-promo', detalle: 'promo', boton: /^voz/ },
  { id: 'a-proyecto', hash: '#/renders', boton: 'A un proyecto…' },
  { id: 'ver-render', hash: '#/renders', boton: 'Ver' },
  { id: 'nueva-seccion', hash: '#/aprender', boton: /^Sección$/ },
]
const OVERLAYS_ELEGIDOS = args.overlays === 'ninguno'
  ? []
  : args.overlays && args.overlays !== true
    ? String(args.overlays).split(',') : OVERLAYS.map((o) => o.id)

// ── Pasada 1: recoger nodos de texto, oclusion y desborde ─────────────────
const RECOGER = (selRaiz) => {
  // Con un overlay modal abierto solo se mide el overlay: lo de detras esta
  // tapado por el velo a proposito.
  const raiz = selRaiz ? document.querySelector(selRaiz) : document.body
  if (!raiz) return { nodos: [], fallos: [{ tipo: 'raiz-no-encontrada', texto: selRaiz }] }

  const px = (v) => parseFloat(v) || 0
  const sel = (el) => (el.tagName.toLowerCase() + (el.className && typeof el.className === 'string'
    ? '.' + el.className.split(/\s+/).filter(Boolean).slice(0, 4).join('.') : '')).slice(0, 120)

  // Rectangulo visible tras aplicar el recorte de todos los ancestros con
  // overflow != visible. Un texto scrolleado fuera de su panel NO esta
  // tapado por nadie: esta recortado, y no se pinta.
  const recorte = (el) => {
    let r = { left: 0, top: 0, right: innerWidth, bottom: innerHeight }
    for (let n = el; n; n = n.parentElement) {
      const cs = getComputedStyle(n)
      if (cs.overflowX === 'visible' && cs.overflowY === 'visible') continue
      const c = n.getBoundingClientRect()
      r = {
        left: Math.max(r.left, c.left), top: Math.max(r.top, c.top),
        right: Math.min(r.right, c.right), bottom: Math.min(r.bottom, c.bottom),
      }
    }
    return r
  }

  const oculto = (el) => {
    for (let n = el, hijo = null; n; hijo = n, n = n.parentElement) {
      if (n.nodeType !== 1) continue
      // Lo plegado dentro de un <details> cerrado no se pinta, pero Chromium
      // le sigue dando caja: el sprint 11 conto como «oclusion» la
      // continuidad de cada clip, que esta plegada. El <summary> si se ve.
      if (n.tagName === 'DETAILS' && !n.open && hijo?.tagName !== 'SUMMARY') return true
      if (n.getAttribute('aria-hidden') === 'true') return true
      if (n.classList.contains('sr-only')) return true
      const cs = getComputedStyle(n)
      if (cs.display === 'none' || cs.visibility === 'hidden' || px(cs.opacity) === 0) return true
    }
    return false
  }

  const fallos = []
  const nodos = []
  const walker = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT)
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (!n.nodeValue.trim()) continue
    const el = n.parentElement
    if (!el || oculto(el)) continue
    const rango = document.createRange()
    rango.selectNodeContents(n)
    const caja = rango.getBoundingClientRect()
    if (caja.width < 1 || caja.height < 2) continue
    if (caja.bottom < 1 || caja.top > innerHeight - 1) continue
    if (caja.right < 1 || caja.left > innerWidth - 1) continue
    // Lo recortado por el scroll de un panel no se pinta: no se mide.
    const vis = recorte(el)
    const dentroDelRecorte = (x, y) => x > vis.left && x < vis.right && y > vis.top && y < vis.bottom
    if (caja.bottom < vis.top + 1 || caja.top > vis.bottom - 1) continue
    if (caja.right < vis.left + 1 || caja.left > vis.right - 1) continue
    // Controles deshabilitados: WCAG 1.4.3 los exceptua del contraste.
    if (el.closest('[disabled], [aria-disabled="true"], [data-disabled]')) continue

    const cs = getComputedStyle(el)
    const tam = px(cs.fontSize)
    const peso = parseInt(cs.fontWeight, 10) || 400
    // Puntos de muestreo dentro de la caja del texto (con el texto en
    // transparente son fondo puro). Cinco a lo ancho; ver MEDIR para por
    // que no se juzga por el peor.
    const dentro = (x, y) => [
      Math.min(Math.max(x, 1), innerWidth - 2),
      Math.min(Math.max(y, 1), innerHeight - 2),
    ]
    const cy = caja.top + caja.height / 2
    const borde = Math.min(6, caja.width / 4)
    const puntos = [
      dentro(caja.left + borde, cy),
      dentro(caja.left + caja.width / 4, cy),
      dentro(caja.left + caja.width / 2, cy),
      dentro(caja.left + (3 * caja.width) / 4, cy),
      dentro(caja.right - borde, cy),
    ]

    nodos.push({
      texto: n.nodeValue.trim().slice(0, 48),
      selector: sel(el),
      color: cs.color,
      tam: Math.round(tam * 10) / 10,
      minimo: tam >= 24 || (tam >= 18.66 && peso >= 700) ? 3 : 4.5,
      puntos,
    })

    // Oclusion: el punto central del texto debe pertenecer al propio texto.
    const [x, y] = puntos[2]
    const arriba = dentroDelRecorte(x, y) ? document.elementFromPoint(x, y) : null
    if (arriba && arriba !== el && !el.contains(arriba) && !arriba.contains(el)) {
      fallos.push({
        tipo: 'oclusion',
        texto: n.nodeValue.trim().slice(0, 48),
        selector: sel(el),
        tapadoPor: sel(arriba),
      })
    }
  }

  const desborde = document.documentElement.scrollWidth - document.documentElement.clientWidth
  if (desborde > 1) {
    const culpables = [...document.querySelectorAll('body *')]
      .map((e) => ({ e, r: e.getBoundingClientRect() }))
      .filter(({ r }) => r.right > innerWidth + 1 && r.width > 0 && r.height > 0)
      .slice(0, 3)
      .map(({ e, r }) => `${sel(e)} (+${Math.round(r.right - innerWidth)}px)`)
    fallos.push({ tipo: 'desborde', px: desborde, culpables })
  }

  return { nodos, fallos }
}

// ── Pasada 2: leer el fondo pintado de la captura y juzgar el contraste ───
const MEDIR = async ({ nodos, captura }) => {
  const img = new Image()
  img.src = 'data:image/png;base64,' + captura
  await img.decode()
  const lienzo = document.createElement('canvas')
  lienzo.width = img.width
  lienzo.height = img.height
  const ctx = lienzo.getContext('2d', { willReadFrequently: true })
  ctx.drawImage(img, 0, 0)
  const escala = img.width / innerWidth // por si el viewport no es 1:1
  const datos = ctx.getImageData(0, 0, img.width, img.height).data

  // El color declarado puede venir en cualquier formato de CSS Color 4
  // (`oklab(...)`, `color-mix(...)`): que lo resuelva el propio navegador
  // pintandolo. Parsear la cadena a mano daba negro y falsos 1,1:1.
  const tinta = document.createElement('canvas').getContext('2d', { willReadFrequently: true })
  const cache = new Map()
  const parseColor = (c) => {
    if (cache.has(c)) return cache.get(c)
    tinta.clearRect(0, 0, 1, 1)
    tinta.fillStyle = '#000'
    tinta.fillStyle = c
    tinta.fillRect(0, 0, 1, 1)
    const d = tinta.getImageData(0, 0, 1, 1).data
    const v = [d[0], d[1], d[2], d[3] / 255]
    cache.set(c, v)
    return v
  }
  const sobre = (fg, bg) => [0, 1, 2].map((i) => fg[i] * fg[3] + bg[i] * (1 - fg[3]))
  const lum = ([r, g, b]) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4 }
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
  }
  const ratio = (a, b) => {
    const [l1, l2] = [lum(a), lum(b)].sort((x, y) => y - x)
    return (l1 + 0.05) / (l2 + 0.05)
  }
  const pixel = (x, y) => {
    const cx = Math.round(x * escala)
    const cy = Math.round(y * escala)
    const i = (cy * img.width + cx) * 4
    return [datos[i], datos[i + 1], datos[i + 2]]
  }

  const fallos = []
  for (const n of nodos) {
    const fgDecl = parseColor(n.color)
    // Se juzga por el SEGUNDO peor de cinco puntos. El fondo animado dibuja
    // estrellas de 2 px y enlaces de 1 px que se ven a traves del vidrio: el
    // sprint 11 conto una veintena de «fallos» que eran una estrella debajo
    // de una letra en ese fotograma (fondos rgb(14,88,104), rgb(129,50,143)).
    // Un fondo REAL —un chip, un velo, un degradado— cubre la caja entera y
    // hunde los cinco puntos a la vez, asi que tolerar uno no lo esconde.
    const medidas = n.puntos
      .map(([x, y]) => { const bg = pixel(x, y); return { c: ratio(sobre(fgDecl, bg), bg), bg } })
      .sort((a, b) => a.c - b.c)
    const peor = medidas[Math.min(1, medidas.length - 1)]
    if (peor.c < n.minimo - 0.005) {
      fallos.push({
        tipo: 'contraste',
        texto: n.texto,
        selector: n.selector,
        ratio: Math.round(peor.c * 100) / 100,
        minimo: n.minimo,
        color: n.color,
        fondo: `rgb(${peor.bg.join(',')})`,
        tam: n.tam,
      })
    }
  }
  return fallos
}

// Recorrido de tabulacion: cada parada debe tener anillo de foco visible.
const FOCO = ({ max, selRaiz }) => {
  const raiz = selRaiz ? document.querySelector(selRaiz) : document
  if (!raiz) return []
  const fallos = []
  const foco = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]),'
    + ' textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
  const visibles = [...raiz.querySelectorAll(foco)].filter((el) => {
    const r = el.getBoundingClientRect()
    if (r.width < 1 || r.height < 1) return false
    const cs = getComputedStyle(el)
    return cs.visibility !== 'hidden' && cs.display !== 'none'
  }).slice(0, max)
  const activo = document.activeElement
  for (const el of visibles) {
    el.focus()
    if (document.activeElement !== el) continue // no es una parada real
    const cs = getComputedStyle(el)
    const anillo = (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0)
      || (cs.boxShadow && cs.boxShadow !== 'none')
    if (!anillo) {
      fallos.push({
        tipo: 'foco',
        selector: (el.tagName.toLowerCase() + '.' + [...el.classList].slice(0, 3).join('.')).slice(0, 120),
        texto: (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 40),
      })
    }
  }
  if (activo && activo.focus) activo.focus()
  return fallos
}

// ── Orquestacion ──────────────────────────────────────────────────────────
const informe = { fecha: new Date().toISOString(), base: BASE, escenas: [], resumen: {} }
let totalFallos = 0
let totalMedidos = 0

const navegador = await chromium.launch()
const url = new URL(BASE)

// Un proyecto de cada tipo: el detalle de un curso y el de un promo no son
// la misma pantalla (el promo tiene su propio dialogo de audio).
const pidCache = {}
async function primerProyecto(page, tipo) {
  if (pidCache[tipo]) return pidCache[tipo]
  pidCache[tipo] = await page.evaluate(async (t) => {
    const d = await fetch('/api/projects').then((x) => x.json()).catch(() => null)
    const lista = d?.projects || []
    return (lista.find((p) => p.tipo === t) || lista[0])?.id || null
  }, tipo)
  return pidCache[tipo]
}

// Ir a una escena SIEMPRE con documento nuevo.
//
// Trampa que costo una auditoria entera: `page.goto` a una URL que solo
// cambia en el hash es una navegacion *del mismo documento*. La app no se
// recarga, asi que el script de `index.html` que lee `ms_theme` antes del
// primer pintado no vuelve a correr: los cuatro temas se median en
// `orbital`. Ademas el scroll se hereda, y con el scroll heredado la barra
// pegajosa tapa contenido que en reposo no tapa (13 falsas oclusiones).
// Con un parametro distinto en la query, el documento se carga de verdad.
let visita = 0
async function ir(page, hash, tema) {
  await page.goto(`${BASE}/?ux=${++visita}${hash}`, { waitUntil: 'domcontentloaded' })
  const activo = await page.evaluate(() => document.documentElement.dataset.theme)
  if (activo !== tema) return [{ tipo: 'tema-no-aplicado', esperado: tema, activo }]
  await page.evaluate(() => {
    document.documentElement.style.scrollBehavior = 'auto'
    window.scrollTo(0, 0)
  })
  return []
}

// Contraste de una escena: recoge, apaga el texto, captura, muestrea.
async function contraste(page, selRaiz) {
  const { nodos, fallos } = await page.evaluate(RECOGER, selRaiz)
  if (!nodos.length) return { fallos, medidos: 0 }
  // El texto se apaga para que la captura sea fondo puro. Y con el se apaga
  // el ORNAMENTO animado (`[data-ornamento]`: las estrellas del fondo): son
  // puntos de 2 px y enlaces de 0,6 px que se MUEVEN, asi que el «fondo» que
  // dan bajo una letra no existe en el fotograma siguiente. Medirlos daba un
  // fallo distinto en cada pasada —otra vista, otra letra, siempre un fondo
  // saturado del acento— y ninguno reproducible. Lo que queda fotografiado es
  // el fondo que sostiene al texto de verdad: lienzo, velos, chips y
  // degradados, todos ellos quietos. Con `--con-ornamento` se mide tambien la
  // capa decorativa (util solo para juzgar el ornamento en si).
  const estilo = await page.addStyleTag({
    content: '*,*::before,*::after{color:transparent !important;'
      + 'text-shadow:none !important;caret-color:transparent !important}'
      + (args['con-ornamento'] ? '' : '[data-ornamento]{display:none !important}'),
  })
  await page.waitForTimeout(150)
  const captura = (await page.screenshot({ type: 'png' })).toString('base64')
  await estilo.evaluate((e) => e.remove())
  const deContraste = await page.evaluate(MEDIR, { nodos, captura })
  return { fallos: [...fallos, ...deContraste], medidos: nodos.length }
}

function anota(escena, tema, viewport, medidos, fallos) {
  totalFallos += fallos.length
  totalMedidos += medidos
  informe.escenas.push({ escena, tema, viewport, medidos, fallos })
  process.stdout.write(fallos.length ? '✗' : '·')
}

for (const vpNombre of VP_ELEGIDOS) {
  const ctx = await navegador.newContext({ viewport: VIEWPORTS[vpNombre] })
  if (COOKIE) {
    await ctx.addCookies([{ name: 'ms_session', value: COOKIE, domain: url.hostname, path: '/' }])
  }
  const page = await ctx.newPage()
  const consola = []
  page.on('console', (m) => { if (m.type() === 'error') consola.push(m.text().slice(0, 200)) })
  page.on('pageerror', (e) => consola.push(`pageerror: ${String(e).slice(0, 200)}`))

  for (const tema of TEMAS) {
    await page.goto(`${BASE}/#/estudio`, { waitUntil: 'domcontentloaded' })
    await page.evaluate((t) => { localStorage.setItem('ms_theme', t) }, tema)

    for (const vista of VISTAS) {
      if (!VISTAS_ELEGIDAS.includes(vista.id)) continue
      consola.length = 0
      const hash = vista.detalle
        ? `#/proyectos/${await primerProyecto(page, vista.detalle)}` : vista.hash
      if (vista.detalle && hash.endsWith('null')) continue
      const malTema = await ir(page, hash, tema)
      // theme.css anima el cambio de tema (.3s): medir antes lee colores
      // interpolados que no existen en reposo (trampa del sprint 10).
      await page.waitForTimeout(1400)
      if (malTema.length) { anota(vista.id, tema, vpNombre, 0, malTema); continue }
      const { fallos, medidos } = await contraste(page, null)
      const foco = await page.evaluate(FOCO, { max: 30, selRaiz: null })
      if (args.capturas) {
        mkdirSync(args.capturas, { recursive: true })
        await page.screenshot({ path: `${args.capturas}/${vpNombre}-${tema}-${vista.id}.png` })
      }
      anota(vista.id, tema, vpNombre, medidos,
        [...fallos, ...foco, ...consola.map((t) => ({ tipo: 'consola', texto: t }))])
    }

    for (const ov of OVERLAYS) {
      if (!OVERLAYS_ELEGIDOS.includes(ov.id)) continue
      consola.length = 0
      const destino = ov.detalle
        ? `#/proyectos/${await primerProyecto(page, ov.detalle)}` : ov.hash
      const malTema = await ir(page, destino, tema)
      await page.waitForTimeout(1200)
      if (malTema.length) { anota(`overlay:${ov.id}`, tema, vpNombre, 0, malTema); continue }
      try {
        if (ov.tecla) await page.keyboard.press(ov.tecla)
        // Se abre con TECLADO, no con clic. Chromium decide `:focus-visible`
        // por la ultima modalidad de entrada: abriendo con raton, ningun
        // `.focus()` posterior pinta anillo y el instrumento acusaba de
        // «sin foco visible» a los 21 controles de cada dialogo.
        if (ov.boton) {
          const b = page.getByRole('button', { name: ov.boton }).first()
          await b.scrollIntoViewIfNeeded({ timeout: 4000 })
          await b.focus({ timeout: 4000 })
          await page.keyboard.press('Enter')
        }
        await page.waitForSelector('[role="dialog"]', { timeout: 4000 })
      } catch {
        anota(`overlay:${ov.id}`, tema, vpNombre, 0, [{ tipo: 'overlay-no-abre', texto: ov.id }])
        continue
      }
      await page.waitForTimeout(700)
      const { fallos, medidos } = await contraste(page, '[role="dialog"]')
      const foco = await page.evaluate(FOCO, { max: 20, selRaiz: '[role="dialog"]' })
      const fuera = await page.evaluate(() => {
        const d = document.querySelector('[role="dialog"]')
        if (!d) return []
        const r = d.getBoundingClientRect()
        return (r.left < -1 || r.top < -1 || r.right > innerWidth + 1 || r.bottom > innerHeight + 1)
          ? [{ tipo: 'overlay-fuera-de-viewport', caja: [r.left, r.top, r.right, r.bottom].map(Math.round) }]
          : []
      })
      if (args.capturas) {
        mkdirSync(args.capturas, { recursive: true })
        await page.screenshot({ path: `${args.capturas}/${vpNombre}-${tema}-overlay-${ov.id}.png` })
      }
      await page.keyboard.press('Escape')
      await page.waitForTimeout(400)
      const sigueAbierto = await page.locator('[role="dialog"]').count()
      anota(`overlay:${ov.id}`, tema, vpNombre, medidos, [
        ...fallos, ...foco, ...fuera,
        ...(sigueAbierto ? [{ tipo: 'overlay-no-cierra-con-escape', texto: ov.id }] : []),
        ...consola.map((t) => ({ tipo: 'consola', texto: t })),
      ])
    }
  }
  await ctx.close()
}
await navegador.close()

informe.resumen = {
  escenas: informe.escenas.length,
  nodosMedidos: totalMedidos,
  fallos: totalFallos,
  porTipo: informe.escenas.flatMap((e) => e.fallos).reduce((acc, f) => {
    acc[f.tipo] = (acc[f.tipo] || 0) + 1
    return acc
  }, {}),
}

console.log('\n')
console.log(`escenas: ${informe.resumen.escenas} · nodos de texto medidos: ${totalMedidos}`)
console.log(`fallos: ${totalFallos}`, informe.resumen.porTipo)
for (const e of informe.escenas) {
  if (!e.fallos.length) continue
  console.log(`\n▸ ${e.escena} · ${e.tema} · ${e.viewport} (${e.fallos.length})`)
  const vistos = new Set()
  for (const f of e.fallos) {
    const clave = `${f.tipo}|${f.selector || ''}|${f.texto || ''}`
    if (vistos.has(clave)) continue
    vistos.add(clave)
    console.log('   ', JSON.stringify(f))
  }
}
if (args.json) {
  writeFileSync(args.json, JSON.stringify(informe, null, 2))
  console.log(`\ninforme: ${args.json}`)
}
process.exit(totalFallos ? 1 : 0)
