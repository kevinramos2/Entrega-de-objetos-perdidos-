import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import type { Mensaje, ObjetoPublico } from '../api/estudiante'
import { Button } from '../components/Button'
import { CategoryIcon } from '../components/CategoryIcon'
import { HeroTracker } from '../components/HeroTracker'
import { useCategorias, useResumen } from '../hooks/useEstudianteApi'
import { useAuth } from '../lib/auth-context'

function FilaObjetoReciente({ objeto }: { objeto: ObjetoPublico }) {
  return (
    <Link to={`/objetos/${objeto.id}`} className="demo-item">
      <span
        className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-input text-white"
        style={{ backgroundColor: 'rgba(255,255,255,.16)' }}
      >
        <CategoryIcon clave={objeto.categoria_icono} size={20} />
      </span>
      <div className="min-w-0">
        <p className="truncate font-semibold text-body text-white">{objeto.nombre_objeto || 'Objeto sin nombre'}</p>
        <p className="truncate text-caption text-white/70">
          {objeto.categoria_nombre} · {objeto.lugar_encontrado || 'Sin lugar'}
        </p>
      </div>
    </Link>
  )
}

const ICONOS_INSIGHT: Record<string, ReactNode> = {
  reportes: (
    <>
      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
      <path d="M3.27 6.96 12 12.01l8.73-5.05" />
      <path d="M12 22.08V12" />
    </>
  ),
  recuperados: (
    <>
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </>
  ),
  disponibles: (
    <>
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </>
  ),
  solicitudes: (
    <>
      <polyline points="22 12 16 12 14 15 10 15 8 12 2 12" />
      <path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z" />
    </>
  ),
  categoria: (
    <>
      <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
      <line x1="7" y1="7" x2="7.01" y2="7" />
    </>
  ),
  plazo: (
    <>
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </>
  ),
}

function IconoInsight({ tipo }: { tipo: string }) {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      {ICONOS_INSIGHT[tipo] ?? ICONOS_INSIGHT.plazo}
    </svg>
  )
}

function Insight({ mensaje }: { mensaje: Mensaje }) {
  return (
    <div className="insight animar-entrada flex flex-col items-center gap-2.5 rounded-card border border-line bg-surface p-5 text-center shadow-card">
      <span className="flex h-11 w-11 items-center justify-center rounded-input bg-primary-wash text-primary">
        <IconoInsight tipo={mensaje.tipo} />
      </span>
      <div>
        <p className="font-semibold text-body text-ink">{mensaje.titulo}</p>
        <p className="mt-0.5 text-caption leading-relaxed text-muted">{mensaje.detalle}</p>
      </div>
    </div>
  )
}

const PASOS = [
  {
    titulo: 'Explora',
    texto: 'Revisa los objetos encontrados y filtra por categoría o lugar.',
    icono: (
      <>
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </>
    ),
  },
  {
    titulo: 'Solicita',
    texto: '¿Reconoces el objeto? Envía tu solicitud de reclamo.',
    icono: (
      <>
        <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
        <rect x="8" y="2" width="8" height="4" rx="1" />
      </>
    ),
  },
  {
    titulo: 'Recupera',
    texto: 'La coordinación verifica la entrega y coordina la devolución.',
    icono: (
      <>
        <path d="m21 2-9.6 9.6" />
        <path d="m15.5 7.5 3 3L22 7l-3-3" />
        <path d="m9 11 3 3" />
        <path d="M9.2 10.8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z" />
      </>
    ),
  },
]

function SeccionHeader({ eyebrow, titulo, texto }: { eyebrow: string; titulo: string; texto: string }) {
  return (
    <div className="mx-auto mb-9 max-w-xl text-center">
      <span className="inline-flex rounded-pill bg-primary-wash px-3.5 py-1.5 text-caption font-bold uppercase tracking-widest text-primary-dark">
        {eyebrow}
      </span>
      <h2 className="mt-3.5 font-display text-heading font-bold text-ink">{titulo}</h2>
      <p className="mt-2 text-body text-muted">{texto}</p>
    </div>
  )
}

