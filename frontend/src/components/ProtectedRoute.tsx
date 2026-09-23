import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../lib/auth-context'

export function ProtectedRoute() {
  const { usuario, cargando } = useAuth()
  const location = useLocation()

  if (cargando) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-canvas">
        <p className="font-mono text-body text-muted">Cargando…</p>
      </div>
    )
  }
  if (!usuario) {
    return <Navigate to="/login" state={{ desde: location.pathname }} replace />
  }
  return <Outlet />
}

/** Igual que ProtectedRoute, pero además exige rol de administrador. */
export function AdminRoute() {
  const { usuario, cargando } = useAuth()
  const location = useLocation()

  if (cargando) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-canvas">
        <p className="font-mono text-body text-muted">Cargando…</p>
      </div>
    )
  }
  if (!usuario) {
    return <Navigate to="/login" state={{ desde: location.pathname }} replace />
  }
  if (!usuario.is_staff) {
    return <Navigate to="/objetos" replace />
  }
  return <Outlet />
}
