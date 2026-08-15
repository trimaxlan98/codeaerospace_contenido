// Identidad CO.DE Academy dentro de la interfaz.
//
// Es la MISMA marca que `studio/content/manim_extensions/code_brand.py`
// estampa en cada video (wordmark con el punto en ambar, esquinas HUD, ambar
// -> naranja). Que la consola y el render se vean de la misma familia es un
// requisito del encargo, no decoracion.
//
// Divergencia consciente: el video usa Rajdhani (TTF propia, registrada en
// Pango dentro del contenedor); la web usa la display que ya carga la app
// (Space Grotesk). Traer Rajdhani al bundle costaria ~150 kB para un
// wordmark, y el despliegue del VPS es `git pull` + `vite build` sin
// `npm install`: cualquier dependencia nueva rompe ese camino.
//
// La geometria del glifo es la misma que genera `studio/tools/brand_icons.mjs`
// para el favicon: si cambia una, cambia la otra.

import { useId } from 'react'
import { cn } from '@/lib/utils'

/** Glifo de marca: teja oscura + "C" geometrica + punto ambar. Colores fijos
 *  (es un logotipo, no sigue al tema); funciona igual sobre lienzo claro. */
export function BrandMark({ size = 40, className }) {
  const gid = useId() // dos marcas en la misma pagina no pueden compartir id de gradiente
  return (
    <svg
      viewBox="0 0 64 64"
      width={size}
      height={size}
      role="img"
      aria-label="CO.DE Academy"
      className={cn('shrink-0', className)}
    >
      <defs>
        <linearGradient id={gid} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#f59e0b" />
          <stop offset="100%" stopColor="#ea580c" />
        </linearGradient>
      </defs>
      <rect x="0" y="0" width="64" height="64" rx="14" fill="#05070a" />
      {/* esquinas HUD: el mismo encuadre que enmarca cada escena renderizada */}
      <g stroke="#f59e0b" strokeOpacity="0.45" strokeWidth="2" fill="none" strokeLinecap="round">
        <path d="M8 15V8h7M49 8h7v7M56 49v7h-7M15 56H8v-7" />
      </g>
      <path
        d="M35.03 20.53A14 14 0 1 0 35.03 43.47"
        fill="none"
        stroke="#e8edf3"
        strokeWidth="8"
        strokeLinecap="round"
      />
      <circle cx="50" cy="43.5" r="5.5" fill={`url(#${gid})`} />
    </svg>
  )
}

const WORDMARK_SIZES = {
  sm: 'text-[12px]',
  md: 'text-[15px]',
  lg: 'text-[19px]',
}

/** Wordmark "CO.DE ACADEMY". El punto en ambar es el rasgo distintivo del
 *  logotipo; `--brand` se oscurece en el tema claro para cumplir contraste. */
export function Wordmark({ size = 'md', className }) {
  return (
    <span
      className={cn('inline-flex items-baseline gap-[0.4em] font-display leading-none',
        WORDMARK_SIZES[size] || WORDMARK_SIZES.md, className)}
    >
      <span className="font-semibold tracking-tight text-ink">
        CO<span className="text-brand">.</span>DE
      </span>
      <span className="text-[0.72em] font-medium uppercase tracking-[0.24em] text-muted">
        Academy
      </span>
    </span>
  )
}

/** Cuatro escuadras de esquina estilo HUD: el encuadre de la marca aplicado a
 *  un contenedor (que debe ser `relative`). Puro ornamento -> aria-hidden. */
export function HudCorners({ className, inset = 'inset-2.5' }) {
  const arm = 'absolute h-3.5 w-3.5 border-brand/35'
  return (
    <span aria-hidden="true" className={cn('pointer-events-none absolute', inset, className)}>
      <span className={cn(arm, 'left-0 top-0 border-l border-t')} />
      <span className={cn(arm, 'right-0 top-0 border-r border-t')} />
      <span className={cn(arm, 'bottom-0 left-0 border-b border-l')} />
      <span className={cn(arm, 'bottom-0 right-0 border-b border-r')} />
    </span>
  )
}
