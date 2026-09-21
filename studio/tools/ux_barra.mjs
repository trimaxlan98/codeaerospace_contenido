#!/usr/bin/env node
// La barra superior, medida en los anchos que la auditoria no cubre.
//
// `ux_auditoria.mjs` mide en 1440 y 390. La barra se rompe ENTRE medias: con
// siete vistas, a 1280 px (el portatil mas comun) «Admin» salia cortado y el
// reloj se partia en dos lineas; a 900 se escondian tres vistas sin que nada
// lo dijera (sprint 11). Este instrumento recorre cada ancho con CADA vista
// activa —la activa lleva rotulo y es la que mas ocupa— y falla si algun
// boton de la nav queda fuera de su caja, si la nav necesita scroll, si la
// pagina desborda o si un texto de la barra se parte en dos lineas.
//
//   node studio/tools/ux_barra.mjs --base http://127.0.0.1:4173 --cookie "$COOKIE" \
//        [--anchos 360,390,768,1024,1280,1440,1536,1920]

import { chromium } from '../frontend/node_modules/playwright/index.mjs'

const args = Object.fromEntries(
  process.argv.slice(2).flatMap((a, i, all) =>
    a.startsWith('--') ? [[a.slice(2), all[i + 1] && !all[i + 1].startsWith('--') ? all[i + 1] : true]] : []),
)
const BASE = args.base || 'http://127.0.0.1:4173'
const ANCHOS = String(args.anchos || '360,375,390,414,768,900,1024,1180,1280,1366,1440,1536,1600,1680,1920')
  .split(',').map(Number)
const VISTAS = ['proyectos', 'estudio', 'renders', 'biblioteca', 'aprender', 'laboratorio', 'admin', 'configuracion']

const MEDIR = () => {
  const nav = document.querySelector('nav[aria-label="vistas"]')
  const header = document.querySelector('header')
  if (!nav || !header) return { fallos: ['sin barra'] }
  const nr = nav.getBoundingClientRect()
  const fallos = []
  for (const b of nav.querySelectorAll('button')) {
    const r = b.getBoundingClientRect()
    if (r.right > nr.right + 1 || r.left < nr.left - 1) fallos.push(`cortado: ${b.textContent.trim()}`)
  }
  if (nav.scrollWidth - nav.clientWidth > 1) fallos.push(`nav con scroll ${nav.scrollWidth - nav.clientWidth}px`)
  const desborde = document.documentElement.scrollWidth - innerWidth
  if (desborde > 1) fallos.push(`pagina desborda ${desborde}px`)
  // Un texto de la barra que se parte en dos lineas (el reloj, «Ctrl K»).
  for (const el of header.querySelectorAll('span, kbd, button')) {
    const cs = getComputedStyle(el)
    if (cs.display === 'none' || el.closest('.sr-only') || el.classList.contains('sr-only')) continue
    if (el.children.length && el.tagName !== 'KBD') continue
    const rects = [...el.getClientRects()].filter((r) => r.width > 0)
    const lineas = new Set(rects.map((r) => Math.round(r.top))).size
    const alto = el.getBoundingClientRect().height
    const linea = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.5
    if (lineas > 1 || (el.textContent.trim() && alto > linea * 1.8 && el.tagName !== 'BUTTON')) {
      fallos.push(`partido en dos lineas: ${el.textContent.trim().slice(0, 30)}`)
    }
  }
  return { fallos, alto: Math.round(header.getBoundingClientRect().height) }
}

const navegador = await chromium.launch()
let total = 0
for (const ancho of ANCHOS) {
  const ctx = await navegador.newContext({ viewport: { width: ancho, height: 800 } })
  if (args.cookie) {
    await ctx.addCookies([{ name: 'ms_session', value: args.cookie, domain: new URL(BASE).hostname, path: '/' }])
  }
  const page = await ctx.newPage()
  const linea = []
  for (const vista of VISTAS) {
    await page.goto(`${BASE}/?barra=${ancho}-${vista}#/${vista}`, { waitUntil: 'domcontentloaded' })
    await page.waitForSelector('nav[aria-label="vistas"]', { timeout: 15000 })
    await page.waitForTimeout(500)
    const { fallos, alto } = await page.evaluate(MEDIR)
    total += fallos.length
    linea.push(fallos.length ? `✗ ${vista}: ${fallos.join('; ')}` : null)
    if (vista === VISTAS[0]) linea.unshift(`alto de la barra ${alto}px`)
  }
  const malos = linea.filter((l) => l && l.startsWith('✗'))
  console.log(`${String(ancho).padStart(4)} px  ${malos.length ? '' : 'ok · '}${linea[0]}`)
  for (const m of malos) console.log(`         ${m}`)
  await ctx.close()
}
await navegador.close()
console.log(total ? `\n${total} fallos` : '\nbarra limpia en todos los anchos y vistas')
process.exit(total ? 1 : 0)
