// Pipeline de render: KaTeX sobre $...$/$$...$$ -> marked -> DOMPurify.
// Las formulas se extraen ANTES de marked para que este no rompa los
// backslashes de LaTeX; se reinyectan como placeholders ya renderizados.

import { marked } from 'marked'
import DOMPurify from 'dompurify'
import katex from 'katex'

marked.setOptions({ gfm: true, breaks: false })

function renderMath(md) {
  const chunks = []
  // Token improbable en prosa: no colisiona con texto real de las lecciones.
  const keep = (html) => `%%KTX${chunks.push(html) - 1}%%`
  // Bloques $$...$$ primero (pueden contener $ simples dentro)
  let out = md.replace(/\$\$([\s\S]+?)\$\$/g, (_, tex) =>
    keep(katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false })))
  // Inline $...$ (sin saltos de linea dentro)
  out = out.replace(/\$([^$\n]+?)\$/g, (_, tex) =>
    keep(katex.renderToString(tex.trim(), { throwOnError: false })))
  return { out, chunks }
}

export function renderMarkdown(md) {
  const { out, chunks } = renderMath(md)
  let html = marked.parse(out)
  html = html.replace(/%%KTX(\d+)%%/g, (_, i) => chunks[Number(i)])
  return DOMPurify.sanitize(html, {
    USE_PROFILES: { html: true, mathMl: true, svg: true },
  })
}
