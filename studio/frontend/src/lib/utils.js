import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

// cn(): combina clases condicionales (clsx) y resuelve conflictos de Tailwind
// (twMerge). Base de todas las primitivas estilo shadcn.
export function cn(...inputs) {
  return twMerge(clsx(inputs))
}
