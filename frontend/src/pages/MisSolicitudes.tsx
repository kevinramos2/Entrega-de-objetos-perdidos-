import { useState, type FormEvent } from 'react'
import type { Solicitud } from '../api/estudiante'
import { ApiError } from '../api/client'
import { BadgeEstadoSolicitud } from '../components/Badge'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Textarea } from '../components/Input'
import { useApelarSolicitud, useMisSolicitudes } from '../hooks/useEstudianteApi'

function TarjetaSolicitud({ solicitud }: { solicitud: Solicitud }) {
  const apelar = useApelarSolicitud()
  const [mostrarApelacion, setMostrarApelacion] = useState(false)
  const [motivo, setMotivo] = useState('')
  const [error, setError] = useState('')

  async function enviarApelacion(evento: FormEvent) {
    evento.preventDefault()
    setError('')
    try {
      await apelar.mutateAsync({ id: solicitud.id, motivo })
      setMostrarApelacion(false)
      setMotivo('')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No pudimos enviar tu apelación.')
    }
  }

  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-display text-heading-sm text-ink">
            {solicitud.objeto_detalle.nombre_objeto || 'Objeto sin nombre'}
          </h3>
          <p className="text-caption font-mono text-ink-muted">
            Solicitado el {new Date(solicitud.fecha).toLocaleDateString('es-CO')}
          </p>
        </div>
        <BadgeEstadoSolicitud estado={solicitud.estado} etiqueta={solicitud.estado_display} />
      </div>

      {solicitud.comentario_admin && (
        <p className="text-body text-ink-muted">
          <span className="font-medium text-ink">Respuesta: </span>
          {solicitud.comentario_admin}
        </p>
      )}

      {solicitud.estado === 'aprobada' && solicitud.datos_entrega && (
        <div className="rounded-input bg-salvia-wash p-4">
          <p className="text-caption font-medium uppercase tracking-wide text-salvia">
            ¿Cómo reclamar tu objeto?
          </p>
          <p className="mt-1 text-body text-ink">{solicitud.datos_entrega}</p>
        </div>
      )}

      {solicitud.puede_apelar && !mostrarApelacion && (
        <Button variante="ghost" tamano="sm" className="self-start" onClick={() => setMostrarApelacion(true)}>
          Apelar esta decisión
        </Button>
      )}

      {mostrarApelacion && (
        <form onSubmit={enviarApelacion} className="flex flex-col gap-3 rounded-input border border-hairline p-4">
          <Textarea
            id={`apelacion-${solicitud.id}`}
            label="¿Por qué no estás de acuerdo con la decisión?"
            rows={3}
            value={motivo}
            onChange={(evento) => setMotivo(evento.target.value)}
            required
          />
          {error && <p className="text-caption text-alerta">{error}</p>}
          <div className="flex gap-2">
            <Button type="submit" variante="primario" tamano="sm" disabled={apelar.isPending}>
              {apelar.isPending ? 'Enviando…' : 'Enviar apelación'}
            </Button>
            <Button type="button" variante="ghost" tamano="sm" onClick={() => setMostrarApelacion(false)}>
              Cancelar
            </Button>
          </div>
        </form>
      )}

      {solicitud.fue_apelada && solicitud.estado === 'apelada' && (
        <p className="text-caption text-ink-muted">Tu apelación está en revisión.</p>
      )}
    </Card>
  )
}

export default function MisSolicitudes() {
  const { data, isLoading } = useMisSolicitudes()

  return (
    <div className="flex flex-col gap-8">
      <header>
        <h1 className="font-display text-heading text-ink">Mis solicitudes</h1>
        <p className="mt-1 text-body text-ink-muted">Sigue el estado de los objetos que has reclamado.</p>
      </header>

      {isLoading && <p className="text-body text-ink-muted">Cargando…</p>}

      {data && data.solicitudes.length === 0 && (
        <p className="rounded-card border border-hairline bg-mist p-8 text-center text-body text-ink-muted">
          Todavía no has solicitado ningún objeto.
        </p>
      )}

      {data && data.solicitudes.length > 0 && (
        <div className="flex flex-col gap-4">
          {data.solicitudes.map((solicitud) => (
            <TarjetaSolicitud key={solicitud.id} solicitud={solicitud} />
          ))}
        </div>
      )}
    </div>
  )
}
