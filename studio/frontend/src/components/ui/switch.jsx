// Conmutador booleano del sistema. Escrito a mano (role="switch" nativo) en
// vez de traer @radix-ui/react-switch: es un boton con dos estados y no
// justifica una dependencia mas en el bundle.

import { cn } from '@/lib/utils'

export function Switch({ checked, onCheckedChange, disabled, className, ...props }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => onCheckedChange?.(!checked)}
      className={cn(
        'relative inline-flex h-6 w-11 shrink-0 items-center rounded-full border transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan focus-visible:ring-offset-1 focus-visible:ring-offset-canvas',
        'disabled:cursor-not-allowed disabled:opacity-45',
        checked ? 'border-accent/60 bg-accent/85' : 'border-line bg-canvas',
        className,
      )}
      {...props}
    >
      <span
        aria-hidden="true"
        className={cn(
          'block h-4 w-4 rounded-full transition-transform',
          checked ? 'translate-x-[24px] bg-accent-ink' : 'translate-x-[3px] bg-muted',
        )}
      />
    </button>
  )
}

/** Fila de ajuste: rotulo + explicacion a la izquierda, control a la derecha.
 *  Es el bloque de construccion de toda la vista de Configuracion. */
export function SettingRow({ label, hint, htmlFor, children }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-2 border-t border-line px-4 py-3.5 first:border-t-0">
      <div className="min-w-[min(100%,15rem)] flex-1">
        <label htmlFor={htmlFor} className="block text-[13.5px] font-medium text-ink">{label}</label>
        {hint && <p className="mt-0.5 max-w-[60ch] text-[12px] leading-relaxed text-muted">{hint}</p>}
      </div>
      <div className="flex shrink-0 items-center gap-2">{children}</div>
    </div>
  )
}
