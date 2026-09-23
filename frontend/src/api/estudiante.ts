import { apiFetch } from './client'

export interface Categoria {
  id: number
  nombre: string
  icono: string
  color: string
  orden: number
  total_disponibles?: number
}

export interface ObjetoPublico {
  id: number
  nombre_objeto: string
  categoria: number | null
  categoria_nombre: string
  categoria_icono: string
  categoria_color: string | null
  descripcion_objeto: string
  sede: 'minas' | 'volador'
  sede_display: string
  lugar_encontrado: string
  fecha_registro: string | null
  foto_url: string | null
  estado: 'disponible' | 'reclamado' | 'entregado'
  estado_display: string
  ya_solicito?: boolean
}

export interface Resumen {
  total: number
  disponibles: number
  reclamados: number
  entregados: number
  recuperados: number
  tasa_recuperacion: number
  solicitudes_pendientes: number
}

export interface Mensaje {
  tipo: string
  titulo: string
  detalle: string
}

export interface InstruccionesEntrega {
  texto_minas: string
  texto_volador: string
  fecha_actualizada: string
}

export type EstadoSolicitud = 'pendiente' | 'apelada' | 'aprobada' | 'rechazada'

export interface Solicitud {
  id: number
  objeto: number
  objeto_detalle: ObjetoPublico
  usuario: number
  usuario_nombre: string
  usuario_email: string
  mensaje: string
  tipo_documento: string
  numero_documento: string
  telefono: string
  estado: EstadoSolicitud
  estado_display: string
  fecha: string
  comentario_admin: string
  fue_apelada: boolean
  apelacion: string
  fecha_apelacion: string | null
  datos_entrega: string
  fecha_entrega: string | null
  formato_descargado: boolean
  puede_apelar: boolean
  esta_entregada: boolean
}

export const TIPOS_DOCUMENTO = [
  { value: 'CC', label: 'Cédula de ciudadanía' },
  { value: 'TI', label: 'Tarjeta de identidad' },
  { value: 'CE', label: 'Cédula de extranjería' },
  { value: 'PEP', label: 'Pasaporte' },
]

export const SEDES = [
  { value: 'minas', label: 'Sede Minas' },
  { value: 'volador', label: 'Sede El Volador' },
]

export function obtenerResumen() {
  return apiFetch<{ resumen: Resumen; mensajes: Mensaje[] }>('/api/v1/resumen/')
}

export function obtenerCategorias() {
  return apiFetch<Categoria[]>('/api/v1/categorias/')
}

export interface FiltrosObjetos {
  q?: string
  categoria?: string
  sede?: string
}

export function obtenerObjetos(filtros: FiltrosObjetos = {}) {
  const parametros = new URLSearchParams()
  if (filtros.q) parametros.set('q', filtros.q)
  if (filtros.categoria) parametros.set('categoria', filtros.categoria)
  if (filtros.sede) parametros.set('sede', filtros.sede)
  const query = parametros.toString()
  return apiFetch<ObjetoPublico[]>(`/api/v1/objetos/${query ? `?${query}` : ''}`)
}

export function obtenerObjeto(id: number) {
  return apiFetch<ObjetoPublico>(`/api/v1/objetos/${id}/`)
}

export interface DatosSolicitud {
  mensaje: string
  tipo_documento: string
  numero_documento: string
  telefono: string
}

export function solicitarReclamo(objetoId: number, datos: DatosSolicitud) {
  return apiFetch<Solicitud>(`/api/v1/objetos/${objetoId}/solicitar/`, {
    method: 'POST',
    json: datos,
  })
}

export function obtenerMisSolicitudes() {
  return apiFetch<{ solicitudes: Solicitud[]; instrucciones: InstruccionesEntrega }>(
    '/api/v1/mis-solicitudes/',
  )
}

export function apelarSolicitud(id: number, motivo: string) {
  return apiFetch<Solicitud>(`/api/v1/solicitudes/${id}/apelar/`, {
    method: 'POST',
    json: { motivo },
  })
}
