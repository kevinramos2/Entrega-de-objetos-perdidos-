import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { LogoMark } from '../components/Logo'
import { useAuth } from '../lib/auth-context'

/** Destino tras el login con Google: el backend ya dejó la cookie de
 * refresh (ver api/auth_views.py::google_auth_bridge); aquí solo esperamos
 * a que AuthProvider la use para restaurar la sesión y redirigimos. */
export default function AuthCallback() {
  const { usuario, cargando } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (cargando) return
    navigate(usuario ? (usuario.is_staff ? '/panel' : '/objetos') : '/login', { replace: true })
  }, [cargando, usuario, navigate])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-canvas">
      <LogoMark size={48} />
      <p className="font-medium text-body text-muted">Iniciando sesión…</p>
    </div>
  )
}
