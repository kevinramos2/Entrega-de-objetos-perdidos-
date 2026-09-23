import type { Perfil } from './auth'
import { apiFetch, descargarArchivo } from './client'
import type { Categoria, EstadoSolicitud, InstruccionesEntrega, Resumen, Solicitud } from './estudiante'

export interface ObjetoAdmin {
  id: number
  nombre_objeto: string
  categoria: number | null
  categoria_nombre: string
  descripcion_objeto: string
  sede: 'minas' | 'volador'
  sede_display: string
  lugar_encontrado: string
  fecha_registro: string | null
  foto_url: string | null
  estado: 'disponible' | 'reclamado' | 'entregado'
  estado_display: string
  registrado_por_nombre: string
  nombre_persona: string
  tipo_documento: string
  numero_documento: string
  telefono: string
  suministro_correo: boolean
  correo: string | null
  fecha_entrega: string | null
  responsable_entrega: string
}

export interface UsuarioAdmin {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_staff: boolean
  is_active: boolean
  rol: 'admin' | 'estudiante'
  perfil: Perfil | null
}

export interface DashboardData {
  resumen: Resumen
  por_categoria: { categoria__nombre: string | null; categoria__icono: string; categoria__color: string; total: number }[]
  por_estado: { estado: string; total: number }[]
  por_mes: { mes: string; total: number }[]
  actividad: { objetos: ObjetoAdmin[]; solicitudes: Solicitud[] }
}

/** Convierte un objeto plano a FormData (para los formularios que aceptan
 * una foto/firma, tal como los espera el ``Form`` de Django del otro lado). */
export function aFormData(datos: Record<string, string | number | boolean | File | null | undefined>): FormData {
  const form = new FormData()
  for (const [clave, valor] of Object.entries(datos)) {
    if (valor === undefined || valor === null) continue
    if (valor instanceof File) form.append(clave, valor)
    else form.append(clave, String(valor))
  }
  return form
}

export function obtenerDashboard() {
  return apiFetch<DashboardData>('/api/v1/panel/dashboard/')
}

export interface FiltrosObjetosAdmin {
  q?: string
  estado?: string
  categoria?: string
  sede?: string
}

export function obtenerObjetosAdmin(filtros: FiltrosObjetosAdmin = {}) {
  const parametros = new URLSearchParams()
  if (filtros.q) parametros.set('q', filtros.q)
  if (filtros.estado) parametros.set('estado', filtros.estado)
  if (filtros.categoria) parametros.set('categoria', filtros.categoria)
  if (filtros.sede) parametros.set('sede', filtros.sede)
  const query = parametros.toString()
  return apiFetch<ObjetoAdmin[]>(`/api/v1/panel/objetos/${query ? `?${query}` : ''}`)
}

export function obtenerObjetoAdmin(id: number) {
  return apiFetch<ObjetoAdmin>(`/api/v1/panel/objetos/${id}/`)
}

export function crearObjeto(datos: FormData) {
  return apiFetch<ObjetoAdmin>('/api/v1/panel/objetos/', { method: 'POST', form: datos })
}

export function actualizarObjeto(id: number, datos: FormData) {
  return apiFetch<ObjetoAdmin>(`/api/v1/panel/objetos/${id}/`, { method: 'PUT', form: datos })
}

export function eliminarObjeto(id: number) {
  return apiFetch<void>(`/api/v1/panel/objetos/${id}/`, { method: 'DELETE' })
}

export function eliminarObjetosSeleccion(ids: number[]) {
  return apiFetch<{ eliminados: number }>('/api/v1/panel/objetos/eliminar-seleccion/', {
    method: 'POST',
    json: { ids: ids.join(',') },
  })
}

export function cambiarEstadoObjeto(id: number, estado: string) {
  return apiFetch<ObjetoAdmin>(`/api/v1/panel/objetos/${id}/estado/`, { method: 'POST', json: { estado } })
}

