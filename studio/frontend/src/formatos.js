// Formato del lienzo, del lado de la interfaz.
//
// Un promo de redes no es 16:9, y hasta el sprint P1 la app pintaba TODAS las
// miniaturas y reproductores con `aspect-video` escrito a mano: un video
// vertical se veia como una isla con bandas negras dentro de una caja 16:9.
//
// La proporcion de verdad es la del ARCHIVO (`job.resolution`, medida con
// ffprobe por el runner al terminar el render). El formato pedido al proyecto
// es solo el respaldo mientras ese archivo todavia no existe.

export const FORMATOS = [
  { id: 'horizontal', label: 'Horizontal · 16:9', hint: 'Cursos, YouTube', ratio: 16 / 9 },
  { id: 'vertical', label: 'Vertical · 9:16', hint: 'Instagram, TikTok, Shorts', ratio: 9 / 16 },
  { id: 'cuadrado', label: 'Cuadrado · 1:1', hint: 'Feed', ratio: 1 },
]

const POR_ID = Object.fromEntries(FORMATOS.map((f) => [f.id, f]))

export function formatoPorId(id) {
  return POR_ID[id] || POR_ID.horizontal
}

/** Proporción del formato pedido (16/9, 9/16, 1). */
export function ratioDeFormato(formato) {
  return formatoPorId(formato).ratio
}

/** Proporción de un job: la MEDIDA si ya hay video, la pedida si no. */
export function ratioDeJob(job, formatoProyecto) {
  const m = /^(\d+)x(\d+)$/.exec(job?.resolution || '')
  if (m) {
    const w = Number(m[1])
    const h = Number(m[2])
    if (w > 0 && h > 0) return w / h
  }
  return ratioDeFormato(job?.formato || formatoProyecto)
}

/** "1080×1920" a partir de la resolución medida, o "" si aún no hay video. */
export function resolucionLegible(job) {
  const m = /^(\d+)x(\d+)$/.exec(job?.resolution || '')
  return m ? `${m[1]}×${m[2]}` : ''
}
