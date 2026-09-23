import { Link } from 'react-router-dom'
import type { ObjetoPublico } from '../api/estudiante'
import { BadgeEstadoObjeto } from './Badge'
import { Card } from './Card'

export function ObjetoCard({ objeto }: { objeto: ObjetoPublico }) {
  return (
    <Link to={`/objetos/${objeto.id}`} className="block h-full">
      <Card className="flex h-full flex-col gap-3 transition-transform duration-150 hover:-translate-y-0.5">
        {objeto.foto_url ? (
          <img
            src={objeto.foto_url}
            alt={objeto.nombre_objeto || 'Foto del objeto'}
            className="h-40 w-full rounded-input object-cover"
          />
        ) : (
          <div className="flex h-40 w-full items-center justify-center rounded-input bg-mist text-caption text-ink-muted">
            Sin foto
          </div>
        )}
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-display text-heading-sm text-ink">
            {objeto.nombre_objeto || 'Objeto sin nombre'}
          </h3>
          <BadgeEstadoObjeto estado={objeto.estado} etiqueta={objeto.estado_display} />
        </div>
        <p className="text-caption font-mono text-ink-muted">
          {objeto.categoria_nombre} · {objeto.sede_display}
        </p>
        {objeto.lugar_encontrado && (
          <p className="line-clamp-2 text-body text-ink-muted">Encontrado en {objeto.lugar_encontrado}</p>
        )}
      </Card>
    </Link>
  )
}
