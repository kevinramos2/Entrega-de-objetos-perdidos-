import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Variante = 'primario' | 'ghost' | 'ghost-oscuro' | 'peligro'
type Tamano = 'sm' | 'md'

interface BotonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante
  tamano?: Tamano
  children: ReactNode
}

const BASE =
  'inline-flex items-center justify-center gap-2 rounded-pill font-sans font-medium ' +
  'transition-colors duration-150 ease-out disabled:opacity-50 disabled:pointer-events-none ' +
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2'

const VARIANTES: Record<Variante, string> = {
  primario:
    'bg-terracota text-paper hover:bg-terracota-hover focus-visible:ring-terracota focus-visible:ring-offset-paper',
  ghost:
    'bg-transparent text-ink border border-hairline hover:border-ink focus-visible:ring-terracota focus-visible:ring-offset-paper',
  'ghost-oscuro':
    'bg-transparent text-cream border border-forest-hairline hover:border-cream focus-visible:ring-cream focus-visible:ring-offset-forest',
  peligro:
    'bg-transparent text-alerta border border-alerta/40 hover:bg-alerta-wash focus-visible:ring-alerta focus-visible:ring-offset-paper',
}

const TAMANOS: Record<Tamano, string> = {
  sm: 'text-caption px-4 py-2',
  md: 'text-body px-5 py-2.5',
}

export function Button({ variante = 'primario', tamano = 'md', className = '', ...props }: BotonProps) {
  return (
    <button className={`${BASE} ${VARIANTES[variante]} ${TAMANOS[tamano]} ${className}`} {...props} />
  )
}
