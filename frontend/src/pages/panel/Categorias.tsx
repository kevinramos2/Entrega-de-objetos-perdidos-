import { useState, type FormEvent } from 'react'
import { ApiError } from '../../api/client'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { CategoryIcon } from '../../components/CategoryIcon'
import { useConfirmModal } from '../../components/ConfirmModal'
import { Input, Select } from '../../components/Input'
import { useCategoriasAdmin, useActualizarCategoria, useCrearCategoria, useEliminarCategoria } from '../../hooks/usePanelApi'
import { useToast } from '../../lib/toast-context'

const OPCIONES_ICONO = [
  { value: 'otros', label: 'Genérico' },
  { value: 'termo', label: 'Termo / bebida' },
  { value: 'documento', label: 'Documentos' },
  { value: 'cargador', label: 'Cargador' },
  { value: 'tecnologia', label: 'Tecnología' },
  { value: 'lonchera', label: 'Lonchera' },
  { value: 'comida', label: 'Comida' },
  { value: 'sombrilla', label: 'Sombrilla' },
  { value: 'cartuchera', label: 'Cartuchera' },
  { value: 'ropa', label: 'Ropa y accesorios' },
  { value: 'libros', label: 'Libros y cuadernos' },
  { value: 'llaves', label: 'Llaves' },
]

const VACIO = { nombre: '', icono: 'otros', color: '#0b7a54', orden: 0 }

export default function Categorias() {
  const { data: categorias, isLoading } = useCategoriasAdmin()
  const crear = useCrearCategoria()
  const actualizar = useActualizarCategoria()
  const eliminar = useEliminarCategoria()
  const toast = useToast()
  const { confirmar, modal } = useConfirmModal()

  const [editandoId, setEditandoId] = useState<number | null>(null)
  const [form, setForm] = useState(VACIO)
  const [errores, setErrores] = useState<Record<string, string[]>>({})

  function editar(categoria: { id: number; nombre: string; icono: string; color: string; orden: number }) {
    setEditandoId(categoria.id)
    setForm({ nombre: categoria.nombre, icono: categoria.icono, color: categoria.color, orden: categoria.orden })
    setErrores({})
  }

  function cancelar() {
    setEditandoId(null)
    setForm(VACIO)
    setErrores({})
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    setErrores({})
    try {
      if (editandoId) {
        await actualizar.mutateAsync({ id: editandoId, datos: form })
        toast.mostrar('Categoría actualizada.', 'exito')
      } else {
        await crear.mutateAsync(form)
        toast.mostrar('Categoría creada.', 'exito')
      }
      cancelar()
    } catch (err) {
      if (err instanceof ApiError && err.errores) setErrores(err.errores as Record<string, string[]>)
      else toast.mostrar('No pudimos guardar la categoría.', 'error')
    }
  }

  async function eliminarCategoria(id: number, nombre: string, totalObjetos: number) {
    if (totalObjetos > 0) {
      toast.mostrar('No puedes eliminar una categoría que tiene objetos.', 'error')
      return
    }
    const ok = await confirmar({ titulo: 'Eliminar categoría', mensaje: `¿Eliminar «${nombre}»?`, textoConfirmar: 'Eliminar' })
    if (!ok) return
    try {
      await eliminar.mutateAsync(id)
      toast.mostrar('Categoría eliminada.', 'exito')
    } catch {
      toast.mostrar('No pudimos eliminar la categoría.', 'error')
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <header>
        <p className="text-caption text-muted">Configuración</p>
        <h1 className="font-display text-heading font-bold text-ink">Categorías</h1>
      </header>

      <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="overflow-x-auto rounded-card shadow-card">
          <table className="tabla min-w-[480px]">
            <thead>
              <tr>
                <th>Ícono</th>
                <th>Nombre</th>
                <th>Objetos</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr><td colSpan={4} className="text-center text-muted">Cargando…</td></tr>
              )}
              {categorias?.map((cat) => (
                <tr key={cat.id}>
                  <td>
                    <span
                      className="flex h-9 w-9 items-center justify-center rounded-input text-white"
                      style={{ backgroundColor: cat.color }}
                    >
                      <CategoryIcon clave={cat.icono} size={18} />
                    </span>
                  </td>
                  <td className="font-semibold text-ink">{cat.nombre}</td>
                  <td className="text-muted">{cat.total_objetos}</td>
                  <td>
                    <div className="acciones">
                      <Button variante="ghost" tamano="sm" onClick={() => editar(cat)}>Editar</Button>
                      <Button variante="peligro" tamano="sm" onClick={() => eliminarCategoria(cat.id, cat.nombre, cat.total_objetos)}>
                        Eliminar
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
              {categorias && categorias.length === 0 && (
                <tr><td colSpan={4} className="text-center text-muted">Aún no hay categorías.</td></tr>
              )}
            </tbody>
          </table>
        </div>

        <Card>
          <h3 className="font-display text-body-lg font-bold text-ink">
            {editandoId ? 'Editar categoría' : 'Nueva categoría'}
          </h3>
          <form onSubmit={enviar} className="mt-4 flex flex-col gap-4">
            <Input
              id="nombre" label="Nombre" value={form.nombre}
              onChange={(e) => setForm((p) => ({ ...p, nombre: e.target.value }))}
              error={errores.nombre?.[0]}
            />
            <div className="flex items-end gap-3">
              <div className="flex-1">
                <Select
                  id="icono" label="Ícono" value={form.icono}
                  onChange={(e) => setForm((p) => ({ ...p, icono: e.target.value }))}
                >
                  {OPCIONES_ICONO.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </Select>
              </div>
              <span
                className="mb-0.5 flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-input text-white"
                style={{ backgroundColor: form.color }}
              >
                <CategoryIcon clave={form.icono} size={20} />
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="mb-1.5 block text-caption font-medium text-muted" htmlFor="color">Color</label>
                <input
                  id="color" type="color" value={form.color}
                  onChange={(e) => setForm((p) => ({ ...p, color: e.target.value }))}
                  className="h-[42px] w-full cursor-pointer rounded-input border border-line bg-surface"
                />
              </div>
              <Input
                id="orden" label="Orden" type="number" value={form.orden}
                onChange={(e) => setForm((p) => ({ ...p, orden: Number(e.target.value) || 0 }))}
              />
            </div>
            <div className="flex gap-3">
              <Button type="submit" variante="primario" className="flex-1">
                {editandoId ? 'Guardar cambios' : 'Crear categoría'}
              </Button>
              {editandoId && (
                <Button type="button" variante="ghost" onClick={cancelar}>Cancelar</Button>
              )}
            </div>
          </form>
        </Card>
      </div>
      {modal}
    </div>
  )
}
