// Pipeline de render: extraer codigo -> KaTeX sobre $...$/$$...$$ -> restaurar
// codigo -> marked -> DOMPurify.
// El codigo (fences ``` / ~~~ y code spans `...`) se extrae ANTES de aplicar
// los regex de math para que un $ dentro de codigo (ej. `echo $HOME`) nunca se
// confunda con una formula. Se restaura ANTES de marked para que este procese
// el codigo normalmente. Las formulas se extraen ANTES de marked para que este
// no rompa los backslashes de LaTeX; se reinyectan como placeholders ya
// renderizados despues de marked.

import { marked } from 'marked'
import DOMPurify from 'dompurify'
import katex from 'katex'

marked.setOptions({ gfm: true, breaks: false })

function extractCode(md) {
  const chunks = []
  // Token improbable en prosa: no colisiona con texto real de las lecciones.
  const keep = (text) => `%%CODE${chunks.push(text) - 1}%%`
  // Fences ```...``` y ~~~...~~~ primero (pueden abarcar varias lineas).
  let out = md.replace(/```[\s\S]*?```|~~~[\s\S]*?~~~/g, keep)
  // Code spans inline `...` (sin saltos de linea dentro).
  out = out.replace(/`[^`\n]+`/g, keep)
  return { out, chunks }
}

function renderMath(md) {
  const chunks = []
  // Token improbable en prosa: no colisiona con texto real de las lecciones.
  const keep = (html) => `%%KTX${chunks.push(html) - 1}%%`
  // Bloques $$...$$ primero (pueden contener $ simples dentro)
  let out = md.replace(/\$\$([\s\S]+?)\$\$/g, (_, tex) =>
    keep(katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false })))
  // Inline $...$, convencion Pandoc: sin espacio tras el $ de apertura, sin
  // espacio ni backslash antes del $ de cierre, y el cierre no seguido de
  // digito (evita que "$62 millones ... $80 millones" se lea como formula).
  out = out.replace(/\$(?!\s)((?:[^$\n])+?)(?<![\s\\])\$(?!\d)/g, (_, tex) =>
    keep(katex.renderToString(tex.trim(), { throwOnError: false })))
  return { out, chunks }
}

export function renderMarkdown(md) {
  const { out: noCode, chunks: codeChunks } = extractCode(md)
  const { out: mathOut, chunks: mathChunks } = renderMath(noCode)
  const restored = mathOut.replace(/%%CODE(\d+)%%/g, (_, i) => codeChunks[Number(i)])
  let html = marked.parse(restored)
  html = html.replace(/%%KTX(\d+)%%/g, (_, i) => mathChunks[Number(i)])
  return DOMPurify.sanitize(html, {
    USE_PROFILES: { html: true, mathMl: true, svg: true },
  })
}
