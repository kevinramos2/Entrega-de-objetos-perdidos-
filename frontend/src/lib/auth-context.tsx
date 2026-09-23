import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { cerrarSesion, iniciarSesion, restaurarSesion, type Usuario } from '../api/auth'

interface AuthContextValor {
  usuario: Usuario | null
  cargando: boolean
  login: (identificador: string, contrasena: string) => Promise<Usuario>
  logout: () => Promise<void>
  establecerUsuario: (usuario: Usuario | null) => void
}

const AuthContext = createContext<AuthContextValor | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    let vigente = true
    restaurarSesion().then((u) => {
      if (vigente) {
        setUsuario(u)
        setCargando(false)
      }
    })
    return () => {
      vigente = false
    }
  }, [])

  async function login(identificador: string, contrasena: string) {
    const u = await iniciarSesion(identificador, contrasena)
    setUsuario(u)
    return u
  }

  async function logout() {
    await cerrarSesion()
    setUsuario(null)
  }

  return (
    <AuthContext.Provider value={{ usuario, cargando, login, logout, establecerUsuario: setUsuario }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  return ctx
}