export default function Home() {
  const { usuario } = useAuth()
  const { data } = useResumen()
  const { data: categorias } = useCategorias()
  const resumen = data?.resumen

  return (
    <div className="flex flex-col">
      <section className="hero-fondo relative left-1/2 right-1/2 -mx-[50vw] -mt-10 w-screen px-4 py-20 text-white sm:px-10">
        <span className="hero-orb hero-orb-a" aria-hidden="true" />
        <span className="hero-orb hero-orb-b" aria-hidden="true" />
        <HeroTracker />
        <div className="relative mx-auto grid max-w-5xl items-center gap-10 lg:grid-cols-2">
          <div>
            <h1 className="font-display text-heading-lg font-bold leading-tight">
              ¿Perdiste algo?
              <br />
              Aquí puede estar esperándote.
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
            </div>
            {resumen && (
              <div className="mt-10 grid grid-cols-3 gap-3.5">
                <div className="hero-stat">
                  <b className="font-display text-heading-sm font-bold">{resumen.total}</b>
                  <span className="block text-caption text-white/80">objetos reportados</span>
                </div>
                <div className="hero-stat">
                  <b className="font-display text-heading-sm font-bold">{resumen.disponibles}</b>
                  <span className="block text-caption text-white/80">esperando dueño</span>
                </div>
                <div className="hero-stat">
                  <b className="font-display text-heading-sm font-bold">{resumen.tasa_recuperacion}%</b>
                  <span className="block text-caption text-white/80">recuperados</span>
                </div>
              </div>
            )}
          </div>

          {data && (
            <div className="hero-demo relative">
              <div className="mb-4 flex items-center justify-between">
                <span className="font-semibold text-body text-white">Encontrados recientemente</span>
                {resumen && <span className="demo-pill">{resumen.disponibles} disponibles</span>}
              </div>
              <div className="flex flex-col gap-2.5">
                {data.recientes.length > 0 ? (
                  data.recientes.map((objeto) => <FilaObjetoReciente key={objeto.id} objeto={objeto} />)
                ) : (
                  <p className="text-body text-white/80">Aún no hay reportes. Los objetos registrados aparecerán aquí.</p>
                )}
              </div>
              <Link to={usuario ? '/objetos' : '/login'} className="btn btn-invertido mt-4 w-full py-2.5 text-body">
                Explorar todos los objetos
              </Link>
            </div>
          )}
        </div>
      </section>

      {categorias && categorias.length > 0 && (
        <section className="py-16">
          <SeccionHeader
            eyebrow="Explora por categoría"
            titulo="¿Qué se pierde en la universidad?"
            texto="Revisa las categorías más comunes y encuentra lo que buscas."
          />
          <div className="grid grid-cols-[repeat(auto-fill,minmax(225px,1fr))] gap-3.5">
            {categorias.map((categoria) => (
              <Link
                key={categoria.id}
                to={usuario ? `/objetos?categoria=${categoria.id}` : '/login'}
                className="cat-card animar-entrada rounded-card border border-line bg-surface p-3.5 shadow-card"
              >
                <span
                  className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-input text-white"
                  style={{ backgroundColor: categoria.color }}
                >
                  <CategoryIcon clave={categoria.icono} size={22} />
                </span>
                <span className="flex min-w-0 flex-col">
                  <b className="truncate text-body text-ink">{categoria.nombre}</b>
                  <span className="truncate text-caption text-muted">
                    {categoria.total_disponibles ? `${categoria.total_disponibles} esperando dueño` : 'Sin reportes disponibles'}
                  </span>
                </span>
                <svg className="cat-card-flecha ml-auto h-[18px] w-[18px] flex-shrink-0 text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </Link>
            ))}
          </div>
        </section>
      )}

      <section className="seccion-alt relative left-1/2 right-1/2 -mx-[50vw] w-screen px-4 py-16 sm:px-10">
        <div className="mx-auto max-w-5xl">
          <SeccionHeader
            eyebrow="¿Cómo funciona?"
            titulo="Tres pasos simples que conectan lo perdido con su dueño"
            texto="Del armario de objetos perdidos de regreso a tus manos."
          />
          <div className="grid gap-5 sm:grid-cols-3">
            {PASOS.map((paso) => (
              <div key={paso.titulo} className="paso animar-entrada rounded-card border border-line bg-surface p-7 text-center shadow-card">
                <span className="mx-auto mb-3.5 flex h-[52px] w-[52px] items-center justify-center rounded-full bg-primary-wash text-primary">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.9} strokeLinecap="round" strokeLinejoin="round">
                    {paso.icono}
                  </svg>
                </span>
                <h3 className="font-display text-body-lg font-bold text-ink">{paso.titulo}</h3>
                <p className="mt-1.5 text-body text-muted">{paso.texto}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {data?.mensajes && data.mensajes.length > 0 && (
        <section className="py-16">
          <SeccionHeader
            eyebrow="La situación, en números"
            titulo="Datos reales de la plataforma"
            texto="Actualizados en cada consulta."
          />
          <div className="grid gap-3.5 sm:grid-cols-2 lg:grid-cols-3">
            {data.mensajes.map((mensaje) => (
              <Insight key={mensaje.titulo} mensaje={mensaje} />
            ))}
          </div>
          <div className="mt-9 text-center">
            <Link to={usuario ? '/objetos' : '/login'}>
              <Button variante="primario">
                {usuario ? 'Ver objetos perdidos' : 'Quiero recuperar lo que es mío'}
              </Button>
            </Link>
          </div>
        </section>
      )}
    </div>
  )
}
