import { useState } from 'react'
import { Link } from 'react-router-dom'
import { descargarFormatoObjeto, type ObjetoAdmin } from '../../api/panel'
import { SEDES } from '../../api/estudiante'
import { BadgeEstadoObjeto } from '../../components/Badge'
import { Button } from '../../components/Button'
import { Input, Select } from '../../components/Input'
import { useCategoriasAdmin } from '../../hooks/usePanelApi'
import { useCambiarEstadoObjeto, useEliminarObjeto, useObjetosAdmin } from '../../hooks/usePanelApi'

const ESTADOS = [
  { value: 'disponible', label: 'Disponible' },
  { value: 'reclamado', label: 'Reclamado' },
  { value: 'entregado', label: 'Entregado' },
]

function FilaObjeto({ objeto }: { objeto: ObjetoAdmin }) {
  const cambiarEstado = useCambiarEstadoObjeto()
  const eliminar = useEliminarObjeto()
  const [descargando, setDescargando] = useState(false)

  async function descargar() {
    setDescargando(true)
    try {
      await descargarFormatoObjeto(objeto.id)
    } finally {
      setDescargando(false)
    }
  }

  function confirmarEliminar() {
    if (window.confirm(`¿Eliminar «${objeto.nombre_objeto || 'este objeto'}»? Esta acción no se puede deshacer.`)) {
      eliminar.mutate(objeto.id)
    }
  }

  return (
    <tr className="border-b border-line text-body">
      <td className="py-3 pr-4">
        <Link to={`/panel/objetos/${objeto.id}/editar`} className="font-medium text-ink hover:text-primary">
          {objeto.nombre_objeto || 'Sin nombre'}
        </Link>
        <p className="text-caption text-muted">{objeto.categoria_nombre}</p>
      </td>
      <td className="py-3 pr-4 text-caption text-muted">{objeto.sede_display}</td>
      <td className="py-3 pr-4">
        <select
          value={objeto.estado}
          onChange={(evento) => cambiarEstado.mutate({ id: objeto.id, estado: evento.target.value })}
          className="rounded-input border border-line bg-surface px-2 py-1 text-caption text-ink"
        >
          {ESTADOS.map((estado) => (
            <option key={estado.value} value={estado.value}>
              {estado.label}
            </option>
          ))}
        </select>
      </td>
      <td className="py-3 pr-4">
        <BadgeEstadoObjeto estado={objeto.estado} etiqueta={objeto.estado_display} />
      </td>
      <td className="py-3 text-right">
        <div className="flex justify-end gap-2">
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

  const { data: categorias } = useCategoriasAdmin()
  const { data: objetos, isLoading } = useObjetosAdmin({ q, estado, categoria, sede })

  return (
    <div className="flex flex-col gap-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-heading text-ink">Objetos</h1>
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

      {objetos && (
        <div className="overflow-x-auto rounded-card border border-line bg-surface">
          <table className="w-full min-w-[640px] px-2">
            <thead>
              <tr className="border-b border-line text-left text-caption uppercase tracking-wide text-muted">
                <th className="px-4 py-3 font-medium">Objeto</th>
                <th className="px-4 py-3 font-medium">Sede</th>
                <th className="px-4 py-3 font-medium">Cambiar estado</th>
                <th className="px-4 py-3 font-medium">Estado</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="px-4">
              {objetos.map((objeto) => (
                <FilaObjeto key={objeto.id} objeto={objeto} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
