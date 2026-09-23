import { Link } from 'react-router-dom'
import { useAuth } from '../lib/auth-context'
import { LogoMark } from './Logo'

function IconoCorreo() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <path d="m22 7-10 6L2 7" />
    </svg>
  )
}

export function Footer() {
  const { usuario } = useAuth()

  return (
    <footer className="footer mt-16">
      <div className="mx-auto grid max-w-5xl gap-8 px-4 py-14 sm:grid-cols-2 lg:grid-cols-[1.6fr_1fr_1fr_1.3fr]">
        <div>
          <Link to="/" className="inline-flex items-center gap-2.5 text-body-lg font-bold text-white">
            <LogoMark size={32} />
            Perdidos &amp; Encontrados
          </Link>
          <p className="mt-4 max-w-xs text-body text-[#9dc4b2]">
            Una herramienta creada por y para la comunidad universitaria para reducir los objetos que
            quedan sin dueño. Encuentra lo que perdiste o ayuda a devolver lo que encontraste.
          </p>
          <span className="footer-sello mt-2 inline-flex">
            Proyecto académico · Universidad Nacional de Colombia
          </span>
        </div>

        <div>
          <h4 className="mb-4 text-caption font-bold uppercase tracking-widest text-white">Explora</h4>
          <nav className="flex flex-col">
            <Link to="/" className="py-1 text-body">Inicio</Link>
            <Link to="/objetos" className="py-1 text-body">Objetos perdidos</Link>
            {usuario && <Link to="/mis-solicitudes" className="py-1 text-body">Mis reclamos</Link>}
            {usuario?.is_staff && <Link to="/panel" className="py-1 text-body">Panel de administración</Link>}
          </nav>
        </div>

        <div>
          <h4 className="mb-4 text-caption font-bold uppercase tracking-widest text-white">Institución</h4>
          <a href="https://unal.edu.co" target="_blank" rel="noopener noreferrer" className="py-1 text-body block">
            Universidad Nacional
          </a>
          <span className="block py-1 text-caption text-[#7aa894]">Coordinación de Bienestar Universitario</span>
          <span className="block py-1 text-caption text-[#7aa894]">Sede Medellín · Calle 59A No. 63-20</span>
        </div>

        <div>
          <h4 className="mb-4 text-caption font-bold uppercase tracking-widest text-white">Contacto</h4>
          <a href="mailto:objetos.perdidos@unal.edu.co" className="footer-mail mb-4">
            <IconoCorreo />
            objetos.perdidos@unal.edu.co
          </a>
          <p className="text-body text-[#9dc4b2]">
            ¿Perdiste un objeto o tienes problemas para ingresar? Escríbenos y te ayudamos a resolverlo.
          </p>
        </div>
      </div>
      <div className="border-t border-[#1c3a30]">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-2 px-4 py-4 text-caption text-[#7aa894]">
          <span>Plataforma académica de la comunidad universitaria</span>
          <span>© {new Date().getFullYear()} Perdidos &amp; Encontrados</span>
        </div>
      </div>
    </footer>
  )
}
