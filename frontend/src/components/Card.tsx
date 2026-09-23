import type { HTMLAttributes } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  tono?: 'claro' | 'tenue' | 'oscuro'
  flotante?: boolean
}

const TONOS: Record<NonNullable<CardProps['tono']>, string> = {
  claro: 'bg-surface border border-line',
  tenue: 'bg-primary-wash border border-primary/15',
  oscuro: 'bg-dark-lift border border-dark-line text-on-dark',
}

export function Card({ tono = 'claro', flotante = false, className = '', children, ...props }: CardProps) {
  return (
    <div
      className={`rounded-card p-6 ${TONOS[tono]} ${flotante ? 'shadow-floating' : 'shadow-card'} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}
