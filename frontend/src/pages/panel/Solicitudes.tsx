import { useState } from 'react'
import { Link } from 'react-router-dom'
import { BadgeEstadoSolicitud } from '../../components/Badge'
import { CategoryIcon } from '../../components/CategoryIcon'
import { useSolicitudesAdmin } from '../../hooks/usePanelApi'
import { formatearFecha } from '../../lib/fecha'

const FILTROS = [
  { estado: '', etiqueta: 'conteo', clave: 'por_revisar' as const, texto: 'Por revisar' },
  { estado: 'apelada', etiqueta: 'conteo', clave: 'apelada' as const, texto: 'Apeladas' },
  { estado: 'aprobada', etiqueta: 'conteo', clave: 'aprobada' as const, texto: 'Aprobadas' },
  { estado: 'rechazada', etiqueta: 'conteo', clave: 'rechazada' as const, texto: 'Rechazadas' },
]

export default function Solicitudes() {
  const [estado, setEstado] = useState('')
  const { data, isLoading } = useSolicitudesAdmin({ estado })

  return (
    <div className="flex flex-col gap-6">
      <header>
        <p className="text-caption text-muted">Gestión</p>
        <h1 className="font-display text-heading font-bold text-ink">Solicitudes de reclamación</h1>
      </header>

      <div className="flex flex-wrap gap-2">
        {FILTROS.map((f) => (
          <button
            key={f.texto}
            onClick={() => setEstado(f.estado)}
            className={`cat-chip inline-flex items-center gap-1.5 rounded-pill border px-4 py-2 text-caption font-semibold shadow-card ${
              estado === f.estado ? 'activo' : 'border-line bg-surface text-ink-soft hover:border-primary/40'
            }`}
          >
            {f.texto} ({data?.conteos[f.clave] ?? 0})
          </button>
        ))}
      </div>

      {isLoading && <p className="text-body text-muted">Cargando…</p>}

      {data && data.solicitudes.length === 0 && (
        <p className="rounded-card border border-line bg-surface p-8 text-center text-body text-muted shadow-card">
          No hay solicitudes en esta vista.
        </p>
      )}

      {data && data.solicitudes.length > 0 && (
        <div className="overflow-x-auto rounded-card shadow-card">
          <table className="tabla min-w-[760px]">
            <thead>
              <tr>
                <th>Estudiante</th>
                <th>Objeto</th>
                <th>Mensaje</th>
                <th>Fecha</th>
                <th>Estado</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {data.solicitudes.map((s) => (
                <tr key={s.id}>
                  <td>
                    <b className="text-ink">{s.usuario_nombre}</b>
                    <p className="text-caption text-muted">{s.usuario_email}</p>
                  </td>
                  <td>
                    <div className="flex items-center gap-2.5">
                      <span
                        className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-input text-white"
                        style={{ backgroundColor: s.objeto_detalle.categoria_color || '#0b7a54' }}
                      >
                        <CategoryIcon clave={s.objeto_detalle.categoria_icono} size={16} />
                      </span>
                      <div>
                        <b className="text-ink">{s.objeto_detalle.nombre_objeto}</b>
                        <p className="text-caption text-muted">{s.objeto_detalle.categoria_nombre}</p>
                      </div>
                    </div>
                  </td>
                  <td className="max-w-60 truncate text-muted">{s.mensaje || '—'}</td>
                  <td className="text-caption text-muted">{formatearFecha(s.fecha, { conHora: true })}</td>
                  <td>
                    <BadgeEstadoSolicitud estado={s.estado} etiqueta={s.estado_display} />
                  </td>
                  <td>
                    <Link to={`/panel/solicitudes/${s.id}`} className="btn btn-ghost text-caption px-4 py-2">
                      Revisar
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
