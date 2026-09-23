// "localhost" (no "127.0.0.1"): con SameSite=Lax en desarrollo, la cookie de
// refresh solo viaja entre orígenes que comparten el mismo *sitio* — puerto
// aparte, "localhost" y "127.0.0.1" cuentan como sitios distintos.
const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

let accessToken: string | null = null

export function setAccessToken(token: string | null) {
  accessToken = token
}

export function getAccessToken() {
  return accessToken
}

export class ApiError extends Error {
  status: number
  errores?: unknown

  constructor(status: number, message: string, errores?: unknown) {
    super(message)
    this.status = status
    this.errores = errores
  }
}

async function refrescarToken(): Promise<string | null> {
  try {
    const respuesta = await fetch(`${API_BASE_URL}/api/v1/auth/refresh/`, {
      method: 'POST',
      credentials: 'include',
    })
    if (!respuesta.ok) {
      accessToken = null
      return null
    }
    const datos = await respuesta.json()
    accessToken = datos.access
    return accessToken
  } catch {
    // Backend caído o sin red: se trata igual que "no hay sesión".
    accessToken = null
    return null
  }
}

interface OpcionesApi extends RequestInit {
  /** Cuerpo como JSON: se serializa y fija el Content-Type automáticamente. */
  json?: unknown
  /** Cuerpo como FormData (subida de archivos): el navegador fija el boundary. */
  form?: FormData
}

/**
 * Cliente fetch central de la SPA. Adjunta el access token en memoria, y si
 * el servidor responde 401 intenta refrescarlo una vez (con la cookie
 * HttpOnly) antes de reintentar — así una sesión sobrevive a un refresh de
 * página sin que el usuario note nada.
 */
export async function apiFetch<T = unknown>(
  path: string,
  opciones: OpcionesApi = {},
  reintentar = true,
): Promise<T> {
  const headers = new Headers(opciones.headers)
  let body: BodyInit | undefined = opciones.body ?? undefined

  if (opciones.json !== undefined) {
    headers.set('Content-Type', 'application/json')
    body = JSON.stringify(opciones.json)
  } else if (opciones.form) {
    body = opciones.form
  }

  if (accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`)
  }

  const respuesta = await fetch(`${API_BASE_URL}${path}`, {
    ...opciones,
    headers,
    body,
    credentials: 'include',
  })

  if (respuesta.status === 401 && reintentar) {
    const nuevoToken = await refrescarToken()
    if (nuevoToken) {
      return apiFetch<T>(path, opciones, false)
    }
  }

  if (!respuesta.ok) {
    let detalle = 'Ocurrió un error inesperado. Inténtalo de nuevo.'
    let errores: unknown
    try {
      const datos = await respuesta.clone().json()
      detalle = datos.detail ?? detalle
      errores = datos.errores
    } catch {
      // Respuesta sin cuerpo JSON (204, binarios, etc.)
    }
    throw new ApiError(respuesta.status, detalle, errores)
  }

  const tipo = respuesta.headers.get('Content-Type') ?? ''
  if (tipo.includes('application/json')) {
    return (await respuesta.json()) as T
  }
  return respuesta as unknown as T
}

/** Descarga un archivo binario (PDF/CSV) autenticado y dispara la descarga
 * en el navegador — un <a href> normal no puede llevar el header JWT. */
export async function descargarArchivo(path: string, nombreArchivo: string): Promise<void> {
  const respuesta = await apiFetch<Response>(path)
  const blob = await respuesta.blob()
  const url = URL.createObjectURL(blob)
  const enlace = document.createElement('a')
  enlace.href = url
  enlace.download = nombreArchivo
  document.body.appendChild(enlace)
  enlace.click()
  enlace.remove()
  URL.revokeObjectURL(url)
}

export { API_BASE_URL, refrescarToken }
