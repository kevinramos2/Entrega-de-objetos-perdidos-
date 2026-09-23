import type { ReactNode } from 'react'
import { Card } from './Card'

interface StatCardProps {
  etiqueta: string
  valor: ReactNode
  detalle?: string
  tono?: 'claro' | 'oscuro'
  icono?: ReactNode
}

export function StatCard({ etiqueta, valor, detalle, tono = 'claro', icono }: StatCardProps) {
  return (
    <Card tono={tono === 'oscuro' ? 'oscuro' : 'claro'} className="flex flex-col gap-1">
      <div className="flex items-center justify-between">
        <span className={`text-caption font-medium uppercase tracking-wide ${tono === 'oscuro' ? 'text-on-dark-muted' : 'text-muted'}`}>
          {etiqueta}
        </span>
        {icono && (
          <span className={`flex h-8 w-8 items-center justify-center rounded-input ${tono === 'oscuro' ? 'bg-white/10' : 'bg-primary-wash text-primary'}`}>
            {icono}
          </span>
        )}
      </div>
      <span className={`font-display text-heading-lg font-bold ${tono === 'oscuro' ? 'text-on-dark' : 'text-ink'}`}>
        {valor}
      </span>
      {detalle && (
        <span className={`text-caption ${tono === 'oscuro' ? 'text-on-dark-muted' : 'text-muted'}`}>{detalle}</span>
      )}
    </Card>
  )
}
