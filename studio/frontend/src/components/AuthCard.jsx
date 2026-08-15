// Tarjeta de las pantallas sin sesion (Login y cambio de contraseña):
// panel de marca a la izquierda + formulario a la derecha, apilados en movil.
//
// Sustituye a `GlowCard`, que pintaba un resplandor HSL fijo (morado) ajeno a
// los temas y solo dejaba un velo del 4,5 % sobre el lienzo: sobre el cielo
// animado la tarjeta no se leia como tarjeta ("esta todo oscuro", encargo 1).
// Aqui el fondo es el lienzo del tema al 88 % con borde fuerte: legible en los
// cuatro temas y sin depender de que el navegador soporte backdrop-filter.

import { cn } from '@/lib/utils'
import { BrandMark, HudCorners, Wordmark } from './Brand.jsx'

/** Fondo compartido: cielo del tema + viñeta que oscurece los bordes para que
 *  la tarjeta gane contraste contra el degradado. */
function AuthBackdrop() {
  return (
    <>
      <div className="login__sky" aria-hidden="true" />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_35%,var(--canvas)_100%)] opacity-90"
      />
    </>
  )
}

/** Columna de marca. En movil se reduce a la firma (marca + wordmark): el
 *  formulario es lo que se viene a hacer, el discurso sobra en 390 px. */
function BrandPanel({ title, subtitle, facts }) {
  return (
    <div className="relative flex flex-col gap-5 border-b border-line bg-surface-2/60 p-6 md:w-[46%] md:border-b-0 md:border-r md:p-8">
      <HudCorners className="hidden md:block" />
      <div className="flex items-center gap-3">
        <BrandMark size={40} />
        <Wordmark size="md" />
      </div>

      <div>
        <h1 className="font-display text-[26px] font-semibold leading-tight tracking-tight text-ink">
          {title}
        </h1>
        <p className="mt-2 max-w-[34ch] text-[13.5px] leading-relaxed text-muted">{subtitle}</p>
      </div>

      {facts?.length > 0 && (
        <ul className="mt-auto hidden flex-col gap-2 md:flex">
          {facts.map((f) => (
            <li key={f} className="flex items-start gap-2">
              <span aria-hidden="true" className="mt-[6px] h-1 w-1 shrink-0 rounded-full bg-brand" />
              <span className="eyebrow leading-[1.5]">{f}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

/**
 * @param title    titulo grande de la columna de marca
 * @param subtitle una frase de contexto
 * @param facts    lineas cortas en mono (solo escritorio)
 * @param heading  titulo del formulario
 * @param shake    sacude la tarjeta (error de credenciales)
 */
export function AuthCard({ title, subtitle, facts, heading, shake, children, ...formProps }) {
  return (
    <div className="relative grid min-h-dvh place-items-center overflow-hidden p-4 sm:p-6">
      <AuthBackdrop />

      <form
        {...formProps}
        className={cn(
          'relative z-[1] flex w-full max-w-[880px] flex-col overflow-hidden rounded-xl md:flex-row',
          'border border-line-strong bg-canvas/88 backdrop-blur-xl',
          'shadow-[0_30px_80px_-20px_rgba(0,0,0,0.55)]',
          'animate-in fade-in slide-in-from-bottom-2 duration-500',
          shake && 'animate-shake',
        )}
      >
        <BrandPanel title={title} subtitle={subtitle} facts={facts} />

        <div className="flex flex-1 flex-col justify-center gap-5 p-6 md:p-8">
          <h2 className="font-display text-[17px] font-semibold tracking-tight text-ink">{heading}</h2>
          {children}
        </div>
      </form>
    </div>
  )
}

/** Campo etiquetado: rotulo mono arriba, control debajo, ayuda opcional. */
export function Field({ label, hint, children }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="eyebrow">{label}</span>
      {children}
      {hint && <span className="text-[11.5px] text-muted">{hint}</span>}
    </label>
  )
}
