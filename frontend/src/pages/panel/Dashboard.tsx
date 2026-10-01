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
import { Link } from 'react-router-dom'
import { BadgeEstadoSolicitud } from '../../components/Badge'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { StatCard } from '../../components/StatCard'
import { useDashboard } from '../../hooks/usePanelApi'
import { useAuth } from '../../lib/auth-context'

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, LineElement, PointElement, Legend, Tooltip)

const COLOR_MUTED = '#667085'
const COLOR_LINE = '#e4e7ec'

const NOMBRES_ESTADO: Record<string, string> = {
  disponible: 'Disponible',
  reclamado: 'Reclamado',
  entregado: 'Entregado',
}

const ICONO_CAJA = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
    <path d="M3.27 6.96 12 12.01l8.73-5.05" />
    <path d="M12 22.08V12" />
  </svg>
)
const ICONO_LUPA = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
)
const ICONO_RELOJ = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </svg>
)
const ICONO_CHECK = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12" />
  </svg>
)
const ICONO_DIANA = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <circle cx="12" cy="12" r="6" />
    <circle cx="12" cy="12" r="2" />
  </svg>
)

export default function Dashboard() {
  const { usuario } = useAuth()
  const { data, isLoading } = useDashboard()

  if (isLoading || !data) {
    return <p className="text-body text-muted">Cargando indicadores…</p>
  }

  const { resumen, por_categoria, por_estado, por_mes, actividad } = data

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-caption text-muted">Panel de administración</p>
          <h1 className="font-display text-heading font-bold text-ink">
            Hola, {usuario?.first_name || usuario?.username}
          </h1>
        </div>
        <div className="flex gap-2">
          <Link to="/panel/objetos/nuevo">
            <Button variante="primario">Registrar objeto</Button>
          </Link>
        </div>
      </header>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard etiqueta="Objetos registrados" valor={resumen.total} icono={ICONO_CAJA} />
        <StatCard etiqueta="Disponibles" valor={resumen.disponibles} tono="verde" icono={ICONO_LUPA} />
        <StatCard etiqueta="Reclamados" valor={resumen.reclamados} tono="amarillo" icono={ICONO_RELOJ} />
        <StatCard etiqueta="Entregados" valor={resumen.entregados} tono="azul" icono={ICONO_CHECK} />
        <StatCard etiqueta="Tasa de recuperación" valor={`${resumen.tasa_recuperacion}%`} icono={ICONO_DIANA} />
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
