import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  apelarSolicitud,
  obtenerCategorias,
  obtenerMisSolicitudes,
  obtenerObjeto,
  obtenerObjetos,
  obtenerResumen,
  solicitarReclamo,
  type DatosSolicitud,
  type FiltrosObjetos,
} from '../api/estudiante'

export function useResumen() {
  return useQuery({ queryKey: ['resumen'], queryFn: obtenerResumen })
}

export function useCategorias() {
  return useQuery({ queryKey: ['categorias'], queryFn: obtenerCategorias, staleTime: 5 * 60_000 })
}

export function useObjetos(filtros: FiltrosObjetos, opciones: { enabled?: boolean } = {}) {
  return useQuery({
    queryKey: ['objetos', filtros],
    queryFn: () => obtenerObjetos(filtros),
    enabled: opciones.enabled ?? true,
  })
}

export function useObjeto(id: number) {
  return useQuery({
    queryKey: ['objeto', id],
    queryFn: () => obtenerObjeto(id),
    enabled: Number.isFinite(id),
  })
}

export function useMisSolicitudes() {
  return useQuery({ queryKey: ['mis-solicitudes'], queryFn: obtenerMisSolicitudes })
}

export function useSolicitarReclamo(objetoId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (datos: DatosSolicitud) => solicitarReclamo(objetoId, datos),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['objeto', objetoId] })
      queryClient.invalidateQueries({ queryKey: ['objetos'] })
      queryClient.invalidateQueries({ queryKey: ['mis-solicitudes'] })
    },
  })
}

export function useApelarSolicitud() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, motivo }: { id: number; motivo: string }) => apelarSolicitud(id, motivo),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mis-solicitudes'] })
    },
  })
}
