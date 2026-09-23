import { Link } from 'react-router-dom'
import { ObjetoCard } from '../components/ObjetoCard'
import { Button } from '../components/Button'
import { StatCard } from '../components/StatCard'
import { useObjetos, useResumen } from '../hooks/useEstudianteApi'
import { useAuth } from '../lib/auth-context'

export default function Home() {
  const { usuario } = useAuth()
  const { data, isLoading } = useResumen()
  const { data: objetos } = useObjetos({}, { enabled: Boolean(usuario) })

  const resumen = data?.resumen

  return (
    <div className="flex flex-col gap-16 pb-16">
      <section className="-mx-4 rounded-b-card-lg bg-forest px-4 py-20 text-center sm:mx-0 sm:rounded-card-lg">
        <p className="font-mono text-caption uppercase tracking-widest text-terracota">
          Universidad Nacional de Colombia
        </p>
        <h1 className="mx-auto mt-4 max-w-2xl font-display text-display leading-none text-cream">
          Perdiste algo, <span className="text-terracota">lo encontramos</span>
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-body-lg text-cream-muted">
          Centralizamos los objetos perdidos y encontrados en las sedes Minas y El Volador.
          Busca el tuyo o revisa el estado de tus solicitudes.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          {usuario ? (
            <Link to="/objetos">
              <Button variante="primario">Ver objetos perdidos</Button>
            </Link>
          ) : (
            <Link to="/login">
              <Button variante="primario">Ingresar con tu correo institucional</Button>
            </Link>
          )}
          <Link to="/mis-solicitudes">
            <Button variante="ghost-oscuro">Mis solicitudes</Button>
          </Link>
        </div>
      </section>

      {resumen && (
        <section className="grid gap-4 sm:grid-cols-3">
          <StatCard etiqueta="Objetos disponibles" valor={resumen.disponibles} detalle="esperando a su dueño" />
          <StatCard
            etiqueta="Tasa de recuperación"
            valor={`${resumen.tasa_recuperacion}%`}
            detalle="del total reportado"
            tono="oscuro"
          />
          <StatCard etiqueta="Total reportados" valor={resumen.total} detalle="desde el inicio de la plataforma" />
        </section>
      )}

      {data?.mensajes && data.mensajes.length > 0 && (
        <section className="grid gap-4 sm:grid-cols-2">
          {data.mensajes.slice(0, 4).map((mensaje) => (
            <div key={mensaje.titulo} className="rounded-card border border-hairline bg-mist p-5">
              <p className="font-display text-heading-sm text-ink">{mensaje.titulo}</p>
              <p className="mt-1 text-body text-ink-muted">{mensaje.detalle}</p>
            </div>
          ))}
        </section>
      )}

      {usuario ? (
        objetos && objetos.length > 0 && (
          <section>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-display text-heading-sm text-ink">Objetos recién reportados</h2>
              <Link to="/objetos" className="text-caption font-medium text-terracota hover:underline">
                Ver todos →
              </Link>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              {objetos.slice(0, 3).map((objeto) => (
                <ObjetoCard key={objeto.id} objeto={objeto} />
              ))}
            </div>
          </section>
        )
      ) : (
        !isLoading && (
          <section className="rounded-card border border-hairline bg-mist p-8 text-center">
            <p className="text-body-lg text-ink-muted">
              Inicia sesión con tu correo institucional para explorar el listado de objetos.
            </p>
          </section>
        )
      )}
    </div>
  )
}
