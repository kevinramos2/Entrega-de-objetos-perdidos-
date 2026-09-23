import type { ReactNode } from 'react'

export type EstadoObjeto = 'disponible' | 'reclamado' | 'entregado'
export type EstadoSolicitud = 'pendiente' | 'apelada' | 'aprobada' | 'rechazada'

interface BadgeProps {
  children: ReactNode
  tono?: 'terracota' | 'salvia' | 'neutro' | 'alerta'
}

const TONOS: Record<NonNullable<BadgeProps['tono']>, string> = {
  terracota: 'bg-terracota-wash text-terracota-hover',
  salvia: 'bg-salvia-wash text-salvia',
  neutro: 'bg-mist text-ink-muted',
  alerta: 'bg-alerta-wash text-alerta',
}

export function Badge({ children, tono = 'neutro' }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-pill px-3 py-1 text-caption font-mono font-medium ${TONOS[tono]}`}
    >
      {children}
    </span>
  )
}

const TONO_POR_ESTADO_OBJETO: Record<EstadoObjeto, BadgeProps['tono']> = {
  disponible: 'terracota',
  reclamado: 'neutro',
  entregado: 'salvia',
}

const TONO_POR_ESTADO_SOLICITUD: Record<EstadoSolicitud, BadgeProps['tono']> = {
  pendiente: 'neutro',
  apelada: 'terracota',
  aprobada: 'salvia',
  rechazada: 'alerta',
}

export function BadgeEstadoObjeto({ estado, etiqueta }: { estado: EstadoObjeto; etiqueta: string }) {
  return <Badge tono={TONO_POR_ESTADO_OBJETO[estado]}>{etiqueta}</Badge>
}

export function BadgeEstadoSolicitud({ estado, etiqueta }: { estado: EstadoSolicitud; etiqueta: string }) {
  return <Badge tono={TONO_POR_ESTADO_SOLICITUD[estado]}>{etiqueta}</Badge>
}
