import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Variante = 'primario' | 'invertido' | 'ghost' | 'ghost-oscuro' | 'peligro'
type Tamano = 'sm' | 'md'

interface BotonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante
  tamano?: Tamano
  children: ReactNode
}

const TAMANOS: Record<Tamano, string> = {
  sm: 'text-caption px-4 py-2',
  md: 'text-body px-5 py-2.5',
}

export function Button({ variante = 'primario', tamano = 'md', className = '', ...props }: BotonProps) {
  return (
    <button className={`btn btn-${variante} font-sans ${TAMANOS[tamano]} ${className}`} {...props} />
  )
}
