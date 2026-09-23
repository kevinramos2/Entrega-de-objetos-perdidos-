import type { ReactNode } from 'react'
import { Card } from './Card'

interface StatCardProps {
  etiqueta: string
  valor: ReactNode
  detalle?: string
  tono?: 'papel' | 'oscuro'
}

export function StatCard({ etiqueta, valor, detalle, tono = 'papel' }: StatCardProps) {
  return (
    <Card tono={tono === 'oscuro' ? 'oscuro' : 'mist'} className="flex flex-col gap-1">
      <span className={`text-caption font-mono uppercase tracking-wide ${tono === 'oscuro' ? 'text-cream-muted' : 'text-ink-muted'}`}>
        {etiqueta}
      </span>
      <span className={`font-display text-heading-lg ${tono === 'oscuro' ? 'text-cream' : 'text-ink'}`}>
        {valor}
      </span>
      {detalle && (
        <span className={`text-caption ${tono === 'oscuro' ? 'text-cream-muted' : 'text-ink-muted'}`}>
          {detalle}
        </span>
      )}
    </Card>
  )
}
