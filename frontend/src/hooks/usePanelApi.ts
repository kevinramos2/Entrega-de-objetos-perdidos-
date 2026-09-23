import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  actualizarCategoria,
  actualizarConfiguracionEntrega,
  actualizarObjeto,
  actualizarUsuario,
  cambiarEstadoObjeto,
  crearCategoria,
  crearObjeto,
  crearUsuario,
  decidirSolicitud,
  eliminarCategoria,
  eliminarObjeto,
  eliminarObjetosSeleccion,
  entregarSolicitud,
  obtenerCategoriasAdmin,
  obtenerConfiguracionEntrega,
  obtenerDashboard,
  obtenerObjetoAdmin,
  obtenerObjetosAdmin,
  obtenerSolicitudAdmin,
  obtenerSolicitudesAdmin,
  obtenerUsuario,
  obtenerUsuarios,
  type FiltrosObjetosAdmin,
  type FiltrosSolicitudes,
  type FiltrosUsuarios,
} from '../api/panel'

export function useDashboard() {
  return useQuery({ queryKey: ['panel', 'dashboard'], queryFn: obtenerDashboard })
}

// --- Objetos ---------------------------------------------------------------

export function useObjetosAdmin(filtros: FiltrosObjetosAdmin) {
  return useQuery({ queryKey: ['panel', 'objetos', filtros], queryFn: () => obtenerObjetosAdmin(filtros) })
}

export function useObjetoAdmin(id: number) {
  return useQuery({
    queryKey: ['panel', 'objeto', id],
    queryFn: () => obtenerObjetoAdmin(id),
    enabled: Number.isFinite(id),
  })
}

function useInvalidarObjetos() {
  const queryClient = useQueryClient()
  return () => {
    queryClient.invalidateQueries({ queryKey: ['panel', 'objetos'] })
    queryClient.invalidateQueries({ queryKey: ['panel', 'dashboard'] })
  }
}

export function useCrearObjeto() {
  const invalidar = useInvalidarObjetos()
  return useMutation({ mutationFn: crearObjeto, onSuccess: invalidar })
}

export function useActualizarObjeto(id: number) {
  const invalidar = useInvalidarObjetos()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (datos: FormData) => actualizarObjeto(id, datos),
    onSuccess: () => {
      invalidar()
      queryClient.invalidateQueries({ queryKey: ['panel', 'objeto', id] })
    },
  })
}

export function useEliminarObjeto() {
  const invalidar = useInvalidarObjetos()
  return useMutation({ mutationFn: eliminarObjeto, onSuccess: invalidar })
}

export function useEliminarObjetosSeleccion() {
  const invalidar = useInvalidarObjetos()
  return useMutation({ mutationFn: eliminarObjetosSeleccion, onSuccess: invalidar })
}

export function useCambiarEstadoObjeto() {
  const invalidar = useInvalidarObjetos()
  return useMutation({
    mutationFn: ({ id, estado }: { id: number; estado: string }) => cambiarEstadoObjeto(id, estado),
    onSuccess: invalidar,
  })
}

// --- Solicitudes -------------------------------------------------------------

export function useSolicitudesAdmin(filtros: FiltrosSolicitudes) {
  return useQuery({ queryKey: ['panel', 'solicitudes', filtros], queryFn: () => obtenerSolicitudesAdmin(filtros) })
}

export function useSolicitudAdmin(id: number) {
  return useQuery({
    queryKey: ['panel', 'solicitud', id],
    queryFn: () => obtenerSolicitudAdmin(id),
    enabled: Number.isFinite(id),
  })
}

function useInvalidarSolicitudes(id?: number) {
  const queryClient = useQueryClient()
  return () => {
    queryClient.invalidateQueries({ queryKey: ['panel', 'solicitudes'] })
    queryClient.invalidateQueries({ queryKey: ['panel', 'dashboard'] })
    if (id !== undefined) queryClient.invalidateQueries({ queryKey: ['panel', 'solicitud', id] })
  }
}

export function useDecidirSolicitud(id: number) {
  const invalidar = useInvalidarSolicitudes(id)
  return useMutation({
    mutationFn: (datos: Parameters<typeof decidirSolicitud>[1]) => decidirSolicitud(id, datos),
    onSuccess: invalidar,
  })
}

export function useEntregarSolicitud(id: number) {
  const invalidar = useInvalidarSolicitudes(id)
  return useMutation({ mutationFn: () => entregarSolicitud(id), onSuccess: invalidar })
}

// --- Configuración de entrega ------------------------------------------------

export function useConfiguracionEntrega() {
  return useQuery({ queryKey: ['panel', 'configuracion-entrega'], queryFn: obtenerConfiguracionEntrega })
}

export function useActualizarConfiguracionEntrega() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: actualizarConfiguracionEntrega,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['panel', 'configuracion-entrega'] }),
  })
}

// --- Categorías ---------------------------------------------------------------

export function useCategoriasAdmin() {
  return useQuery({ queryKey: ['panel', 'categorias'], queryFn: obtenerCategoriasAdmin })
}

function useInvalidarCategorias() {
  const queryClient = useQueryClient()
  return () => {
    queryClient.invalidateQueries({ queryKey: ['panel', 'categorias'] })
    queryClient.invalidateQueries({ queryKey: ['categorias'] })
  }
}

export function useCrearCategoria() {
  const invalidar = useInvalidarCategorias()
  return useMutation({ mutationFn: crearCategoria, onSuccess: invalidar })
}

export function useActualizarCategoria() {
  const invalidar = useInvalidarCategorias()
  return useMutation({
    mutationFn: ({ id, datos }: { id: number; datos: Parameters<typeof actualizarCategoria>[1] }) =>
      actualizarCategoria(id, datos),
    onSuccess: invalidar,
  })
}

export function useEliminarCategoria() {
  const invalidar = useInvalidarCategorias()
  return useMutation({ mutationFn: eliminarCategoria, onSuccess: invalidar })
}

// --- Usuarios -------------------------------------------------------------

export function useUsuarios(filtros: FiltrosUsuarios) {
  return useQuery({ queryKey: ['panel', 'usuarios', filtros], queryFn: () => obtenerUsuarios(filtros) })
}

export function useUsuario(id: number) {
  return useQuery({
    queryKey: ['panel', 'usuario', id],
    queryFn: () => obtenerUsuario(id),
    enabled: Number.isFinite(id),
  })
}

export function useCrearUsuario() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: crearUsuario,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['panel', 'usuarios'] }),
  })
}

export function useActualizarUsuario(id: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (datos: FormData) => actualizarUsuario(id, datos),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['panel', 'usuarios'] })
      queryClient.invalidateQueries({ queryKey: ['panel', 'usuario', id] })
    },
  })
}
