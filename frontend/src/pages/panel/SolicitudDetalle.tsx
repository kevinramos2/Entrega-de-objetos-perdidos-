import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ApiError } from '../../api/client'
import { SEDES } from '../../api/estudiante'
import { descargarFormatoSolicitud } from '../../api/panel'
import { BadgeEstadoObjeto, BadgeEstadoSolicitud } from '../../components/Badge'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { useConfirmModal } from '../../components/ConfirmModal'
import { Textarea } from '../../components/Input'
import { useDecidirSolicitud, useEntregarSolicitud, useSolicitudAdmin } from '../../hooks/usePanelApi'
import { useToast } from '../../lib/toast-context'

function Dato({ etiqueta, children }: { etiqueta: string; children: React.ReactNode }) {
  return (
    <li className="flex gap-3 border-b border-dashed border-line py-2.5 text-body last:border-0">
      <b className="min-w-[110px] font-semibold text-muted">{etiqueta}</b>
      <span className="text-ink">{children}</span>
    </li>
  )
}

export default function SolicitudDetalle() {
  const { id } = useParams()
  const solicitudId = Number(id)
  const toast = useToast()
  const { confirmar, modal } = useConfirmModal()

  const { data, isLoading } = useSolicitudAdmin(solicitudId)
  const decidir = useDecidirSolicitud(solicitudId)
  const entregar = useEntregarSolicitud(solicitudId)

  const [comentario, setComentario] = useState('')
  const [datosEntrega, setDatosEntrega] = useState('')
  const [sede, setSede] = useState('')
  const [descargando, setDescargando] = useState(false)

  if (isLoading || !data) {
    return <p className="text-body text-muted">Cargando…</p>
  }

  const { solicitud, textos_entrega } = data
  const sedeElegida = sede || solicitud.objeto_detalle.sede
  const esApelacion = solicitud.estado === 'apelada'

  async function decidirSolicitud(accion: 'aprobar' | 'rechazar') {
    const ok = await confirmar({
      titulo: accion === 'aprobar' ? 'Aprobar reclamo' : 'Rechazar solicitud',
      mensaje:
        accion === 'aprobar'
          ? '¿Confirmas que el objeto es de este estudiante? El objeto pasará a estado Reclamado.'
          : esApelacion
            ? '¿Mantener el rechazo y cerrar la apelación?'
            : '¿Rechazar esta solicitud?',
      textoConfirmar: accion === 'aprobar' ? 'Aprobar' : 'Rechazar',
      tono: accion === 'aprobar' ? 'exito' : 'peligro',
    })
    if (!ok) return
    try {
      await decidir.mutateAsync({ accion, comentario, datos_entrega: datosEntrega, sede: sedeElegida })
      toast.mostrar(accion === 'aprobar' ? 'Solicitud aprobada.' : 'Solicitud rechazada.', 'exito')
    } catch (err) {
      toast.mostrar(err instanceof ApiError ? err.message : 'No pudimos registrar la decisión.', 'error')
    }
  }

  async function marcarEntregado() {
    const ok = await confirmar({
      titulo: 'Marcar como entregado',
      mensaje: '¿Confirmas que el objeto ya fue entregado a este estudiante? Esto habilitará el formato (PDF).',
      textoConfirmar: 'Marcar entregado',
      tono: 'exito',
    })
    if (!ok) return
    try {
      await entregar.mutateAsync()
      toast.mostrar('Objeto marcado como entregado.', 'exito')
    } catch (err) {
      toast.mostrar(err instanceof ApiError ? err.message : 'No pudimos registrar la entrega.', 'error')
    }
  }

  async function descargarPdf() {
    setDescargando(true)
    try {
      await descargarFormatoSolicitud(solicitudId)
    } catch (err) {
      toast.mostrar(err instanceof ApiError ? err.message : 'No pudimos generar el PDF.', 'error')
    } finally {
      setDescargando(false)
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-caption text-muted">
            <Link to="/panel/solicitudes" className="hover:text-primary">Solicitudes</Link> →
          </p>
          <h1 className="font-display text-heading font-bold text-ink">Revisión de solicitud</h1>
        </div>
        <div className="flex gap-2">
          {solicitud.esta_entregada ? (
            <Button variante="primario" onClick={descargarPdf} disabled={descargando}>
              {descargando ? 'Generando…' : 'Formato de entrega (PDF)'}
            </Button>
          ) : solicitud.estado === 'aprobada' ? (
            <Button variante="primario" onClick={marcarEntregado} disabled={entregar.isPending}>
              Marcar como entregado
            </Button>
          ) : null}
          <Link to="/panel/solicitudes">
            <Button variante="ghost">← Volver</Button>
          </Link>
        </div>
      </header>

      <div className="grid gap-5 lg:grid-cols-2">
        <Card>
          <h3 className="font-display text-body-lg font-bold text-ink">Objeto solicitado</h3>
          <ul className="mt-3">
            <Dato etiqueta="Nombre">{solicitud.objeto_detalle.nombre_objeto}</Dato>
            <Dato etiqueta="Sede">{solicitud.objeto_detalle.sede_display}</Dato>
            <Dato etiqueta="Categoría">{solicitud.objeto_detalle.categoria_nombre}</Dato>
            <Dato etiqueta="Descripción">{solicitud.objeto_detalle.descripcion_objeto || '—'}</Dato>
            <Dato etiqueta="Lugar">{solicitud.objeto_detalle.lugar_encontrado || '—'}</Dato>
            <Dato etiqueta="Estado actual">
              <BadgeEstadoObjeto estado={solicitud.objeto_detalle.estado} etiqueta={solicitud.objeto_detalle.estado_display} />
            </Dato>
          </ul>
          <Link to={`/panel/objetos/${solicitud.objeto}/editar`} className="btn btn-ghost mt-3 text-caption px-4 py-2">
            Editar objeto
          </Link>
        </Card>

        <Card>
          <h3 className="font-display text-body-lg font-bold text-ink">Estudiante</h3>
          <ul className="mt-3">
            <Dato etiqueta="Nombre">{solicitud.usuario_nombre}</Dato>
            <Dato etiqueta="Correo">{solicitud.usuario_email}</Dato>
            <Dato etiqueta="Documento">{solicitud.tipo_documento} {solicitud.numero_documento}</Dato>
            <Dato etiqueta="Teléfono">{solicitud.telefono || '—'}</Dato>
          </ul>
        </Card>
      </div>

      <Card>
        <h3 className="font-display text-body-lg font-bold text-ink">¿Por qué cree que es suyo?</h3>
        <p className="mt-2 text-body text-ink">{solicitud.mensaje || 'No dejó un mensaje adicional.'}</p>
        <p className="mt-3 text-caption text-muted">
          Solicitado el {new Date(solicitud.fecha).toLocaleString('es-CO')}
        </p>
      </Card>

      {solicitud.fue_apelada && (
        <Card className="border-l-4" style={{ borderLeftColor: '#7c3aed' }}>
          <h3 className="font-display text-body-lg font-bold text-ink">Apelación del estudiante</h3>
          <p className="mt-2 text-body text-ink">{solicitud.apelacion || 'No dejó un motivo.'}</p>
          {solicitud.fecha_apelacion && (
            <p className="mt-3 text-caption text-muted">
              Apeló el {new Date(solicitud.fecha_apelacion).toLocaleString('es-CO')} · Esta es la única apelación permitida.
            </p>
          )}
        </Card>
      )}

      {solicitud.comentario_admin && (
        <Card className="border-l-4 border-l-primary">
          <h3 className="font-display text-body-lg font-bold text-ink">Lo que se le respondió al estudiante</h3>
          <p className="mt-2 text-body text-ink">{solicitud.comentario_admin}</p>
          {solicitud.datos_entrega && (
            <>
              <h4 className="mt-4 text-caption font-bold text-ink">Datos para reclamar</h4>
              <p className="mt-1 whitespace-pre-line text-body text-ink">{solicitud.datos_entrega}</p>
            </>
          )}
        </Card>
      )}

      {solicitud.estado === 'pendiente' || solicitud.estado === 'apelada' ? (
        <Card>
          <h3 className="font-display text-body-lg font-bold text-ink">
            {esApelacion ? 'Revisión de la apelación' : 'Decisión'}
          </h3>
          <p className="mt-1 text-body text-muted">
            Escribe un comentario (opcional). Lo verá el estudiante junto al resultado.{' '}
            {esApelacion
              ? 'Al mantener el rechazo, la apelación queda cerrada y no se puede volver a apelar.'
              : 'Al aprobar, el objeto pasa a estado Reclamado y se vincula al estudiante.'}
          </p>
          <div className="mt-4 flex flex-col gap-4">
            <Textarea
              id="comentario" label="Comentario para el estudiante (opcional)" rows={3}
              placeholder="Ej. Verificamos el reporte de pérdida y no coincide con tu descripción…"
              value={comentario} onChange={(e) => setComentario(e.target.value)}
            />
            <div>
              <label className="mb-1.5 block text-caption font-medium text-muted">Sede donde se entrega el objeto</label>
              <div className="flex flex-wrap gap-2">
                {SEDES.map((s) => (
                  <label
                    key={s.value}
                    className={`flex cursor-pointer items-center gap-2 rounded-input border px-4 py-2.5 text-body font-medium transition-colors ${
                      sedeElegida === s.value ? 'border-primary bg-primary-wash text-primary-dark' : 'border-line bg-surface text-ink'
                    }`}
                  >
                    <input type="radio" className="sr-only" checked={sedeElegida === s.value} onChange={() => setSede(s.value)} />
                    {s.label}
                  </label>
                ))}
              </div>
              {textos_entrega[sedeElegida as 'minas' | 'volador'] && (
                <div className="mt-2 rounded-input bg-success-wash p-3.5">
                  <p className="text-caption font-bold uppercase tracking-wide text-success">Instrucción configurada para esta sede</p>
                  <p className="mt-1 whitespace-pre-line text-body text-ink">{textos_entrega[sedeElegida as 'minas' | 'volador']}</p>
                </div>
              )}
            </div>
            <Textarea
              id="datos_entrega" label="Datos para reclamar el objeto (opcional)" rows={3}
              placeholder="Si lo dejas vacío se usará la instrucción configurada para la sede seleccionada."
              value={datosEntrega} onChange={(e) => setDatosEntrega(e.target.value)}
            />
            <div className="flex gap-3">
              <Button variante="primario" onClick={() => decidirSolicitud('aprobar')} disabled={decidir.isPending}>
                {esApelacion ? 'Aprobar la apelación' : 'Aprobar reclamo'}
              </Button>
              <Button variante="peligro" onClick={() => decidirSolicitud('rechazar')} disabled={decidir.isPending}>
                {esApelacion ? 'Mantener rechazo' : 'Rechazar'}
              </Button>
            </div>
          </div>
        </Card>
      ) : (
        <Card className="flex flex-wrap items-center gap-4">
          <BadgeEstadoSolicitud estado={solicitud.estado} etiqueta={solicitud.estado_display} />
          {solicitud.fecha_entrega && (
            <span className="rounded-pill bg-primary-dark px-3 py-1 text-caption font-semibold text-white">
              Entregado el {solicitud.fecha_entrega}
            </span>
          )}
        </Card>
      )}
      {modal}
    </div>
  )
}
