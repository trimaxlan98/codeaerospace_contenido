import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import { cn } from '@/lib/utils'

export function Input({ className, type = 'text', ...props }) {
  return (
    <input
      type={type}
      className={cn(
        'flex h-9 w-full rounded-md border border-line bg-canvas px-3 py-1 text-sm text-ink',
        'transition-colors placeholder:text-faint',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan focus-visible:border-cyan/50',
        'disabled:cursor-not-allowed disabled:opacity-50',
        className,
      )}
      {...props}
    />
  )
}

/** Campo de contraseña con conmutador de visibilidad. Vive en el sistema
 *  porque lo usan el login, el cambio obligatorio y (sprint 3) Configuracion:
 *  tres copias del mismo boton se desincronizan solas. */
export function PasswordInput({ className, label = 'la contraseña', ...props }) {
  const [visible, setVisible] = useState(false)
  const Icon = visible ? EyeOff : Eye
  return (
    <div className="relative">
      <Input {...props} type={visible ? 'text' : 'password'} className={cn('pr-10', className)} />
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        aria-pressed={visible}
        aria-label={`${visible ? 'Ocultar' : 'Mostrar'} ${label}`}
        className="absolute right-1.5 top-1/2 grid -translate-y-1/2 place-items-center rounded p-1.5 text-muted transition-colors hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
      >
        <Icon className="h-[18px] w-[18px]" />
      </button>
    </div>
  )
}
