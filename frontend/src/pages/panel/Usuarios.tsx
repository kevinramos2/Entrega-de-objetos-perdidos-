import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { TIPOS_DOCUMENTO } from '../../api/estudiante'
import { ApiError } from '../../api/client'
import { aFormData } from '../../api/panel'
import { Badge } from '../../components/Badge'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { Input, Select } from '../../components/Input'
import { useCrearUsuario, useUsuarios } from '../../hooks/usePanelApi'
import { useToast } from '../../lib/toast-context'

const VACIO = {
  username: '', email: '', first_name: '', last_name: '', rol: 'estudiante', is_active: true,
  contrasena: '', tipo_documento: 'CC', numero_documento: '', telefono: '', programa: '',
}

export default function Usuarios() {
  const [q, setQ] = useState('')
  const [rol, setRol] = useState('')
  const { data: usuarios, isLoading } = useUsuarios({ q, rol })
  const crear = useCrearUsuario()
  const toast = useToast()

  const [form, setForm] = useState(VACIO)
  const [errores, setErrores] = useState<Record<string, string[]>>({})

  function actualizar<K extends keyof typeof form>(campo: K, valor: typeof form[K]) {
    setForm((p) => ({ ...p, [campo]: valor }))
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    setErrores({})
    try {
      await crear.mutateAsync(aFormData(form))
      toast.mostrar(`Cuenta de ${form.username} creada.`, 'exito')
      setForm(VACIO)
    } catch (err) {
      if (err instanceof ApiError && err.errores) setErrores(err.errores as Record<string, string[]>)
      else toast.mostrar('No pudimos crear la cuenta.', 'error')
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <header>
        <p className="text-caption text-muted">Configuración</p>
        <h1 className="font-display text-heading font-bold text-ink">Gestión de cuentas</h1>
      </header>

      <div className="grid gap-5 lg:grid-cols-[1.3fr_0.7fr]">
        <div className="flex flex-col gap-4">
          <div className="flex flex-wrap gap-3">
            <Input id="q" label="" placeholder="Buscar usuario o correo…" value={q} onChange={(e) => setQ(e.target.value)} className="max-w-xs" />
            <Select id="rol" label="" value={rol} onChange={(e) => setRol(e.target.value)} className="max-w-[180px]">
              <option value="">Todos los roles</option>
              <option value="estudiante">Estudiantes</option>
              <option value="admin">Administradores</option>
            </Select>
          </div>

          <div className="overflow-x-auto rounded-card shadow-card">
            <table className="tabla min-w-[560px]">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {isLoading && <tr><td colSpan={4} className="text-center text-muted">Cargando…</td></tr>}
                {usuarios?.map((u) => (
                  <tr key={u.id}>
                    <td>
                      <div className="flex items-center gap-2.5">
                        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-caption font-bold text-white">
                          {u.username.charAt(0).toUpperCase()}
                        </span>
                        <div>
                          <b className="text-ink">{u.first_name && u.last_name ? `${u.first_name} ${u.last_name}` : u.username}</b>
                          <p className="text-caption text-muted">{u.email}</p>
                        </div>
                      </div>
                    </td>
                    <td>
                      <Badge tono={u.is_staff ? 'primary' : 'info'}>{u.is_staff ? 'Administrador' : 'Estudiante'}</Badge>
                    </td>
                    <td>
                      <Badge tono={u.is_active ? 'success' : 'danger'}>{u.is_active ? 'Activa' : 'Inactiva'}</Badge>
                    </td>
                    <td>
                      <Link to={`/panel/usuarios/${u.id}/editar`} className="btn btn-ghost text-caption px-4 py-2">
                        Editar
                      </Link>
                    </td>
                  </tr>
                ))}
                {usuarios && usuarios.length === 0 && (
                  <tr><td colSpan={4} className="text-center text-muted">No hay cuentas que coincidan.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <Card>
          <h3 className="font-display text-body-lg font-bold text-ink">Crear cuenta</h3>
          <form onSubmit={enviar} className="mt-4 flex flex-col gap-4">
            <Input id="username" label="Usuario" value={form.username} onChange={(e) => actualizar('username', e.target.value)} error={errores.username?.[0]} />
            <Input id="email" label="Correo institucional" type="email" value={form.email} onChange={(e) => actualizar('email', e.target.value)} error={errores.email?.[0]} ayuda="Estudiantes: correo @unal.edu.co" />
            <div className="grid grid-cols-2 gap-4">
              <Input id="first_name" label="Nombres" value={form.first_name} onChange={(e) => actualizar('first_name', e.target.value)} />
              <Input id="last_name" label="Apellidos" value={form.last_name} onChange={(e) => actualizar('last_name', e.target.value)} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Select id="rol" label="Rol" value={form.rol} onChange={(e) => actualizar('rol', e.target.value)}>
                <option value="estudiante">Estudiante</option>
                <option value="admin">Administrador</option>
              </Select>
              <label className="mt-7 flex items-center gap-2 text-body text-ink">
                <input type="checkbox" checked={form.is_active} onChange={(e) => actualizar('is_active', e.target.checked)} />
                Cuenta activa
              </label>
            </div>
            <Input id="contrasena" label="Contraseña" type="password" value={form.contrasena} onChange={(e) => actualizar('contrasena', e.target.value)} error={errores.contrasena?.[0]} />
            <div className="grid grid-cols-2 gap-4">
              <Select id="tipo_documento" label="Tipo de documento" value={form.tipo_documento} onChange={(e) => actualizar('tipo_documento', e.target.value)}>
                {TIPOS_DOCUMENTO.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </Select>
              <Input id="numero_documento" label="Número de documento" value={form.numero_documento} onChange={(e) => actualizar('numero_documento', e.target.value)} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Input id="telefono" label="Teléfono" value={form.telefono} onChange={(e) => actualizar('telefono', e.target.value)} />
              <Input id="programa" label="Programa / Carrera" value={form.programa} onChange={(e) => actualizar('programa', e.target.value)} />
            </div>
            <Button type="submit" variante="primario" disabled={crear.isPending}>
              {crear.isPending ? 'Creando…' : 'Crear cuenta'}
            </Button>
          </form>
        </Card>
      </div>
    </div>
  )
}
