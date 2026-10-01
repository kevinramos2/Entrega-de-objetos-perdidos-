import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { SEDES } from '../../api/estudiante'
import { ApiError } from '../../api/client'
import { aFormData } from '../../api/panel'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { CategoryIcon } from '../../components/CategoryIcon'
import { Input, Select, Textarea } from '../../components/Input'
import { useCategoriasAdmin, useCrearObjeto, useActualizarObjeto, useObjetoAdmin } from '../../hooks/usePanelApi'
import { useToast } from '../../lib/toast-context'

const TIPOS_DOCUMENTO_OBJETO = [
  { value: 'CC', label: 'Cédula de ciudadanía' },
  { value: 'TI', label: 'Tarjeta de identidad' },
  { value: 'CE', label: 'Cédula de extranjería' },
]

type Errores = Record<string, string[]>

export default function ObjetoForm() {
  const { id } = useParams()
  const esNuevo = !id
  const objetoId = Number(id)
  const navigate = useNavigate()
  const toast = useToast()

  const { data: categorias } = useCategoriasAdmin()
  const { data: objeto } = useObjetoAdmin(objetoId)
  const crear = useCrearObjeto()
  const actualizar = useActualizarObjeto(objetoId)

  const [form, setForm] = useState({
    nombre_objeto: '', descripcion_objeto: '', categoria: '', sede: 'minas', lugar_encontrado: '',
    estado: 'disponible', fecha_registro: '', nombre_persona: '', tipo_documento: 'CC',
    numero_documento: '', telefono: '', correo: '', fecha_entrega: '', responsable_entrega: '',
    suministro_correo: false,
  })
  const [foto, setFoto] = useState<File | null>(null)
  const [previewFoto, setPreviewFoto] = useState<string | null>(null)
  const [errores, setErrores] = useState<Errores>({})
  const [enviando, setEnviando] = useState(false)

  useEffect(() => {
    if (!objeto) return
    setForm({
      nombre_objeto: objeto.nombre_objeto, descripcion_objeto: objeto.descripcion_objeto,
      categoria: objeto.categoria ? String(objeto.categoria) : '', sede: objeto.sede,
      lugar_encontrado: objeto.lugar_encontrado, estado: objeto.estado,
      fecha_registro: objeto.fecha_registro ?? '', nombre_persona: objeto.nombre_persona,
      tipo_documento: objeto.tipo_documento || 'CC', numero_documento: objeto.numero_documento,
      telefono: objeto.telefono, correo: objeto.correo ?? '', fecha_entrega: objeto.fecha_entrega ?? '',
      responsable_entrega: objeto.responsable_entrega, suministro_correo: objeto.suministro_correo,
    })
    if (objeto.foto_url) setPreviewFoto(objeto.foto_url)
  }, [objeto])

  function actualizarCampo<K extends keyof typeof form>(campo: K, valor: typeof form[K]) {
    setForm((previo) => ({ ...previo, [campo]: valor }))
  }

  function elegirFoto(archivo: File | null) {
    setFoto(archivo)
    if (archivo) setPreviewFoto(URL.createObjectURL(archivo))
  }

  const requiereReclamante = form.estado === 'reclamado' || form.estado === 'entregado'

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    setErrores({})
    setEnviando(true)
    try {
      const datos = aFormData({
        nombre_objeto: form.nombre_objeto,
        descripcion_objeto: form.descripcion_objeto,
        categoria: form.categoria,
        sede: form.sede,
        lugar_encontrado: form.lugar_encontrado,
        estado: esNuevo ? 'disponible' : form.estado,
        fecha_registro: form.fecha_registro,
        foto,
        nombre_persona: requiereReclamante ? form.nombre_persona : '',
        tipo_documento: requiereReclamante ? form.tipo_documento : '',
        numero_documento: requiereReclamante ? form.numero_documento : '',
        telefono: requiereReclamante ? form.telefono : '',
        correo: requiereReclamante ? form.correo : '',
        fecha_entrega: requiereReclamante ? form.fecha_entrega : '',
        responsable_entrega: requiereReclamante ? form.responsable_entrega : '',
        suministro_correo: requiereReclamante ? form.suministro_correo : false,
      })
      if (esNuevo) {
        await crear.mutateAsync(datos)
        toast.mostrar('Objeto registrado correctamente.', 'exito')
      } else {
        await actualizar.mutateAsync(datos)
        toast.mostrar('Los cambios fueron guardados.', 'exito')
      }
      navigate('/panel/objetos')
    } catch (err) {
      if (err instanceof ApiError && err.errores) setErrores(err.errores as Errores)
      else toast.mostrar('No pudimos guardar el objeto.', 'error')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <header>
        <p className="text-caption text-muted">Objetos →</p>
        <h1 className="font-display text-heading font-bold text-ink">
          {esNuevo ? 'Registrar nuevo objeto' : 'Editar objeto'}
        </h1>
      </header>

      <Card>
        <form onSubmit={enviar} className="flex flex-col gap-5">
          <div>
            <label className="mb-1.5 block text-caption font-medium text-muted">Foto</label>
            <label className="archivo-subida-area block">
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(evento) => elegirFoto(evento.target.files?.[0] ?? null)}
              />
              {previewFoto ? (
                <img src={previewFoto} alt="Vista previa" className="archivo-subida-preview" />
              ) : (
                <div className="flex flex-col items-center gap-2 py-6 text-muted">
                  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21 15 16 10 5 21" />
                  </svg>
                  <span className="text-caption">Elige una imagen (JPG, PNG o WEBP · máx. 5 MB)</span>
                </div>
              )}
            </label>
            {errores.foto && <p className="mt-1.5 text-caption text-danger">{errores.foto[0]}</p>}
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              id="nombre_objeto" label="Nombre del objeto" placeholder="Ej. Termo negro 500 ml"
              value={form.nombre_objeto} onChange={(e) => actualizarCampo('nombre_objeto', e.target.value)}
              error={errores.nombre_objeto?.[0]}
            />
            <Textarea
              id="descripcion_objeto" label="Descripción" rows={1}
              placeholder="Color, marca, señas particulares…"
              value={form.descripcion_objeto} onChange={(e) => actualizarCampo('descripcion_objeto', e.target.value)}
              error={errores.descripcion_objeto?.[0]}
            />
          </div>

          <div>
            <label className="mb-1.5 block text-caption font-medium text-muted">Categoría</label>
            <div className="flex flex-wrap justify-center gap-3">
              {categorias?.map((cat) => (
                <button
                  key={cat.id}
                  type="button"
                  onClick={() => actualizarCampo('categoria', String(cat.id))}
                  className={`flex w-24 flex-col items-center gap-2 rounded-card border p-3 text-center transition-all ${
                    form.categoria === String(cat.id)
                      ? 'border-primary bg-primary-wash shadow-card'
                      : 'border-line bg-surface hover:border-primary/40'
                  }`}
                >
                  <span
                    className="flex h-11 w-11 items-center justify-center rounded-input text-white"
                    style={{ backgroundColor: cat.color }}
                  >
                    <CategoryIcon clave={cat.icono} size={22} />
                  </span>
                  <span className="text-caption font-medium text-ink">{cat.nombre}</span>
                </button>
              ))}
            </div>
            {errores.categoria && <p className="mt-1.5 text-center text-caption text-danger">{errores.categoria[0]}</p>}
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Select id="sede" label="Sede" value={form.sede} onChange={(e) => actualizarCampo('sede', e.target.value)}>
              {SEDES.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </Select>
            <Input
              id="lugar_encontrado" label="Lugar donde fue encontrado" placeholder="Ej. Biblioteca, bloque 2…"
              value={form.lugar_encontrado} onChange={(e) => actualizarCampo('lugar_encontrado', e.target.value)}
              error={errores.lugar_encontrado?.[0]}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {esNuevo ? (
              <div>
                <label className="mb-1.5 block text-caption font-medium text-muted">Estado</label>
                <p className="rounded-input border border-line bg-surface-hover px-4 py-2.5 text-body text-ink">Disponible</p>
              </div>
            ) : (
              <Select id="estado" label="Estado" value={form.estado} onChange={(e) => actualizarCampo('estado', e.target.value)}>
                <option value="disponible">Disponible</option>
                <option value="reclamado">Reclamado</option>
                <option value="entregado">Entregado</option>
              </Select>
            )}
            <Input
              id="fecha_registro" label="Fecha en que fue encontrado" type="date"
              value={form.fecha_registro} onChange={(e) => actualizarCampo('fecha_registro', e.target.value)}
              error={errores.fecha_registro?.[0]}
            />
          </div>

          {requiereReclamante ? (
            <>
              <hr className="border-line" />
              <h3 className="font-display text-body-lg font-bold text-ink">Datos de la persona que reclama</h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <Input id="nombre_persona" label="Nombre de quien reclama" value={form.nombre_persona} onChange={(e) => actualizarCampo('nombre_persona', e.target.value)} error={errores.nombre_persona?.[0]} />
                <Select id="tipo_documento" label="Tipo de documento" value={form.tipo_documento} onChange={(e) => actualizarCampo('tipo_documento', e.target.value)}>
                  {TIPOS_DOCUMENTO_OBJETO.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </Select>
                <Input id="numero_documento" label="Número de documento" value={form.numero_documento} onChange={(e) => actualizarCampo('numero_documento', e.target.value)} error={errores.numero_documento?.[0]} />
                <Input id="telefono" label="Teléfono" value={form.telefono} onChange={(e) => actualizarCampo('telefono', e.target.value)} error={errores.telefono?.[0]} />
                <Input id="correo" label="Correo" type="email" value={form.correo} onChange={(e) => actualizarCampo('correo', e.target.value)} error={errores.correo?.[0]} />
                <Input id="fecha_entrega" label="Fecha de entrega" type="date" value={form.fecha_entrega} onChange={(e) => actualizarCampo('fecha_entrega', e.target.value)} />
                <Input id="responsable_entrega" label="Responsable de la entrega" value={form.responsable_entrega} onChange={(e) => actualizarCampo('responsable_entrega', e.target.value)} />
                <label className="mt-7 flex items-center gap-2 text-body text-ink">
                  <input type="checkbox" checked={form.suministro_correo} onChange={(e) => actualizarCampo('suministro_correo', e.target.checked)} />
                  ¿Suministró correo?
                </label>
              </div>
            </>
          ) : (
            <p className="text-caption text-muted">
              El objeto se registrará como <b className="text-ink">Disponible</b>. Cuando alguien lo reclame y la
              solicitud sea aprobada, aquí podrás registrar los datos de la persona que lo reclama.
            </p>
          )}

          <div className="flex gap-3">
            <Button type="submit" variante="primario" disabled={enviando}>
              {enviando ? 'Guardando…' : 'Guardar'}
            </Button>
            <Button type="button" variante="ghost" onClick={() => navigate('/panel/objetos')}>
              Cancelar
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
