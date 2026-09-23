import { useEffect, useRef } from 'react'

/** Luminosidad que sigue al cursor dentro del hero, con una estela de
 * partículas — portado 1:1 desde static/js/app.js (mismo suavizado,
 * mismo throttle de partículas) para conservar el efecto de la app
 * clásica. Se desactiva sola en touch y con movimiento reducido. */
export function HeroTracker() {
  const trackerRef = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    const trackerNulable = trackerRef.current
    if (!trackerNulable) return
    if (!window.matchMedia('(pointer: fine)').matches) return
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

    const heroNulable = trackerNulable.closest('.hero-fondo') as HTMLElement | null
    if (!heroNulable) return

    const tracker: HTMLSpanElement = trackerNulable
    const hero: HTMLElement = heroNulable

    const centro = 22
    const destino = { x: 0, y: 0 }
    const actual = { x: 0, y: 0 }
    let iniciado = false
    let ultimaParticula = 0
    let raf = 0

    function animarTracker() {
      actual.x += (destino.x - actual.x) * 0.14
      actual.y += (destino.y - actual.y) * 0.14
      if (tracker) {
        tracker.style.transform = `translate3d(${actual.x - centro}px,${actual.y - centro}px,0)`
      }
      raf = requestAnimationFrame(animarTracker)
    }

    function espolvorear(x: number, y: number) {
      const ahora = Date.now()
      if (ahora - ultimaParticula < 45) return
      ultimaParticula = ahora
      const p = document.createElement('span')
      p.className = 'hero-particula'
      p.style.left = `${x - 3}px`
      p.style.top = `${y - 3}px`
      const tam = (Math.random() * 4 + 3).toFixed(1)
      p.style.width = `${tam}px`
      p.style.height = `${tam}px`
      p.style.setProperty('--dx', `${(Math.random() * 60 - 30).toFixed(0)}px`)
      p.style.setProperty('--dy', `${(Math.random() * -46).toFixed(0)}px`)
      hero.appendChild(p)
      setTimeout(() => p.remove(), 950)
    }

    function alMover(e: MouseEvent) {
      const r = hero.getBoundingClientRect()
      const x = e.clientX - r.left
      const y = e.clientY - r.top
      destino.x = x
      destino.y = y
      espolvorear(x, y)
      if (!iniciado) {
        iniciado = true
        actual.x = x
        actual.y = y
        raf = requestAnimationFrame(animarTracker)
      }
      tracker.classList.add('visible')
    }

    function alSalir() {
      tracker.classList.remove('visible')
    }

    hero.addEventListener('mousemove', alMover)
    hero.addEventListener('mouseleave', alSalir)

    return () => {
      hero.removeEventListener('mousemove', alMover)
      hero.removeEventListener('mouseleave', alSalir)
      cancelAnimationFrame(raf)
      hero.querySelectorAll('.hero-particula').forEach((p) => p.remove())
    }
  }, [])

  return <span ref={trackerRef} className="hero-tracker" aria-hidden="true" />
}
