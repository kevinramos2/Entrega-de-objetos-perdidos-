import type { ReactNode } from 'react'

interface StatCardProps {
  etiqueta: string
  valor: ReactNode
  detalle?: string
  tono?: 'verde' | 'amarillo' | 'azul'
  icono?: ReactNode
}

const TONOS: Record<NonNullable<StatCardProps['tono']>, string> = {
  verde: 'kpi-verde',
  amarillo: 'kpi-amarillo',
  azul: 'kpi-azul',
}

export function StatCard({ etiqueta, valor, detalle, tono, icono }: StatCardProps) {
  return (
    <div className={`kpi rounded-card border border-line bg-surface p-5 ${tono ? TONOS[tono] : ''}`}>
      {icono && (
        <span className="absolute right-4 top-4 flex h-9 w-9 items-center justify-center rounded-input bg-primary-wash text-primary">
          {icono}
        </span>
      )}
      <span className="kpi-valor font-display text-heading-lg font-bold">{valor}</span>
      <p className="mt-1 text-caption font-semibold text-muted">{etiqueta}</p>
      {detalle && <p className="mt-0.5 text-caption text-muted">{detalle}</p>}
    </div>
  )
}
