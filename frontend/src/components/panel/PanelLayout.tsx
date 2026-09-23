import { useState, type ReactNode } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { exportarCsv } from '../../api/panel'
import { useSolicitudesAdmin } from '../../hooks/usePanelApi'
import { useAuth } from '../../lib/auth-context'
import { Button } from '../Button'
import { LogoMark } from '../Logo'

const ENLACES = [
  { etiqueta: 'Resumen', ruta: '/panel', fin: true },
  { etiqueta: 'Objetos', ruta: '/panel/objetos' },
  { etiqueta: 'Solicitudes', ruta: '/panel/solicitudes' },
  { etiqueta: 'Categorías', ruta: '/panel/categorias' },
  { etiqueta: 'Cuentas', ruta: '/panel/usuarios' },
  { etiqueta: 'Entrega', ruta: '/panel/configuracion-entrega' },
]

function EnlaceSidebar({ etiqueta, ruta, fin, contador }: { etiqueta: string; ruta: string; fin?: boolean; contador?: number }) {
  return (
    <NavLink
      to={ruta}
      end={fin}
      className={({ isActive }) =>
        `flex items-center justify-between rounded-input px-4 py-2.5 text-body font-medium transition-colors ${
          isActive ? 'bg-white/10 text-white' : 'text-on-dark-muted hover:bg-white/5 hover:text-on-dark'
        }`
      }
    >
      {etiqueta}
      {Boolean(contador) && (
        <span className="rounded-pill bg-accent px-2 py-0.5 text-caption font-semibold text-white">{contador}</span>
      )}
    </NavLink>
  )
}

function BotonExportarCsv() {
  const [cargando, setCargando] = useState(false)
  async function exportar() {
    setCargando(true)
    try {
      await exportarCsv()
    } finally {
      setCargando(false)
    }
  }
  return (
    <Button variante="ghost-oscuro" tamano="sm" className="w-full" onClick={exportar} disabled={cargando}>
      {cargando ? 'Exportando…' : 'Exportar CSV'}
    </Button>
  )
}

export function PanelLayout({ children }: { children?: ReactNode }) {
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()
  const { data } = useSolicitudesAdmin({})

  async function salir() {
    await logout()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen bg-canvas">
      <aside className="flex w-64 flex-shrink-0 flex-col gap-6 bg-dark p-5">
        <div className="flex items-center gap-2.5">
          <LogoMark size={30} />
          <div>
            <p className="font-display text-caption font-bold text-on-dark">Perdidos &amp; Encontrados</p>
            <p className="text-caption text-on-dark-muted">Panel administrativo</p>
          </div>
        </div>
        <nav className="flex flex-1 flex-col gap-1">
          {ENLACES.map((enlace) => (
            <EnlaceSidebar
              key={enlace.ruta}
              {...enlace}
              contador={enlace.ruta === '/panel/solicitudes' ? data?.conteos.por_revisar : undefined}
            />
          ))}
        </nav>
        <BotonExportarCsv />
        <div className="border-t border-dark-line pt-4">
          <p className="truncate text-caption text-on-dark-muted">{usuario?.email}</p>
          <button onClick={salir} className="mt-2 text-caption font-medium text-on-dark-muted hover:text-on-dark">
            Salir
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-x-hidden p-8">{children ?? <Outlet />}</main>
    </div>
  )
}
