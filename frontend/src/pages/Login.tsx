import { useState, type FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { API_BASE_URL, ApiError } from '../api/client'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input } from '../components/Input'
import { LogoMark } from '../components/Logo'
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
    <div className="flex min-h-screen flex-col items-center justify-center bg-canvas px-4 py-12">
      <LogoMark size={48} />
      <Card className="mt-6 w-full max-w-sm">
        <h1 className="text-center font-display text-heading-sm font-bold text-ink">Bienvenido de nuevo</h1>
        <p className="mt-1 text-center text-body text-muted">Ingresa con tu correo institucional.</p>

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
          {error && <p className="text-caption text-danger">{error}</p>}
          <Button type="submit" variante="primario" disabled={cargando}>
            {cargando ? 'Ingresando…' : 'Ingresar'}
          </Button>
        </form>

        <div className="mt-6 flex items-center gap-3 text-caption text-muted">
          <span className="h-px flex-1 bg-line" />
          o
          <span className="h-px flex-1 bg-line" />
        </div>

        <a
          href={`${API_BASE_URL}/accounts/google/login/`}
          className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-pill border border-primary/30 px-5 py-2.5 text-body font-semibold text-primary transition-colors hover:bg-primary-wash"
        >
          Continuar con Google
        </a>
      </Card>
    </div>
  )
}
