import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Variante = 'primario' | 'invertido' | 'ghost' | 'ghost-oscuro' | 'peligro'
type Tamano = 'sm' | 'md'

interface BotonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante
  tamano?: Tamano
  children: ReactNode
}

const BASE =
  'inline-flex items-center justify-center gap-2 rounded-pill font-sans font-semibold ' +
  'transition-colors duration-150 ease-out disabled:opacity-50 disabled:pointer-events-none ' +
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2'

const VARIANTES: Record<Variante, string> = {
  primario:
    'bg-primary text-white shadow-card hover:bg-primary-hover focus-visible:ring-primary focus-visible:ring-offset-canvas',
  invertido:
    'bg-white text-primary-dark shadow-card hover:bg-white/90 focus-visible:ring-white focus-visible:ring-offset-dark',
  ghost:
    'bg-surface text-primary border border-primary/30 hover:border-primary hover:bg-primary-wash focus-visible:ring-primary focus-visible:ring-offset-canvas',
  'ghost-oscuro':
    'bg-transparent text-on-dark border border-on-dark/40 hover:bg-white/10 focus-visible:ring-on-dark focus-visible:ring-offset-dark',
  peligro:
    'bg-transparent text-danger border border-danger/30 hover:bg-danger-wash focus-visible:ring-danger focus-visible:ring-offset-canvas',
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
