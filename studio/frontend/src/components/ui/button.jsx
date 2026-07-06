import { Slot } from '@radix-ui/react-slot'
import { cva } from 'class-variance-authority'
import { cn } from '@/lib/utils'

// Boton base del sistema. Variantes derivadas de los tokens (acento = firma).
const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md font-medium leading-none transition-[color,background-color,border-color,filter] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan focus-visible:ring-offset-1 focus-visible:ring-offset-canvas disabled:pointer-events-none disabled:opacity-45 select-none',
  {
    variants: {
      variant: {
        primary: 'bg-accent text-accent-ink font-semibold hover:brightness-110 active:brightness-95 shadow-[0_1px_0_rgba(255,255,255,0.15)_inset]',
        default: 'bg-surface-2 text-ink border border-line hover:border-line-strong hover:bg-surface-2/70',
        outline: 'border border-line text-ink hover:bg-surface-2',
        ghost: 'text-muted hover:text-ink hover:bg-surface-2',
        accent: 'text-accent border border-accent/40 hover:bg-accent/10',
        danger: 'border border-err/50 text-err bg-err/10 hover:bg-err/20',
      },
      size: {
        xs: 'h-7 px-2.5 text-xs',
        sm: 'h-8 px-3 text-[13px]',
        md: 'h-9 px-4 text-sm',
        lg: 'h-11 px-6 text-[15px]',
        icon: 'h-9 w-9 p-0',
        iconSm: 'h-8 w-8 p-0',
      },
    },
    defaultVariants: { variant: 'default', size: 'md' },
  },
)

export function Button({ className, variant, size, asChild = false, ...props }) {
  const Comp = asChild ? Slot : 'button'
  return <Comp className={cn(buttonVariants({ variant, size }), className)} {...props} />
}

export { buttonVariants }
