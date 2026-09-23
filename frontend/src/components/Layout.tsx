import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth-context'
import { Button } from './Button'
import { TopNav } from './TopNav'

const ENLACES_ESTUDIANTE = [
  { etiqueta: 'Inicio', ruta: '/' },
  { etiqueta: 'Objetos perdidos', ruta: '/objetos' },
  { etiqueta: 'Mis reclamos', ruta: '/mis-solicitudes' },
]

export function Layout() {
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  async function salir() {
    await logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-canvas">
      <TopNav
        enlaces={ENLACES_ESTUDIANTE.map((enlace) => ({
          etiqueta: enlace.etiqueta,
          activo: location.pathname === enlace.ruta,
          onClick: () => navigate(enlace.ruta),
        }))}
        acciones={
          usuario ? (
            <>
              {usuario.is_staff && (
                <Button variante="primario" tamano="sm" onClick={() => navigate('/panel')}>
                  Panel de administración
                </Button>
              )}
              <span
                className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-wash text-caption font-bold text-primary-dark"
                title={usuario.first_name || usuario.username}
              >
                {(usuario.first_name || usuario.username).charAt(0).toUpperCase()}
              </span>
              <button onClick={salir} className="text-caption font-medium text-ink-soft hover:text-ink">
                Salir
              </button>
            </>
          ) : (
            <Button variante="primario" tamano="sm" onClick={() => navigate('/login')}>
              Iniciar sesión
            </Button>
          )
        }
      />
      <main className="mx-auto max-w-5xl px-4 py-10">
        <Outlet />
      </main>
    </div>
  )
}
