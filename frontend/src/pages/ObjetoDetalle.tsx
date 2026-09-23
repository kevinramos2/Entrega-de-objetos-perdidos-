import { useState, type FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { TIPOS_DOCUMENTO, type DatosSolicitud } from '../api/estudiante'
import { ApiError } from '../api/client'
import { BadgeEstadoObjeto } from '../components/Badge'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { CategoryIcon, fondoTenue } from '../components/CategoryIcon'
import { Input, Select, Textarea } from '../components/Input'
import { useObjeto, useSolicitarReclamo } from '../hooks/useEstudianteApi'

type Errores = Partial<Record<keyof DatosSolicitud, string[]>>

export default function ObjetoDetalle() {
  const { id } = useParams()
  const objetoId = Number(id)
  const navigate = useNavigate()

  const { data: objeto, isLoading } = useObjeto(objetoId)
  const solicitar = useSolicitarReclamo(objetoId)

  const [form, setForm] = useState<DatosSolicitud>({
    mensaje: '', tipo_documento: 'CC', numero_documento: '', telefono: '',
  })
  const [errores, setErrores] = useState<Errores>({})
  const [errorGeneral, setErrorGeneral] = useState('')

  function actualizar<K extends keyof DatosSolicitud>(campo: K, valor: string) {
    setForm((previo) => ({ ...previo, [campo]: valor }))
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    setErrores({})
    setErrorGeneral('')
    try {
      await solicitar.mutateAsync(form)
      navigate('/mis-solicitudes')
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.errores) setErrores(err.errores as Errores)
        else setErrorGeneral(err.message)
      } else {
        setErrorGeneral('No pudimos enviar tu solicitud. Inténtalo de nuevo.')
      }
    }
  }

  if (isLoading) {
    return <p className="text-body text-muted">Cargando…</p>
  }
  if (!objeto) {
    return (
      <p className="rounded-card border border-line bg-surface p-8 text-center text-body text-muted shadow-card">
        No encontramos este objeto, o ya no está disponible.
      </p>
    )
  }

  const color = objeto.categoria_color || '#0b7a54'

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <div>
        {objeto.foto_url ? (
          <img
            src={objeto.foto_url}
            alt={objeto.nombre_objeto || 'Foto del objeto'}
            className="w-full rounded-card-lg object-cover"
          />
        ) : (
          <div
            className="flex h-64 w-full items-center justify-center rounded-card-lg"
            style={{ backgroundColor: fondoTenue(color) }}
          >
            <span className="flex h-20 w-20 items-center justify-center rounded-card bg-surface shadow-card" style={{ color }}>
              <CategoryIcon clave={objeto.categoria_icono} size={40} />
            </span>
          </div>
        )}

        <div className="mt-4 flex items-start justify-between gap-2">
          <h1 className="font-display text-heading font-bold text-ink">{objeto.nombre_objeto || 'Objeto sin nombre'}</h1>
          <BadgeEstadoObjeto estado={objeto.estado} etiqueta={objeto.estado_display} />
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          <span className="rounded-pill px-2.5 py-1 text-caption font-semibold" style={{ backgroundColor: fondoTenue(color), color }}>
            {objeto.categoria_nombre}
          </span>
          <span className="rounded-pill bg-info-wash px-2.5 py-1 text-caption font-semibold text-info">
            {objeto.sede_display}
          </span>
        </div>
        {objeto.lugar_encontrado && (
          <p className="mt-4 text-body text-muted">Encontrado en {objeto.lugar_encontrado}</p>
        )}
        {objeto.descripcion_objeto && <p className="mt-2 text-body text-muted">{objeto.descripcion_objeto}</p>}
      </div>

      <Card className="h-fit">
        {objeto.ya_solicito ? (
          <p className="text-body text-muted">
            Ya enviaste una solicitud para este objeto. Revisa el estado en{' '}
            <span className="font-medium text-ink">Mis solicitudes</span>.
          </p>
        ) : (
          <>
            <h2 className="font-display text-heading-sm font-bold text-ink">Solicitar este objeto</h2>
            <p className="mt-1 text-body text-muted">
              Necesitamos tus datos para poder emitir el formato de entrega si tu solicitud es aprobada.
            </p>
            <form onSubmit={enviar} className="mt-5 flex flex-col gap-4">
              <Textarea
                id="mensaje"
                label="¿Por qué crees que es tuyo? (opcional)"
                rows={3}
                placeholder="Es azul, tiene un sticker de… y lo perdí el lunes en la cafetería."
                value={form.mensaje}
                onChange={(evento) => actualizar('mensaje', evento.target.value)}
                error={errores.mensaje?.[0]}
              />
              <Select
                id="tipo_documento"
                label="Tipo de documento"
                value={form.tipo_documento}
                onChange={(evento) => actualizar('tipo_documento', evento.target.value)}
                error={errores.tipo_documento?.[0]}
              >
                {TIPOS_DOCUMENTO.map((tipo) => (
                  <option key={tipo.value} value={tipo.value}>
                    {tipo.label}
                  </option>
                ))}
              </Select>
              <Input
                id="numero_documento"
                label="Número de documento"
                placeholder="Ej. 1036645213"
                value={form.numero_documento}
                onChange={(evento) => actualizar('numero_documento', evento.target.value)}
                error={errores.numero_documento?.[0]}
              />
              <Input
                id="telefono"
                label="Teléfono de contacto"
                placeholder="Ej. 300 123 4567"
                value={form.telefono}
                onChange={(evento) => actualizar('telefono', evento.target.value)}
                error={errores.telefono?.[0]}
              />
              {errorGeneral && <p className="text-caption text-danger">{errorGeneral}</p>}
              <Button type="submit" variante="primario" disabled={solicitar.isPending}>
                {solicitar.isPending ? 'Enviando…' : 'Enviar solicitud'}
              </Button>
            </form>
          </>
        )}
      </Card>
    </div>
  )
}
