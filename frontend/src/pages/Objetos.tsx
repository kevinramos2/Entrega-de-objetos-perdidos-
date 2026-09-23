import { useState } from 'react'
import { ObjetoCard } from '../components/ObjetoCard'
import { Input, Select } from '../components/Input'
import { SEDES } from '../api/estudiante'
import { useCategorias, useObjetos } from '../hooks/useEstudianteApi'

export default function Objetos() {
  const [q, setQ] = useState('')
  const [categoria, setCategoria] = useState('')
  const [sede, setSede] = useState('')

  const { data: categorias } = useCategorias()
  const { data: objetos, isLoading } = useObjetos({ q, categoria, sede })

  return (
    <div className="flex flex-col gap-8">
      <header>
        <h1 className="font-display text-heading text-ink">Objetos disponibles</h1>
        <p className="mt-1 text-body text-ink-muted">
          Busca por nombre, categoría o lugar donde se encontró.
        </p>
      </header>

      <div className="grid gap-4 sm:grid-cols-3">
        <Input
          id="buscar"
          label="Buscar"
          placeholder="Ej. termo, carné, cargador…"
          value={q}
          onChange={(evento) => setQ(evento.target.value)}
        />
        <Select
          id="categoria"
          label="Categoría"
          value={categoria}
          onChange={(evento) => setCategoria(evento.target.value)}
        >
          <option value="">Todas</option>
          {categorias?.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.nombre}
            </option>
          ))}
        </Select>
        <Select id="sede" label="Sede" value={sede} onChange={(evento) => setSede(evento.target.value)}>
          <option value="">Todas</option>
          {SEDES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </Select>
      </div>

      {isLoading && <p className="text-body text-ink-muted">Cargando objetos…</p>}

      {objetos && objetos.length === 0 && (
        <p className="rounded-card border border-hairline bg-mist p-8 text-center text-body text-ink-muted">
          No encontramos objetos con esos filtros. Prueba con otra búsqueda.
        </p>
      )}

      {objetos && objetos.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {objetos.map((objeto) => (
            <ObjetoCard key={objeto.id} objeto={objeto} />
          ))}
        </div>
      )}
    </div>
  )
}
