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

const TONOS_ICONO: Record<NonNullable<StatCardProps['tono']>, string> = {
  verde: 'bg-success-wash text-success',
  amarillo: 'bg-warning-wash text-warning',
  azul: 'bg-info-wash text-info',
}

export function StatCard({ etiqueta, valor, detalle, tono, icono }: StatCardProps) {
  return (
    <div className={`kpi rounded-card border border-line bg-surface p-5 ${tono ? TONOS[tono] : ''}`}>
      {icono && (
        <span
          className={`absolute right-4 top-4 flex h-9 w-9 items-center justify-center rounded-input [&>svg]:h-4.5 [&>svg]:w-4.5 ${
            tono ? TONOS_ICONO[tono] : 'bg-primary-wash text-primary'
          }`}
        >
          {icono}
        </span>
      )}
      <span className="kpi-valor font-display text-heading-lg font-bold">{valor}</span>
      <p className="mt-1 text-caption font-semibold text-muted">{etiqueta}</p>
      {detalle && <p className="mt-0.5 text-caption text-muted">{detalle}</p>}
    </div>
  )
}
