import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ApiError } from '../../api/client'
import { SEDES } from '../../api/estudiante'
import { descargarFormatoObjeto, type ObjetoAdmin } from '../../api/panel'
import { BadgeEstadoObjeto } from '../../components/Badge'
import { Button } from '../../components/Button'
import { useConfirmModal } from '../../components/ConfirmModal'
import { Input, Select } from '../../components/Input'
import { useCambiarEstadoObjeto, useCategoriasAdmin, useEliminarObjeto, useObjetosAdmin } from '../../hooks/usePanelApi'
import { useToast } from '../../lib/toast-context'

const ESTADOS = [
  { value: 'disponible', label: 'Disponible' },
  { value: 'reclamado', label: 'Reclamado' },
  { value: 'entregado', label: 'Entregado' },
]

function FilaObjeto({ objeto, confirmar }: { objeto: ObjetoAdmin; confirmar: ReturnType<typeof useConfirmModal>['confirmar'] }) {
  const cambiarEstado = useCambiarEstadoObjeto()
  const eliminar = useEliminarObjeto()
  const toast = useToast()
  const [descargando, setDescargando] = useState(false)

  async function descargar() {
    setDescargando(true)
    try {
      await descargarFormatoObjeto(objeto.id)
    } catch (err) {
      toast.mostrar(err instanceof ApiError ? err.message : 'No pudimos generar el PDF.', 'error')
    } finally {
      setDescargando(false)
    }
  }

  async function cambiar(estado: string) {
    try {
      await cambiarEstado.mutateAsync({ id: objeto.id, estado })
      toast.mostrar(`El objeto pasó a «${ESTADOS.find((e) => e.value === estado)?.label}».`, 'exito')
    } catch (err) {
      toast.mostrar(err instanceof ApiError ? err.message : 'No pudimos cambiar el estado.', 'error')
    }
  }

  async function confirmarEliminar() {
    const ok = await confirmar({
      titulo: 'Eliminar objeto',
      mensaje: `¿Eliminar «${objeto.nombre_objeto || 'este objeto'}»? Esta acción no se puede deshacer.`,
      textoConfirmar: 'Eliminar',
    })
    if (!ok) return
    try {
      await eliminar.mutateAsync(objeto.id)
      toast.mostrar('Objeto eliminado.', 'exito')
    } catch {
      toast.mostrar('No pudimos eliminar el objeto.', 'error')
    }
  }

  return (
    <tr>
      <td>
        <Link to={`/panel/objetos/${objeto.id}/editar`} className="font-medium text-ink hover:text-primary">
          {objeto.nombre_objeto || 'Sin nombre'}
        </Link>
        <p className="text-caption text-muted">{objeto.categoria_nombre}</p>
      </td>
      <td className="text-caption text-muted">{objeto.sede_display}</td>
      <td>
        <select
          value={objeto.estado}
          onChange={(evento) => cambiar(evento.target.value)}
          className="rounded-input border border-line bg-surface px-2 py-1.5 text-caption text-ink"
        >
          {ESTADOS.map((estado) => (
            <option key={estado.value} value={estado.value}>
              {estado.label}
            </option>
          ))}
        </select>
      </td>
      <td>
        <BadgeEstadoObjeto estado={objeto.estado} etiqueta={objeto.estado_display} />
      </td>
      <td>
        <div className="acciones">
          {objeto.estado === 'entregado' && (
            <Button variante="ghost" tamano="sm" onClick={descargar} disabled={descargando}>
              {descargando ? 'Generando…' : 'PDF'}
            </Button>
          )}
          <Link to={`/panel/objetos/${objeto.id}/editar`}>
            <Button variante="ghost" tamano="sm" type="button">
              Editar
            </Button>
          </Link>
          <Button variante="peligro" tamano="sm" onClick={confirmarEliminar}>
            Eliminar
          </Button>
        </div>
      </td>
    </tr>
  )
}

export default function ObjetosAdmin() {
  const [q, setQ] = useState('')
  const [estado, setEstado] = useState('')
  const [categoria, setCategoria] = useState('')
  const [sede, setSede] = useState('')
  const { confirmar, modal } = useConfirmModal()

  const { data: categorias } = useCategoriasAdmin()
  const { data: objetos, isLoading } = useObjetosAdmin({ q, estado, categoria, sede })

  return (
    <div className="flex flex-col gap-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-heading font-bold text-ink">Objetos</h1>
          <p className="mt-1 text-body text-muted">{objetos?.length ?? 0} registrados con estos filtros.</p>
        </div>
        <Link to="/panel/objetos/nuevo">
          <Button variante="primario">Registrar objeto</Button>
        </Link>
      </header>

      <div className="grid gap-4 sm:grid-cols-4">
        <Input id="q" label="Buscar" value={q} onChange={(evento) => setQ(evento.target.value)} />
        <Select id="estado" label="Estado" value={estado} onChange={(evento) => setEstado(evento.target.value)}>
          <option value="">Todos</option>
          {ESTADOS.map((e) => (
            <option key={e.value} value={e.value}>
              {e.label}
            </option>
          ))}
        </Select>
        <Select id="categoria" label="Categoría" value={categoria} onChange={(evento) => setCategoria(evento.target.value)}>
          <option value="">Todas</option>
          {categorias?.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.nombre}
            </option>
          ))}
        </Select>
        <Select id="sede" label="Sede" value={sede} onChange={(evento) => setSede(evento.target.value)}>
          <option value="">Todas</option>
          {SEDES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </Select>
      </div>

      {isLoading && <p className="text-body text-muted">Cargando…</p>}

      {objetos && objetos.length === 0 && (
        <p className="rounded-card border border-line bg-surface p-8 text-center text-body text-muted shadow-card">
          No hay objetos con estos filtros.
        </p>
      )}

      {objetos && objetos.length > 0 && (
        <div className="overflow-x-auto rounded-card shadow-card">
          <table className="tabla min-w-[640px]">
            <thead>
              <tr>
                <th>Objeto</th>
                <th>Sede</th>
                <th>Cambiar estado</th>
                <th>Estado</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {objetos.map((objeto) => (
                <FilaObjeto key={objeto.id} objeto={objeto} confirmar={confirmar} />
              ))}
            </tbody>
          </table>
        </div>
      )}
      {modal}
    </div>
  )
}