export function descargarFormatoObjeto(id: number) {
  return descargarArchivo(`/api/v1/panel/objetos/${id}/formato/`, `formato_entrega_${id}.pdf`)
}

export interface FiltrosSolicitudes {
  estado?: string
}

export function obtenerSolicitudesAdmin(filtros: FiltrosSolicitudes = {}) {
  const parametros = new URLSearchParams()
  if (filtros.estado) parametros.set('estado', filtros.estado)
  const query = parametros.toString()
  return apiFetch<{
    solicitudes: Solicitud[]
    conteos: Record<'pendiente' | 'apelada' | 'aprobada' | 'rechazada' | 'por_revisar', number>
  }>(`/api/v1/panel/solicitudes/${query ? `?${query}` : ''}`)
}

export function obtenerSolicitudAdmin(id: number) {
  return apiFetch<{ solicitud: Solicitud; textos_entrega: { minas: string; volador: string } }>(
    `/api/v1/panel/solicitudes/${id}/`,
  )
}

export function decidirSolicitud(
  id: number,
  datos: { accion: 'aprobar' | 'rechazar'; comentario?: string; datos_entrega?: string; sede?: string },
) {
  return apiFetch<Solicitud>(`/api/v1/panel/solicitudes/${id}/decidir/`, { method: 'POST', json: datos })
}

export function entregarSolicitud(id: number) {
  return apiFetch<Solicitud>(`/api/v1/panel/solicitudes/${id}/entregar/`, { method: 'POST' })
}

export function descargarFormatoSolicitud(id: number) {
  return descargarArchivo(`/api/v1/panel/solicitudes/${id}/formato/`, `formato_entrega_${id}.pdf`)
}

export function obtenerConfiguracionEntrega() {
  return apiFetch<InstruccionesEntrega>('/api/v1/panel/configuracion-entrega/')
}

export function actualizarConfiguracionEntrega(datos: { texto_minas: string; texto_volador: string }) {
  return apiFetch<InstruccionesEntrega>('/api/v1/panel/configuracion-entrega/', { method: 'PUT', json: datos })
}

export function obtenerCategoriasAdmin() {
  return apiFetch<(Categoria & { total_objetos: number })[]>('/api/v1/panel/categorias/')
}

export function crearCategoria(datos: { nombre: string; icono?: string; color: string; orden?: number }) {
  return apiFetch<Categoria>('/api/v1/panel/categorias/', { method: 'POST', json: datos })
}

export function actualizarCategoria(id: number, datos: { nombre: string; icono?: string; color: string; orden?: number }) {
  return apiFetch<Categoria>(`/api/v1/panel/categorias/${id}/`, { method: 'PUT', json: datos })
}

export function eliminarCategoria(id: number) {
  return apiFetch<void>(`/api/v1/panel/categorias/${id}/`, { method: 'DELETE' })
}

export interface FiltrosUsuarios {
  q?: string
  rol?: string
}

export function obtenerUsuarios(filtros: FiltrosUsuarios = {}) {
  const parametros = new URLSearchParams()
  if (filtros.q) parametros.set('q', filtros.q)
  if (filtros.rol) parametros.set('rol', filtros.rol)
  const query = parametros.toString()
  return apiFetch<UsuarioAdmin[]>(`/api/v1/panel/usuarios/${query ? `?${query}` : ''}`)
}

export function obtenerUsuario(id: number) {
  return apiFetch<UsuarioAdmin>(`/api/v1/panel/usuarios/${id}/`)
}

export function crearUsuario(datos: FormData) {
  return apiFetch<UsuarioAdmin>('/api/v1/panel/usuarios/', { method: 'POST', form: datos })
}

export function actualizarUsuario(id: number, datos: FormData) {
  return apiFetch<UsuarioAdmin>(`/api/v1/panel/usuarios/${id}/`, { method: 'PUT', form: datos })
}

export function exportarCsv() {
  const fecha = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  return descargarArchivo('/api/v1/panel/exportar-csv/', `objetos_${fecha}.csv`)
}

export type { EstadoSolicitud }
