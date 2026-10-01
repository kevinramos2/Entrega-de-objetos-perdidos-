const MESES_ABREV = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

/** Replica el formato de Django `d M Y` / `d M Y, H:i` usado en toda la app
 * clásica (p. ej. "04 Sep 2026, 15:29"), sin depender de que el navegador
 * tenga datos de Intl en español con meses abreviados. */
export function formatearFecha(valor: string | Date | null | undefined, { conHora = false } = {}) {
  if (!valor) return '—'
  const fecha = typeof valor === 'string' ? new Date(valor) : valor
  if (Number.isNaN(fecha.getTime())) return '—'
  const base = `${String(fecha.getDate()).padStart(2, '0')} ${MESES_ABREV[fecha.getMonth()]} ${fecha.getFullYear()}`
  if (!conHora) return base
  return `${base}, ${String(fecha.getHours()).padStart(2, '0')}:${String(fecha.getMinutes()).padStart(2, '0')}`
}

/** Para fechas sin hora (tipo `date` de Django, p. ej. fecha_registro) —
 * evita el desfase de un día que da `new Date('2026-08-28')` en UTC. */
export function formatearFechaSolo(valor: string | null | undefined) {
  if (!valor) return '—'
  return formatearFecha(`${valor}T00:00:00`)
}
