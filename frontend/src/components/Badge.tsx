import type { ReactNode } from 'react'

export type EstadoObjeto = 'disponible' | 'reclamado' | 'entregado'
export type EstadoSolicitud = 'pendiente' | 'apelada' | 'aprobada' | 'rechazada'

interface BadgeProps {
  children: ReactNode
  tono?: 'primary' | 'accent' | 'success' | 'info' | 'neutro' | 'danger'
}

const TONOS: Record<NonNullable<BadgeProps['tono']>, string> = {
  primary: 'bg-primary-wash text-primary-dark',
  accent: 'bg-accent-wash text-accent',
  success: 'bg-success-wash text-success',
  info: 'bg-info-wash text-info',
  neutro: 'bg-surface-hover text-muted',
  danger: 'bg-danger-wash text-danger',
}

export function Badge({ children, tono = 'neutro' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-pill px-3 py-1 text-caption font-semibold ${TONOS[tono]}`}>
      {children}
    </span>
  )
}

const TONO_POR_ESTADO_OBJETO: Record<EstadoObjeto, BadgeProps['tono']> = {
  disponible: 'primary',
  reclamado: 'accent',
  entregado: 'info',
}

const TONO_POR_ESTADO_SOLICITUD: Record<EstadoSolicitud, BadgeProps['tono']> = {
  pendiente: 'neutro',
  apelada: 'accent',
  aprobada: 'primary',
  rechazada: 'danger',
}

export function BadgeEstadoObjeto({ estado, etiqueta }: { estado: EstadoObjeto; etiqueta: string }) {
  return <Badge tono={TONO_POR_ESTADO_OBJETO[estado]}>{etiqueta}</Badge>
}

export function BadgeEstadoSolicitud({ estado, etiqueta }: { estado: EstadoSolicitud; etiqueta: string }) {
  return <Badge tono={TONO_POR_ESTADO_SOLICITUD[estado]}>{etiqueta}</Badge>
}
