import type { HTMLAttributes } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  tono?: 'papel' | 'mist' | 'oscuro'
  flotante?: boolean
}

const TONOS: Record<NonNullable<CardProps['tono']>, string> = {
  papel: 'bg-paper border border-hairline',
  mist: 'bg-mist border border-hairline',
  oscuro: 'bg-forest-lift border border-forest-hairline text-cream',
}

export function Card({ tono = 'papel', flotante = false, className = '', children, ...props }: CardProps) {
  return (
    <div
      className={`rounded-card p-6 ${TONOS[tono]} ${flotante ? 'shadow-floating' : 'shadow-card'} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}
