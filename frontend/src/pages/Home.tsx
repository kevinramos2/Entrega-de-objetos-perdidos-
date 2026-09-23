import { Link } from 'react-router-dom'
import type { ObjetoPublico } from '../api/estudiante'
import { Button } from '../components/Button'
import { CategoryIcon, fondoTenue } from '../components/CategoryIcon'
import { StatCard } from '../components/StatCard'
import { useResumen } from '../hooks/useEstudianteApi'
import { useAuth } from '../lib/auth-context'

function FilaObjetoReciente({ objeto }: { objeto: ObjetoPublico }) {
  const color = objeto.categoria_color || '#0b7a54'
  return (
    <Link
      to={`/objetos/${objeto.id}`}
      className="flex items-center gap-3 rounded-input border border-line p-3 transition-colors hover:bg-surface-hover"
    >
      <span
        className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-input"
        style={{ backgroundColor: fondoTenue(color), color }}
      >
        <CategoryIcon clave={objeto.categoria_icono} size={22} />
      </span>
      <div className="min-w-0">
        <p className="truncate font-semibold text-body text-ink">{objeto.nombre_objeto || 'Objeto sin nombre'}</p>
        <p className="truncate text-caption text-muted">
          {objeto.categoria_nombre} · {objeto.lugar_encontrado || objeto.sede_display}
        </p>
      </div>
    </Link>
  )
}

export default function Home() {
  const { usuario } = useAuth()
  const { data } = useResumen()
  const resumen = data?.resumen

  return (
    <div className="flex flex-col gap-16 pb-16">
      <section className="-mx-4 rounded-b-card-lg bg-hero-gradient px-4 py-12 text-white sm:mx-0 sm:rounded-card-lg sm:px-10">
        <div className="grid items-center gap-10 lg:grid-cols-2">
          <div>
            <h1 className="font-display text-heading-lg font-bold leading-tight">
              ¿Perdiste algo? Aquí puede estar esperándote.
            </h1>
            <p className="mt-4 max-w-md text-body-lg text-white/85">
              Centralizamos los objetos perdidos y encontrados de la universidad. Busca lo que perdiste,
              solicita su reclamo y recupera lo que es tuyo.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              {usuario ? (
                <Link to="/objetos">
                  <Button variante="invertido">Ver objetos perdidos</Button>
                </Link>
              ) : (
                <Link to="/login">
                  <Button variante="invertido">Ingresar con tu correo institucional</Button>
                </Link>
              )}
              <Link to="/mis-solicitudes">
                <Button variante="ghost-oscuro">Mis solicitudes</Button>
              </Link>
            </div>
          </div>

          {data && data.recientes.length > 0 && (
            <div className="rounded-card-lg bg-surface p-5 text-ink shadow-floating">
              <div className="flex items-center justify-between">
                <h2 className="font-display text-body-lg font-bold text-ink">Encontrados recientemente</h2>
                {resumen && (
                  <span className="rounded-pill bg-primary-wash px-3 py-1 text-caption font-semibold text-primary-dark">
                    {resumen.disponibles} disponibles
                  </span>
                )}
              </div>
              <div className="mt-4 flex flex-col gap-2">
                {data.recientes.map((objeto) => (
                  <FilaObjetoReciente key={objeto.id} objeto={objeto} />
                ))}
              </div>
              <Link to={usuario ? '/objetos' : '/login'} className="mt-4 block">
                <Button variante="ghost" className="w-full">
                  Explorar todos los objetos
                </Button>
              </Link>
            </div>
          )}
        </div>
      </section>

      {resumen && (
        <section className="grid gap-4 sm:grid-cols-3">
          <StatCard etiqueta="Objetos disponibles" valor={resumen.disponibles} detalle="esperando a su dueño" />
          <StatCard etiqueta="Tasa de recuperación" valor={`${resumen.tasa_recuperacion}%`} detalle="del total reportado" />
          <StatCard etiqueta="Total reportados" valor={resumen.total} detalle="desde el inicio de la plataforma" />
        </section>
      )}

      {data?.mensajes && data.mensajes.length > 0 && (
        <section className="grid gap-4 sm:grid-cols-2">
          {data.mensajes.slice(0, 4).map((mensaje) => (
            <div key={mensaje.titulo} className="rounded-card border border-line bg-surface p-5 shadow-card">
              <p className="font-display text-heading-sm font-bold text-ink">{mensaje.titulo}</p>
              <p className="mt-1 text-body text-muted">{mensaje.detalle}</p>
            </div>
          ))}
        </section>
      )}
    </div>
  )
}
