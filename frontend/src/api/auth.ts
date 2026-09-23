import { apiFetch, refrescarToken, setAccessToken } from './client'

export interface Perfil {
  tipo_documento: string
  numero_documento: string
  telefono: string
  programa: string
  firma_url: string | null
}

export interface Usuario {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_staff: boolean
  rol: 'admin' | 'estudiante'
  perfil: Perfil | null
}

interface RespuestaLogin {
  access: string
  usuario: Usuario
}

export async function iniciarSesion(identificador: string, contrasena: string): Promise<Usuario> {
  const datos = await apiFetch<RespuestaLogin>('/api/v1/auth/login/', {
    method: 'POST',
    json: { identificador, contrasena },
  })
  setAccessToken(datos.access)
  return datos.usuario
}

export async function cerrarSesion(): Promise<void> {
  await apiFetch('/api/v1/auth/logout/', { method: 'POST' }).catch(() => undefined)
  setAccessToken(null)
}

export async function obtenerUsuarioActual(): Promise<Usuario> {
  return apiFetch<Usuario>('/api/v1/auth/me/')
}

/** Intenta restaurar la sesión al cargar la app con la cookie de refresh. */
export async function restaurarSesion(): Promise<Usuario | null> {
  const token = await refrescarToken()
  if (!token) return null
  try {
    return await obtenerUsuarioActual()
  } catch {
    return null
  }
}
