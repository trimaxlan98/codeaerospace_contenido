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
