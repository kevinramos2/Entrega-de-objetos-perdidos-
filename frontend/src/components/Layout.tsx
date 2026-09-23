import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth-context'
import { Button } from './Button'
import { PillNav } from './PillNav'

const ENLACES_ESTUDIANTE = [
  { etiqueta: 'Inicio', ruta: '/' },
  { etiqueta: 'Objetos', ruta: '/objetos' },
  { etiqueta: 'Mis solicitudes', ruta: '/mis-solicitudes' },
]

const ENLACES_ADMIN = [
  { etiqueta: 'Panel', ruta: '/panel' },
]

export function Layout() {
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const enlaces = usuario?.is_staff ? ENLACES_ADMIN : ENLACES_ESTUDIANTE

  async function salir() {
    await logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-paper">
      <div className="px-4 pt-6">
        <PillNav
          marca="Objetos Perdidos"
          enlaces={enlaces.map((enlace) => ({
            etiqueta: enlace.etiqueta,
            activo: location.pathname === enlace.ruta,
            onClick: () => navigate(enlace.ruta),
          }))}
          acciones={
            usuario ? (
              <Button variante="ghost-oscuro" tamano="sm" onClick={salir}>
                Salir
              </Button>
            ) : (
              <Button variante="primario" tamano="sm" onClick={() => navigate('/login')}>
                Ingresar
              </Button>
            )
          }
        />
      </div>
      <main className="mx-auto max-w-5xl px-4 py-10">
        <Outlet />
      </main>
    </div>
  )
}
