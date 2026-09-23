import { useState, type FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { API_BASE_URL, ApiError } from '../api/client'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input } from '../components/Input'
import { useAuth } from '../lib/auth-context'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [identificador, setIdentificador] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    setError('')
    setCargando(true)
    try {
      const usuario = await login(identificador, contrasena)
      const destino = (location.state as { desde?: string } | null)?.desde
      navigate(destino ?? (usuario.is_staff ? '/panel' : '/objetos'), { replace: true })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No pudimos iniciar sesión. Inténtalo de nuevo.')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-forest px-4 py-12">
      <Card className="w-full max-w-sm">
        <p className="font-mono text-caption uppercase tracking-widest text-terracota">Objetos Perdidos UNAL</p>
        <h1 className="mt-2 font-display text-heading text-ink">Bienvenido de nuevo</h1>
        <p className="mt-1 text-body text-ink-muted">Ingresa con tu correo institucional.</p>

        <form onSubmit={enviar} className="mt-6 flex flex-col gap-4">
          <Input
            id="identificador"
            label="Usuario o correo institucional"
            placeholder="correo@unal.edu.co"
            value={identificador}
            onChange={(evento) => setIdentificador(evento.target.value)}
            autoComplete="username"
            required
          />
          <Input
            id="contrasena"
            label="Contraseña"
            type="password"
            value={contrasena}
            onChange={(evento) => setContrasena(evento.target.value)}
            autoComplete="current-password"
            required
          />
          {error && <p className="text-caption text-alerta">{error}</p>}
          <Button type="submit" variante="primario" disabled={cargando}>
            {cargando ? 'Ingresando…' : 'Ingresar'}
          </Button>
        </form>

        <div className="mt-6 flex items-center gap-3 text-caption text-ink-muted">
          <span className="h-px flex-1 bg-hairline" />
          o
          <span className="h-px flex-1 bg-hairline" />
        </div>

        <a
          href={`${API_BASE_URL}/accounts/google/login/`}
          className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-pill border border-hairline px-5 py-2.5 text-body font-medium text-ink transition-colors hover:border-ink"
        >
          Continuar con Google
        </a>
      </Card>
    </div>
  )
}
