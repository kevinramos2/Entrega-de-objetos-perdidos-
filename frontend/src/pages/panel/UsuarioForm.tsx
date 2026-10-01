import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { TIPOS_DOCUMENTO } from '../../api/estudiante'
import { ApiError } from '../../api/client'
import { aFormData } from '../../api/panel'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { Input, Select } from '../../components/Input'
import { useActualizarUsuario, useUsuario } from '../../hooks/usePanelApi'
import { useAuth } from '../../lib/auth-context'
import { useToast } from '../../lib/toast-context'

type Errores = Record<string, string[]>

export default function UsuarioForm() {
  const { id } = useParams()
  const usuarioId = Number(id)
  const navigate = useNavigate()
  const toast = useToast()
  const { usuario: usuarioActual } = useAuth()

  const { data: usuario } = useUsuario(usuarioId)
  const actualizar = useActualizarUsuario(usuarioId)

  const [form, setForm] = useState({
    username: '', email: '', first_name: '', last_name: '', rol: 'estudiante', is_active: true,
    contrasena: '', tipo_documento: 'CC', numero_documento: '', telefono: '', programa: '',
  })
  const [firma, setFirma] = useState<File | null>(null)
  const [previewFirma, setPreviewFirma] = useState<string | null>(null)
  const [errores, setErrores] = useState<Errores>({})
  const [enviando, setEnviando] = useState(false)

  const esUnoMismo = usuarioActual?.id === usuarioId

  useEffect(() => {
    if (!usuario) return
    setForm({
      username: usuario.username, email: usuario.email, first_name: usuario.first_name,
      last_name: usuario.last_name, rol: usuario.rol, is_active: usuario.is_active, contrasena: '',
      tipo_documento: usuario.perfil?.tipo_documento || 'CC', numero_documento: usuario.perfil?.numero_documento || '',
      telefono: usuario.perfil?.telefono || '', programa: usuario.perfil?.programa || '',
    })
    if (usuario.perfil?.firma_url) setPreviewFirma(usuario.perfil.firma_url)
  }, [usuario])

  function actualizarCampo<K extends keyof typeof form>(campo: K, valor: typeof form[K]) {
    setForm((p) => ({ ...p, [campo]: valor }))
  }

  function elegirFirma(archivo: File | null) {
    setFirma(archivo)
    if (archivo) setPreviewFirma(URL.createObjectURL(archivo))
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    setErrores({})
    setEnviando(true)
    try {
      await actualizar.mutateAsync(aFormData({ ...form, firma }))
      toast.mostrar('Cuenta actualizada.', 'exito')
      navigate('/panel/usuarios')
    } catch (err) {
      if (err instanceof ApiError && err.errores) setErrores(err.errores as Errores)
      else toast.mostrar('No pudimos guardar los cambios.', 'error')
    } finally {
      setEnviando(false)
    }
  }

  if (!usuario) {
    return <p className="text-body text-muted">Cargando…</p>
  }

  return (
    <div className="flex flex-col gap-6">
      <header>
        <p className="text-caption text-muted">
          <Link to="/panel/usuarios" className="hover:text-primary">Cuentas</Link> →
        </p>
        <h1 className="font-display text-heading font-bold text-ink">Editar cuenta de {usuario.username}</h1>
      </header>

      <Card className="max-w-2xl">
        {esUnoMismo && (
          <p className="mb-4 text-caption text-muted">
            Importante: es tu propia cuenta. Evita desactivarla o quitarte el rol de administrador.
          </p>
        )}
        <form onSubmit={enviar} className="flex flex-col gap-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <Input id="username" label="Usuario" value={form.username} onChange={(e) => actualizarCampo('username', e.target.value)} error={errores.username?.[0]} />
            <Input id="email" label="Correo" type="email" value={form.email} onChange={(e) => actualizarCampo('email', e.target.value)} error={errores.email?.[0]} />
            <Input id="first_name" label="Nombres" value={form.first_name} onChange={(e) => actualizarCampo('first_name', e.target.value)} />
            <Input id="last_name" label="Apellidos" value={form.last_name} onChange={(e) => actualizarCampo('last_name', e.target.value)} />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Select id="rol" label="Rol" value={form.rol} onChange={(e) => actualizarCampo('rol', e.target.value)}>
              <option value="estudiante">Estudiante</option>
              <option value="admin">Administrador</option>
            </Select>
            <label className="mt-7 flex items-center gap-2 text-body text-ink">
              <input type="checkbox" checked={form.is_active} onChange={(e) => actualizarCampo('is_active', e.target.checked)} />
              Cuenta activa
            </label>
          </div>
          <Input
            id="contrasena" label="Contraseña (dejar vacía para no cambiarla)" type="password"
            value={form.contrasena} onChange={(e) => actualizarCampo('contrasena', e.target.value)}
            error={errores.contrasena?.[0]}
          />

          <hr className="border-line" />

          <div className="grid gap-4 sm:grid-cols-2">
            <Select id="tipo_documento" label="Tipo de documento" value={form.tipo_documento} onChange={(e) => actualizarCampo('tipo_documento', e.target.value)}>
              {TIPOS_DOCUMENTO.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </Select>
            <Input id="numero_documento" label="Número de documento" value={form.numero_documento} onChange={(e) => actualizarCampo('numero_documento', e.target.value)} />
            <Input id="telefono" label="Teléfono" value={form.telefono} onChange={(e) => actualizarCampo('telefono', e.target.value)} />
            <Input id="programa" label="Programa / Carrera" value={form.programa} onChange={(e) => actualizarCampo('programa', e.target.value)} />
          </div>

          <hr className="border-line" />

          <div className="archivo-subida-firma">
            <label className="mb-1.5 block text-caption font-medium text-muted">Firma digital</label>
            <label className="archivo-subida-area block max-w-md">
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                className="hidden"
                onChange={(e) => elegirFirma(e.target.files?.[0] ?? null)}
              />
              {previewFirma ? (
                <img src={previewFirma} alt="Vista previa de la firma" className="archivo-subida-preview" />
              ) : (
                <div className="flex flex-col items-center gap-2 py-4 text-muted">
                  <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 19l7-7 3 3-7 7-3-3z" />
                    <path d="m18 13-1.5 7.5L3 4.5 8 3l10 10z" />
                    <path d="m9 14 4-4" />
                  </svg>
                  <span className="text-caption">Arrastra tu firma aquí o elige un archivo</span>
                </div>
              )}
            </label>
            <p className="mt-1.5 text-caption text-muted">
              Se estampa en los formatos de entrega. Se convierte a PNG con fondo transparente (máx. 1000 px).
            </p>
            {errores.firma && <p className="mt-1.5 text-caption text-danger">{errores.firma[0]}</p>}
          </div>

          <div className="flex gap-3">
            <Button type="submit" variante="primario" disabled={enviando}>
              {enviando ? 'Guardando…' : 'Guardar cambios'}
            </Button>
            <Button type="button" variante="ghost" onClick={() => navigate('/panel/usuarios')}>
              Cancelar
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
