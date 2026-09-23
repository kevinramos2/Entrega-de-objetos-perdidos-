import { Link } from 'react-router-dom'
import type { ObjetoPublico } from '../api/estudiante'
import { CategoryIcon, fondoTenue } from './CategoryIcon'

export function ObjetoCard({ objeto }: { objeto: ObjetoPublico }) {
  const color = objeto.categoria_color || '#0b7a54'

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-card border border-line bg-surface shadow-card">
      {objeto.foto_url ? (
        <img src={objeto.foto_url} alt={objeto.nombre_objeto || 'Foto del objeto'} className="h-40 w-full object-cover" />
      ) : (
        <div className="flex h-32 w-full items-center justify-center" style={{ backgroundColor: fondoTenue(color) }}>
          <span
            className="flex h-14 w-14 items-center justify-center rounded-input bg-surface shadow-card"
            style={{ color }}
          >
            <CategoryIcon clave={objeto.categoria_icono} size={28} />
          </span>
        </div>
      )}
      <div className="flex flex-1 flex-col gap-2 p-4">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-display text-body-lg font-bold text-ink">
            {objeto.nombre_objeto || 'Objeto sin nombre'}
          </h3>
          <span
            className="flex-shrink-0 rounded-pill px-2.5 py-1 text-caption font-semibold"
            style={{ backgroundColor: fondoTenue(color), color }}
          >
            {objeto.categoria_nombre}
          </span>
        </div>
        {objeto.lugar_encontrado && <p className="text-body text-muted">{objeto.lugar_encontrado}</p>}
        <div className="mt-auto flex items-center justify-between pt-2">
          <span className="rounded-pill bg-info-wash px-2.5 py-1 text-caption font-semibold text-info">
            {objeto.sede_display}
          </span>
        </div>
        <Link
          to={`/objetos/${objeto.id}`}
          className="mt-2 inline-flex w-full items-center justify-center rounded-pill bg-primary px-4 py-2.5 text-body font-semibold text-white transition-colors hover:bg-primary-hover"
        >
          Ver detalles
        </Link>
      </div>
    </div>
  )
}
