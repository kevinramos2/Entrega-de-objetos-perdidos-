import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from 'chart.js'
import { Bar, Doughnut, Line } from 'react-chartjs-2'
import { BadgeEstadoSolicitud } from '../../components/Badge'
import { Card } from '../../components/Card'
import { StatCard } from '../../components/StatCard'
import { useDashboard } from '../../hooks/usePanelApi'

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, LineElement, PointElement, Legend, Tooltip)

const COLOR_MUTED = '#667085'
const COLOR_LINE = '#e4e7ec'

const NOMBRES_ESTADO: Record<string, string> = {
  disponible: 'Disponible',
  reclamado: 'Reclamado',
  entregado: 'Entregado',
}

export default function Dashboard() {
  const { data, isLoading } = useDashboard()

  if (isLoading || !data) {
    return <p className="text-body text-muted">Cargando indicadores…</p>
  }

  const { resumen, por_categoria, por_estado, por_mes, actividad } = data

  return (
    <div className="flex flex-col gap-8">
      <header>
        <h1 className="font-display text-heading font-bold text-ink">Resumen</h1>
        <p className="mt-1 text-body text-muted">Estado general de objetos y solicitudes.</p>
      </header>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard etiqueta="Disponibles" valor={resumen.disponibles} />
        <StatCard etiqueta="Reclamados" valor={resumen.reclamados} />
        <StatCard etiqueta="Entregados" valor={resumen.entregados} />
        <StatCard etiqueta="Por revisar" valor={resumen.solicitudes_pendientes} />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="font-display text-heading-sm font-bold text-ink">Objetos por categoría</h2>
          <div className="mt-4 h-64">
            <Bar
              data={{
                labels: por_categoria.map((c) => c.categoria__nombre || 'Sin categoría'),
                datasets: [
                  {
                    label: 'Objetos',
                    data: por_categoria.map((c) => c.total),
                    backgroundColor: por_categoria.map((c) => c.categoria__color || '#0b7a54'),
                    borderRadius: 6,
                  },
                ],
              }}
              options={{
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                  x: { ticks: { color: COLOR_MUTED }, grid: { display: false } },
                  y: { ticks: { color: COLOR_MUTED }, grid: { color: COLOR_LINE } },
                },
              }}
            />
          </div>
        </Card>

        <Card>
          <h2 className="font-display text-heading-sm font-bold text-ink">Objetos por estado</h2>
          <div className="mt-4 flex h-64 items-center justify-center">
            <Doughnut
              data={{
                labels: por_estado.map((e) => NOMBRES_ESTADO[e.estado] ?? e.estado),
                datasets: [
                  {
                    data: por_estado.map((e) => e.total),
                    backgroundColor: ['#0b7a54', '#b45309', '#2563eb'],
                    borderWidth: 0,
                  },
                ],
              }}
              options={{ maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }}
            />
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <h2 className="font-display text-heading-sm font-bold text-ink">Objetos registrados por mes</h2>
          <div className="mt-4 h-64">
            <Line
              data={{
                labels: por_mes.map((m) => m.mes),
                datasets: [
                  {
                    label: 'Objetos',
                    data: por_mes.map((m) => m.total),
                    borderColor: '#0b7a54',
                    backgroundColor: '#e8f6ee',
                    tension: 0.3,
                    fill: true,
                  },
                ],
              }}
              options={{
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                  x: { ticks: { color: COLOR_MUTED }, grid: { display: false } },
                  y: { ticks: { color: COLOR_MUTED }, grid: { color: COLOR_LINE } },
                },
              }}
            />
          </div>
        </Card>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="font-display text-heading-sm font-bold text-ink">Objetos recientes</h2>
          <ul className="mt-4 flex flex-col gap-3">
            {actividad.objetos.map((objeto) => (
              <li key={objeto.id} className="flex items-center justify-between border-b border-line pb-2 text-body">
                <span className="text-ink">{objeto.nombre_objeto || 'Objeto sin nombre'}</span>
                <span className="text-caption text-muted">{objeto.estado_display}</span>
              </li>
            ))}
          </ul>
        </Card>
        <Card>
          <h2 className="font-display text-heading-sm font-bold text-ink">Solicitudes recientes</h2>
          <ul className="mt-4 flex flex-col gap-3">
            {actividad.solicitudes.map((solicitud) => (
              <li key={solicitud.id} className="flex items-center justify-between border-b border-line pb-2 text-body">
                <span className="text-ink">{solicitud.objeto_detalle.nombre_objeto || 'Objeto sin nombre'}</span>
                <BadgeEstadoSolicitud estado={solicitud.estado} etiqueta={solicitud.estado_display} />
              </li>
            ))}
          </ul>
        </Card>
      </section>
    </div>
  )
}
