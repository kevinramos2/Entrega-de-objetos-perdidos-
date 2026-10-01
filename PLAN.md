# Plan maestro de construcción — Entrega de Objetos Perdidos

> Documento de referencia: **qué se construyó, cómo y por qué**, paso a paso, pensado para
> que cualquier persona (o cualquier IA) pueda reconstruir el proyecto completo desde cero.
> La app clásica de Django es la fuente de verdad del producto y del diseño; la sección final
> explica cómo portarla a React **sin perder la estética**.

---

## 0. Principios que rigieron todo el proyecto

| Principio | Cómo se aplicó |
|---|---|
| **Un solo origen de verdad para el dato** | Todo vive en modelos Django; las vistas solo orquestan; las plantillas solo pintan |
| **Identidad visual antes que features** | `estilos.css` empieza por tokens (`:root`) y todo lo demás consume variables |
| **Cero librerías de UI** | HTML + CSS + JS propios; solo Chart.js (gráficos) y ReportLab (PDF) |
| **Nada de emojis** | Set de iconos SVG inline + `iconos.py` (templatetag) para categorías |
| **Cada cambio visual se verifica** | Probe headless (Chrome DevTools Protocol) en varios anchos antes de commitear |
| **Cada cambio de modelo se migra y se prueba** | 15 migraciones, 35 tests que pasan antes de commitear |

**Stack exacto:** Python 3.11 · Django 5.2.5 · django-allauth 65.19.1 · ReportLab 5.0.1 ·
Pillow 12.3 · whitenoise · gunicorn · psycopg · dj-database-url · python-dotenv ·
django-anymail (Resend) · SQLite local / PostgreSQL en Render.

---

## Fase 0 — Andamiaje del proyecto

```txt
Entrega-de-objetos-perdidos-/          # raíz del repo (de aquí lee requirements.txt)
├── objetos_reclamados/                # rootDir de Django (aquí vive manage.py)
│   ├── manage.py
│   ├── objetos_reclamados/            # paquete de configuración
│   │   ├── settings.py                # todo por variables de entorno + .env
│   │   ├── urls.py                    # admin/ + accounts/ + api/v1/ + app
│   │   ├── wsgi.py
│   │   └── templates/                 # 403.html, 404.html, socialaccount/login.html
│   ├── registro_objetos/              # app única (todo el dominio)
│   │   ├── models.py · forms.py · admin.py
│   │   ├── adapters.py                # allauth: dominio institucional
│   │   ├── signals.py                 # promoción automática de admin
│   │   ├── context_processors.py      # variables globales para plantillas
│   │   ├── estadisticas.py            # agregados tarjetas + gráficas
│   │   ├── formato_entrega.py         # PDF con ReportLab
│   │   ├── firma_util.py              # normalización de la firma digital
│   │   ├── imagenes.py                # procesamiento de imágenes
│   │   ├── correo.py                  # notificaciones por email
│   │   ├── iconos.py                  # templatetag de iconos de categoría
│   │   ├── views/                     # paquete de vistas por responsabilidad
│   │   ├── api/                       # DRF: serializers, views, urls
│   │   ├── management/commands/       # seed, promo, recompresión, correo
│   │   ├── migrations/                # 0001…0015
│   │   ├── templatetags/
│   │   ├── templates/                 # objetos/ panel/ correo/ registro/ admin/
│   │   ├── tests.py · test_api.py
│   │   └── urls.py
│   ├── static/css/estilos.css         # sistema de diseño completo
│   ├── static/js/app.js               # tema, uploads, datepicker, toasts
│   └── db.sqlite3
├── frontend/                          # SPA en React (migración en curso)
├── requirements.txt · render.yaml · .env.example · README.md
├── desing/                            # notas de diseño de referencia
└── img/capturas/                      # capturas para el README
```

**Pasos:**

1. `python -m venv venv` + `pip install -r requirements.txt`.
2. `django-admin startproject objetos_reclamados .` dentro de la carpeta del proyecto.
3. `python manage.py startapp registro_objetos`.
4. `settings.py` con reglas duras:
   - `SECRET_KEY` obligatoria si `DEBUG=False` (si no, `RuntimeError` al arrancar).
   - `ALLOWED_HOSTS` obligatorio en producción.
   - Logging a consola (`django.request` en `ERROR`) porque Render no muestra logs si no.
   - `DATA_UPLOAD_MAX_MEMORY_SIZE = 5MB` y `FILE_UPLOAD_MAX_MEMORY_SIZE = 5MB`
     (protección de memoria desde el día uno).
5. `dj_database_url` para que la **misma config** sirva con SQLite local y PostgreSQL en
   producción sin tocar código.
6. `.env` en la raíz del repo, cargado con `python-dotenv`; las variables reales del entorno
   tienen prioridad y `.env` nunca se sube a git.

---

## Fase 1 — Modelo de dominio

El corazón del sistema está en `registro_objetos/models.py`:

```python
Categoria            # nombre, icono, color (hex), orden
ObjetoReclamado      # el objeto perdido + datos del reclamante + trazabilidad
PerfilUsuario        # 1:1 con User; datos de contacto + firma digital
SolicitudReclamacion # reclamo del estudiante + decisiones + entrega
InstruccionesEntrega # singleton (pk=1) con el texto de recogida por sede
```

**Decisiones clave que hay que explicar bien:**

- **El ciclo de vida está en el modelo**, no en las vistas:
  `TextChoices` `Estados = disponible → reclamado → entregado` y `Sedes = minas / volador`.
- **La lógica de negocio vive en los métodos del modelo**, no en las vistas:
  - `SolicitudReclamacion.aprobar(admin, comentario, datos_entrega, sede)` → cambia el estado,
    guarda `respondida_por`, `comentario_admin`, marca `respuesta_vista=False`, **copia los
    datos del reclamante al objeto** (nombre, documento, teléfono, correo) y pone el objeto en
    *Reclamado* con `reclamado_por` y `fecha_reclamo`.
  - `rechazar(admin, comentario)` → deja la solicitud en *Rechazada* con su motivo.
  - `marcar_entregado(admin, fecha)` → solo desde *Aprobada* (si no, `ValueError`); registra
    `fecha_entrega`, `entregado_por`, pasa el objeto a *Entregado* y guarda
    `responsable_entrega`.
  - `apelar(usuario, motivo)` → **una sola vez** y solo por el dueño y solo si fue rechazada;
    el método lanza `ValueError` en los tres casos.
  - Si el admin no escribe datos de entrega, `aprobar()` cae en
    `obtener_texto_entrega_para_sede(sede)` → texto configurable por sede.
- **Por qué se copian los datos del reclamante al objeto**: el formato de entrega en PDF debe
  poder emitirse aunque el estudiante después edite o elimine su perfil. Es una decisión de
  "congelar el dato en el momento del reclamo".
- `foto_base64` (TextField) **además de** `foto` (ImageField): el disco de Render es efímero y
  las fotos sin comprimir agotaban la memoria del servicio.
- La `property foto_data` devuelve la URL del endpoint `servir_foto_objeto` si hay base64, o
  `.url` si hay archivo. Las plantillas nunca tocan el archivo directamente.
- `Categoria.categoria = ForeignKey(..., on_delete=PROTECT)`: no se puede borrar una categoría
  que tiene objetos.
- Todos los campos llevan `verbose_name` y `help_text` en español (se ven en el panel clásico
  de Django y documentan el dominio solos).

### Migraciones (15, en orden de nacimiento del proyecto)

```txt
0001_initial
0002_categoria_alter_objetoreclamado_options_and_more
0003_seed_categorias_y_backfill        ← migración de DATOS: crea las 12 categorías
0004_remove_objetoreclamado_tipo_objeto
0005_alter_categoria_color_alter_categoria_icono
0006_instruccionesentrega_solicitudreclamacion_apelacion_and_more
0007_solicitudreclamacion_respuesta_vista
0008_solicitudreclamacion_datos_entrega
0009_objetoreclamado_sede
0010_categoria_iconos
0011_remove_instruccionesentrega_texto_and_more
0012_perfilusuario_firma
0013_alter_objetoreclamado_fecha_registro_and_more
0014_solicitudreclamacion_entregado_por_and_more
0015_objetoreclamado_foto_base64
```

`0003` es el patrón a reutilizar en cualquier siembra dentro de migraciones:
`RunPython` usando **`apps.get_model`** (nunca el modelo real) y su `reverse_code` para que la
migración sea reversible.

---

## Fase 2 — Autenticación, dominio institucional y roles

**Modelo de auth (mixto, deliberado):**

```python
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']   # solo correo, nunca "usuario"
ACCOUNT_EMAIL_VERIFICATION = 'none'   # el dominio institucional ya valida la identidad
ACCOUNT_UNIQUE_EMAIL = True
LOGIN_REDIRECT_URL = LOGOUT_REDIRECT_URL = 'panel_inicio' / 'inicio'
```

**Restricción de dominio — el corazón de la seguridad:**

```python
ALLOWED_EMAIL_DOMAINS = os.getenv('DJANGO_EMAIL_DOMAINS', 'unal.edu.co').split(',')
SOCIALACCOUNT_ADAPTER = 'registro_objetos.adapters.CorreoInstitucionalAdapter'
ACCOUNT_ADAPTER      = 'registro_objetos.adapters.CuentaDominioAdapter'
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
```

`adapters.py` hace dos cosas:

1. `clean_email()` / `pre_social_login()` lanzan `ValidationError` si el dominio no está
   permitido → nadie entra con Gmail ni con un correo personal.
2. `save_user()` enlaza automáticamente la cuenta de Google con la cuenta existente del mismo
   correo, para no duplicar al administrador.

**Rol admin automático:** `signals.py` con `post_save` sobre `User`: si el correo está en
`DJANGO_ADMIN_EMAILS`, promueve la cuenta a `is_staff=True` + superusuario. El comando
`promocionar_admins` aplica lo mismo a cuentas que ya existían.

**Google OAuth:** todo en `settings.py` dentro de `SOCIALACCOUNT_PROVIDERS['google']` con
`SCOPE=['profile','email']`, `OAUTH_PKCE_ENABLED=True` y `AUTH_PARAMS['prompt']='login'` (para no
entrar en silencio con la sesión de Google ya guardada). Si `GOOGLE_OAUTH_CLIENT_ID/SECRET`
vienen vacíos, `context_processors.globales` expone `GOOGLE_OAUTH_CONFIGURADO=False` y la
plantilla **oculta el botón** en lugar de fallar.

**Rate limiting del login** (en `views/helpers.py`, reutilizado por la API):
5 intentos fallidos en 15 minutos con dos claves — `_clave_login(identificador)` y
`_clave_ip(ip)` — y las funciones `intentos_bloqueados`, `registrar_intento_fallido`,
`limpiar_intentos`, `obtener_ip`.

**Cookies y sesión:** `SESSION_COOKIE_AGE = 2h`, `SESSION_EXPIRE_AT_BROWSER_CLOSE = True`,
`HttpOnly` en sesión y CSRF; en producción `Secure=True`, HSTS de 1 año, `X-Frame-Options:
DENY`, `nosniff`, `Referrer-Policy`.

---

## Fase 3 — Sistema de diseño (esto define la estética)

**Todo empieza por las líneas 1–41 de `estilos.css`.** Ese bloque es la fuente de verdad de la
identidad y se escribe **antes** que cualquier pantalla:

```css
:root {
  --font-title: 'Sora', 'Segoe UI', system-ui, sans-serif;
  --font-body:  'Inter', 'Segoe UI', system-ui, sans-serif;

  --primary: #0b7a54; --primary-600: #086144; --primary-700: #064d37; --primary-50: #e8f6ee;
  --accent: #b45309;  --accent-600: #92400e;  --accent-50: #fef3e7;

  --success: #128a56; --success-50: #e9f8f0;
  --warning: #c2700a; --warning-50: #fdf3e3;
  --danger:  #d92d20; --danger-50: #fcefec;
  --info:    #2563eb; --info-50:    #eef3ff;

  --ink: #101828; --ink-soft: #344054; --muted: #667085; --line: #e4e7ec;
  --bg: #f6f7f9; --surface: #ffffff;

  --radius: 16px; --radius-sm: 10px;
  --shadow-xs; --shadow-sm; --shadow; --shadow-lg;
  --grad: linear-gradient(135deg, #0b7a54 0%, #0d6b8c 100%);
}
```

**Layout base que se repite en todo el sitio:**

```css
.container        { width: min(1160px, 92%); margin-inline: auto; }  /* navbar + contenido */
.footer .container{ max-width: min(1080px, 94%); }                 /* footer más contenido */
```

`body` lleva **dos radial-gradient fijos** (teal arriba a la derecha, verde a la izquierda) más
`background-attachment: fixed`: es el detalle sutil que evita que el sitio se vea plano. Los
títulos usan `--font-title` con `letter-spacing: -.01em`.

**Jerarquía de plantillas:**

- `objetos/base.html` → esqueleto público: `<head>` con fuentes Sora + Inter (Google Fonts),
  navbar, `{% block content %}`, footer y `<script app.js>`.
- `panel/base.html` → extiende de `objetos/base.html` y añade el layout del panel
  (`body.panel-body`, `.panel-layout` = sidebar + main).
- `panel/partials/menulateral.html` → menú lateral con contadores.

**Iconografía:** SVG inline de 24×24 con `stroke="currentColor"` (heredan el color del texto).
Para categorías, `iconos.py` es un **templatetag**: `{% load iconos %}` y
`{{ obj.categoria|icono_cat }}` devuelve el SVG guardado en el campo `icono`.

**Imágenes:** `imagenes.py` centraliza el procesamiento (abrir, EXIF, redimensionar, comprimir,
convertir a base64). Las fotos se guardan en la base de datos y se sirven por
`objetos/<pk>/foto/`, comprimidas al vuelo → el HTML queda liviano y Render no muere por
memoria. El comando `recomprimir_fotos` re-aplica la compresión a las existentes al arrancar.

**Cache-busters (CRÍTICO):** en `objetos/base.html`

```html
<link rel="stylesheet" href="{% static 'css/estilos.css' %}?v=26">
<script src="{% static 'js/app.js' %}?v=11"></script>
```

**Regla:** cualquier cambio visual obliga a subir el número. Sin esto el móvil sirve la hoja
vieja y "no se ve el cambio" (pasó varias veces: v19, v21, v22, v23, v24, v25, v26).

---

## Fase 4 — Vistas del estudiante

En `views/publico.py` y `views/estudiante.py`, registradas en `registro_objetos/urls.py`:

| Ruta | Vista | Qué hace |
|---|---|---|
| `/` | `inicio` | Hero de dos columnas + preview de objetos recientes + secciones + recuadros de estadísticas |
| `/registro/`, `/login/`, `/logout/` | auth | Login simplificado: solo botón de Google |
| `/objetos/` | `lista_objetos` | Búsqueda por texto, filtro por categoría (chips), filtro por sede |
| `/objetos/<pk>/` | `detalle_objeto` | Foto, lugar, fecha, descripción, sede, botón solicitar |
| `/objetos/<pk>/solicitar/` | `solicitar_reclamacion` | Pide tipo/número de documento + teléfono (obligatorios para el PDF) |
| `/mis-solicitudes/` | `mis_solicitudes` | Estado, respuesta del admin, contador de "respuesta nueva", botón apelar |
| `/solicitudes/<pk>/apelar/` | `apelar_solicitud` | Una sola apelación, solo el dueño, solo si fue rechazada |

- `forms.py` concentra la validación: `RegistroObjetoForm`, `SolicitudReclamacionForm`,
  `UsuarioPanelForm`, `LoginForm`.
- Los datos de contacto del estudiante viven en `PerfilUsuario`, pero el formulario de reclamo
  **copia** esos datos a la solicitud para que el formato de entrega no dependa del perfil
  vigente.
- `estadisticas.py` calcula los agregados de las tarjetas ("+3 termos este mes", "% recuperados")
  con `Count`/`aggregate` y `TruncMonth`.
- La foto y el reclamante se gestionan en el mismo formulario de objeto: al registrar algo
  nuevo se oculta el bloque de reclamante; al editar algo ya *Reclamado* o *Entregado* aparece.

---

## Fase 5 — Panel de administración

Todas las vistas exigen admin (`@login_required` + `is_staff`) y devuelven 403 si no.

**Dashboard (`panel/inicio.html`):** 5 KPIs (total, disponibles, reclamados, entregados, tasa de
recuperación) + 2 gráficas (`chartCategoria` barras y `chartEstado` **dona**) + línea de
tendencia mensual + "Actividad reciente" (últimos 5). Chart.js 4.4.1 por CDN; los datos llegan
al JS como JSON con `|safe` (`{{ chart_categoria_labels|safe }}`).

**CRUD de objetos:** listado con búsqueda/filtros/selección múltiple, alta y edición con
cámara + galería en móvil, calendario de fecha de hallazgo, cambio rápido de estado, borrado
individual y en lote.

**Solicitudes:** listado con filtros por estado, detalle, aprobar/rechazar con comentario y
**datos de entrega editables**, y marcar entregado.

**Categorías:** alta, edición y borrado (con `PROTECT` en el modelo impide borrar una categoría
con objetos).

**Usuarios:** crear, editar, activar/desactivar, asignar rol y **subir la firma digital**.

**Configuración de entrega:** singleton de instrucciones por sede.

**Exportar CSV:** `views/exportar.py` genera el CSV con el módulo `csv` de la stdlib (incluye
la sede) para Power BI / Excel.

**Responsive del panel (lección dura, aprendida por partes):**

- `.panel-main { overflow-x: auto }` en móvil para que las tablas scrolleen **dentro** del panel
  sin ensanchar la navbar.
- `body.panel-body { overflow-x: hidden }` — aplica en **todos** los anchos.
- El badge de solicitudes se reduce a un puntito de 7px en móvil (antes ensanchaba la navbar).
- `.grid-charts > * { min-width: 0 }` también en escritorio: el `min-width: auto` por defecto
  de un grid item dejaba que el canvas empujara la columna.
- `.chart-caja { max-width: 100%; overflow: hidden }` y `.chart-caja canvas { max-width: 100% }`
  para que **ningún gráfico pueda crear scroll horizontal**, ni siquiera si Chart.js tarda en
  cargar o redimensionar.

---

## Fase 6 — Formato de entrega en PDF + firma digital

`formato_entrega.py` con ReportLab (Platypus): encabezado con logo y datos de la universidad,
tabla con datos del objeto y del reclamante, bloque **"Firma de quien entrega"** y pie de página
con `_pie(canvas, doc)` en `onFirstPage` / `onLaterPages`.

Puntos clave:

- Solo el **admin** descarga el formato, y **solo si la solicitud está aprobada y el objeto
  entregado** (`esta_entregada`). Hay 4 tests que garantizan esta regla.
- **La firma se resuelve así:** `generar_formato_entrega(solicitud)` usa
  `solicitud.entregado_por.perfil.firma`;
  `generar_formato_entrega_objeto(objeto, nombre_encargado, firma_path)` recibe la firma del
  admin que descarga cuando el objeto no tiene solicitud asociada.
- Dibujo: `Image(firma, width=…, height=…)` dentro de un máximo de **60mm × 14mm**, con
  `Spacer(4mm)` arriba y la línea debajo; sin firma deja 16mm para firmar a mano.
- `firma_util.py` nació del problema de memoria: `normalizar_firma` **siempre** guarda PNG RGBA
  con lado mayor ≤1000px, convierte blanco → transparente (`_blanco_a_transparente`), fija
  `Image.MAX_IMAGE_PIXELS = 40_000_000` contra "bombas de compresión" y lanza `ErrorFirma` con
  mensajes claros. `firma_path_de(usuario)` resuelve la ruta de forma segura.
- **Doble capa de compresión:** el cliente (`app.js` → canvas → `File('firma.png')` ≤1000px antes
  de subir) y el servidor (`clean_firma` del formulario). Así ninguna imagen enorme llega a la
  base ni al PDF.
- El campo de subida usa el mismo patrón `.archivo-subida` (arrastrar/soltar + botón "Elegir
  imagen" + preview) que las fotos, con `data-firma="1"` y `[data-btn-firma]` para que el JS solo
  lo procese en ese campo. El preview usa un chip claro (`.archivo-subida-firma`) para que el PNG
  transparente se vea en modo oscuro.

---

## Fase 7 — Correo de notificaciones

`correo.py` decide el backend en este orden (documentado en `settings.py`):

1. `RESEND_API_KEY` → **Resend por HTTPS**. Es lo recomendado en Render gratis porque **bloquea
   los puertos SMTP salientes (25/465/587)**.
2. `SMTP_HOST` + `SMTP_USER` → SMTP real (Gmail u otro).
3. Ninguno de los dos → **backend de consola**: en desarrollo ves el correo en la terminal.

`EMAIL_TIMEOUT = 10` para que un servidor que no responde no tumbe el worker de gunicorn.
Plantillas duales `correo/respuesta_solicitud.html` + `.txt`, con `{{ site_url }}` para los
enlaces. Se notifica al **aprobar** (con datos de recogida) y al **rechazar** (sin ellos).

---

## Fase 8 — Comandos de operación

| Comando | Para qué |
|---|---|
| `seed_demo` | Categorías + admin (`CambiaEsteAdmin123!`) + estudiante (`Estudiante123!`) + 9 objetos |
| `seed_objetos_prueba` | 30 objetos variando sedes, categorías, estados y fechas. Idempotente por nombre; `--limpiar` borra los creados |
| `promocionar_admins` | Aplica `DJANGO_ADMIN_EMAILS` a cuentas que ya existían |
| `recomprimir_fotos` | Re-comprime las fotos guardadas (evita que la memoria se dispare) |
| `probar_correo <correo>` | Envía un correo de prueba e informa qué backend se usó |
| `cargar_legado` / `exportar_legado` | Migración de datos de una base antigua |

Todos son **idempotentes** y se ejecutan en el `startCommand` de Render.

---

## Fase 9 — Modo oscuro y pulidos de maquetación

**Modo oscuro (patrón a replicar tal cual):**

1. `estilos.css`: bloque `[data-tema="oscuro"]` que **solo redefine variables** (colores,
   sombras) + reglas puntuales para elementos con fondo duro (`.tabla th`, `.badge-sede`,
   `.media`, `.seccion-alt`, `.panel-menu`…).
2. `<html data-tema="...">` + script **inline en `<head>`** que lee `localStorage['tema-aplicacion']`
   y, si no hay, `prefers-color-scheme` → cero parpadeo (FOUC).
3. Botón `#tema-toggle` en `.nav-actions` que intercambia luna/sol según el atributo.
4. `app.js`: al hacer clic guarda la preferencia; al cargar, la aplica.

**Pulidos que se hicieron, con su regla:**

- **Footer**: contenido a 1080px en escritorio (se veía "muy ancho" a 1160px, igual que la
  navbar); en móvil dos columnas (`Explora | Institución`) y `Contacto` a ancho completo
  separado por una línea. La altura total bajó de 843px a 751px.
- **Scroll horizontal del panel**: el origen era el `min-width: auto` de los grid items y un
  canvas que podía sobresalir. Arreglo definitivo: `min-width: 0` en los hijos **también en
  escritorio**, `max-width: 100%` en el canvas, `overflow: hidden` en `.chart-caja` y
  `overflow-x: hidden` en `body.panel-body`.
- **Tarjetas de objetos**: botón "Ver detalles" anclado al fondo (`align-self: end`) y texto
  largo recortado con `-webkit-line-clamp`.
- **Navbar en panel móvil**: el menú scrollea internamente, el badge se reduce a un puntito y
  el cuerpo no se desplaza lateralmente.

---

## Fase 10 — Pruebas automatizadas (35 tests)

`tests.py` con `TestCase` de Django, agrupadas por historia de usuario, y `test_api.py` para la
API. **Cada bug encontrado agregó un test.**

```python
class FormatoEntregaTest(TestCase):          # 10 tests
    def test_formato_estampa_la_firma_del_encargado(self):   # assert b'/Subtype /Image' en el PDF
    def test_firma_upload_se_normaliza_a_png(self):           # JPEG 3000x1200 -> PNG ≤1000 con alpha
    def test_firma_invalida_se_rechaza(self):                 # form.has_error('firma')

class NotificacionCorreoTest(TestCase):     # 3 tests con backend de memoria
class FlujoSolicitudApelacionTest(TestCase): # 4 tests: apelación única, dueño, contador
class InstruccionesEntregaTest(TestCase):   # 5 tests: prioridad de datos y textos por sede
class FiltroSedeTest(TestCase):             # 3 tests: filtro de lista y de panel
class RegistroObjetoTipoDocumentoYFechaTest(TestCase)
class InicioYNavegacionTest(TestCase)       # 4 tests: visibilidad por rol
```

**Regla:** `python manage.py test` en verde **antes** de cada commit. Para correo se usa
`override_settings` con el backend de memoria; los usuarios de prueba se crean con
`create_user(username=…, password='clave12345')`.

---

## Fase 11 — Despliegue (Render, configuración a código)

`render.yaml` (Blueprint) declara el Web Service y el PostgreSQL del plan gratuito:

```yaml
buildCommand: "pip install -r ../requirements.txt && python manage.py collectstatic --noinput"
startCommand: "python manage.py migrate && python manage.py recomprimir_fotos && python manage.py promocionar_admins && python manage.py seed_objetos_prueba && gunicorn objetos_reclamados.wsgi:application --bind 0.0.0.0:$PORT"
healthCheckPath: /
```

Variables de entorno: `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY` (Render la pide al aplicar el
blueprint), `DJANGO_ALLOWED_HOSTS` (inyectado desde el servicio), `DATABASE_URL` (inyectado desde
la base), `DJANGO_EMAIL_DOMAINS=unal.edu.co`, `DJANGO_ADMIN_EMAILS`, `GOOGLE_OAUTH_*`,
`RESEND_API_KEY`, `SITE_URL`, `FRONTEND_URL`.

`whitenoise` sirve los estáticos (sin depender de un servidor web delante) y `runtime.txt` fija
la versión de Python. `healthCheckPath: /` mantiene vivo el servicio gratuito.

---

## Fase 12 — Verificación visual headless (el método que usamos)

No confiamos en "debería verse bien": **medimos** con Chrome DevTools Protocol sobre Edge
headless, con sesión real de administrador.

```js
// node probe.js  → lanza Edge headless y mide geometría real en varios anchos
await cdp.send('Emulation.setDeviceMetricsOverride', { width: 393, height: 950, mobile: true });
await cdp.send('Network.setCookie', { name: 'sessionid', value: SID, domain: '127.0.0.1' });
await evalJs(`(() => ({
  docOverflow: document.documentElement.scrollWidth > innerWidth,
  canvas: document.getElementById('chartEstado').getBoundingClientRect()
}))()`);
```

Reglas aprendidas (importan para cualquier IA que retome este proyecto):

1. **Navega siempre con query única** (`?probe=${Date.now()}`) y `--disable-cache`:
   `Page.navigate` puede restaurar desde **bfcache** y devolver HTML viejo.
2. **No pises `ws.onmessage`**: si necesitas escuchar eventos, pasa un callback extra al
   conector.
3. **Revisa los puertos antes de iniciar un servidor**:
   `Get-NetTCPConnection -State Listen -LocalPort 8001,8002,8003`. Spyder (el IDE del
   desarrollador) reinicia su propio `runserver` y **secuestra el puerto 8003 sirviendo otra copia
   del proyecto**; por eso una medición devolvió "v24" cuando el disco ya tenía "v25".
4. **Para entrar al panel sin pelear con el login**, crea la sesión en la base por shell
   (`SessionStore` + `_auth_user_id`, `_auth_user_backend`, `_auth_user_hash`) y setea la cookie
   `sessionid`.
5. **Para probar el peor caso** (CDN lento): `Network.setBlockedURLs(['*chart.umd.min.js*'])` y
   medir con el canvas sin inicializar — así se detectó que el tamaño intrínseco del canvas
   empujaba la tarjeta.
6. **Herramientas:** el edit tool normaliza el whitespace inicial del `newString`; cuando hay
   que reindentar código usa PowerShell con **ruta absoluta** y guardar sin BOM:
   `[System.IO.File]::WriteAllText($p, $nuevo, (New-Object System.Text.UTF8Encoding($false)))`.

---

## Fase 13 — Organización final del código

`views.py` llegó a 900 líneas con 30+ vistas, así que se partió en un **paquete `views/`** por
responsabilidad:

```txt
views/
├── publico.py             # inicio y autenticación
├── estudiante.py          # búsqueda, detalle, solicitudes, apelaciones
├── panel_dashboard.py     # indicadores y gráficas
├── panel_objetos.py       # CRUD de objetos y su formato de entrega
├── panel_solicitudes.py   # revisión de solicitudes y su formato
├── panel_configuracion.py # instrucciones por sede y categorías
├── panel_usuarios.py      # gestión de cuentas
├── exportar.py            # CSV
├── errores.py             # páginas de error
└── helpers.py             # rate limiting, IP, helpers compartidos
```

`views/__init__.py` **reexporta todos los nombres** con `__all__`, de modo que `urls.py` sigue
usando `views.panel_inicio` sin cambiar ni una línea. Regla: los helpers compartidos viven en
`helpers.py`, nunca duplicados en dos módulos.

---

## Convenciones transversales (aplícalas siempre)

1. **Commits en español, sin tildes**, en imperativo y explicando el porqué:
   `evito el scroll horizontal en el resumen del panel: las tarjetas de graficos no se estiran y el
   lienzo nunca se desborda`. Commit y push en la misma tarea.
2. **Nada de secretos en el código**: `.env` local y variables en Render.
3. **Sin comentarios de relleno**; sí docstrings de Django (`verbose_name`, `help_text`) para
   documentar el dominio.
4. **Idioma:** `LANGUAGE_CODE='es'`, `TIME_ZONE='America/Bogota'`, `USE_TZ=True`, textos de
   interfaz en español.
5. **Errores siempre visibles:** `handler500` propio, logging a consola y `DJANGO_SHOW_ERRORS`
   para diagnóstico en producción.

---

# Migración a React conservando la estética (sin cambios extremos)

El repositorio ya tiene `frontend/` (Vite + React 19 + TypeScript + Tailwind 4 + TanStack Query +
react-chartjs-2) y la API REST en `registro_objetos/api/`. La regla de oro:

> **React consume la API, no reimplementa lógica; y el diseño lo dicta `estilos.css`, no los
> documentos de `desing/`.**

## 1. Tokens: el puente exacto entre los dos estilos

`frontend/src/styles/tokens.css` ya traduce el `:root` clásico a `@theme` de Tailwind. Mapeo a
respetar:

| `estilos.css` (clásico) | `tokens.css` (React) |
|---|---|
| `--primary` / `--primary-600` / `--primary-700` / `--primary-50` | `--color-primary` / `-hover` / `-dark` / `-wash` |
| `--accent` / `--accent-50` | `--color-accent` / `--color-accent-wash` |
| `--ink` / `--ink-soft` / `--muted` / `--line` / `--bg` / `--surface` | `--color-ink` / `-ink-soft` / `-muted` / `-line` / `-canvas` / `-surface` |
| `--success` / `--warning` / `--danger` / `--info` (+ sus `-50`) | `-color-success…` / `-color-warning…` / `-color-danger…` / `-color-info…` (+ `-wash`) |
| `--font-title` / `--font-body` | `--font-display` / `--font-sans` (Sora + Inter, idénticos) |
| `--radius` / `--radius-sm` | `--radius-card` (16px) / `--radius-input` (10px) |
| `--shadow-sm` / `--shadow` | `--shadow-card` / `--shadow-floating` |
| `--grad` | utilidad `.bg-hero-gradient` en `index.css` |

**Nunca inventes colores nuevos.** Si un componente necesita un color que no está en esta tabla,
falta una decisión de diseño: agrégala a **ambos** archivos a la vez.

## 2. Conservar imágenes, fuentes e iconografía

- **Fuentes:** mantén el mismo `<link>` de Google Fonts (Sora + Inter) con los mismos pesos; si
  no coinciden, los títulos cambian de forma visible.
- **Iconos:** copia los SVG inline de 24×24 de las plantillas a `components/icons.tsx` con el
  mismo `stroke="currentColor"` y `stroke-width` original. **Prohibido** usar emoji: es una regla
  del diseño institucional.
- **Iconos de categoría:** replica el mapeo de `iconos.py` como un `Record<string, JSX>` en
  TypeScript con las mismas claves (`notebook`, `pen`, `usb`, `shirt`, `phone`, `laptop`, `keys`,
  `wallet`, `card`, `watch`, `bag`, `other`). Si prefieres no duplicar, consume
  `/api/v1/categorias/` (ya devuelve `icono`) y renderiza desde ahí.
- **Fotos, capturas, logo y favicon:** reutiliza `img/` y `static/` tal cual; no las regeneres ni
  las sustituyas por placeholders.

## 3. Traducir clases a componentes sin rediseñar

Crea los componentes con los mismos nombres semánticos del CSS clásico, en
`styles/components.css` con `@layer components`:

| Clásico | Componente React |
|---|---|
| `.btn .btn-primary .btn-outline` | `<Button variant="primary\|outline">` |
| `.card-obj` + `.media` + botón anclado abajo | `<CardObjeto>` con `align-self: end` en el botón |
| `.tabla` + `.panel-tabla` | `<Tabla>` con scroller **interno** en móvil |
| `.badge-sede .badge-sede-minas/-volador` | `<BadgeSede>` |
| `.cat-chip`, `.archivo-subida`, `.toast`, `.menu-acciones-panel` | `<Chip>`, `<SubidaArchivo>`, `<Toast>`, `<MenuAcciones>` |

Mantén los mismos **puntos de quiebre**: `900px` y `560px` para el footer, `1024px` para el
panel. Y mantén el `min-width: 0` de los grid items más el `max-width: 100%` de los gráficos.

## 4. Modo oscuro idéntico

Misma clave `localStorage['tema-aplicacion']` y mismo atributo `data-tema` en `<html>`, con el
mismo script anti-FOUC. Así la preferencia sobrevive al cambio de tecnología y no quedan dos
sistemas de tema distintos.

## 5. Gráficas y descargas autenticadas

- Chart.js con `react-chartjs-2`, **mismos colores y opciones**: `borderWidth: 2`, `borderRadius: 8`,
  leyenda abajo en la dona, `beginAtZero` en las barras, y el contenedor `.chart-caja` con
  `height: 260px; max-width: 100%; overflow: hidden`.
- **PDF y CSV no se descargan con `<a href>`**: un enlace normal no puede mandar el header JWT.
  Usa el helper `descargarArchivo(path, nombre)` de `src/api/client.ts` (fetch → blob →
  `createObjectURL` → click → `revokeObjectURL`).

## 6. Autenticación en la SPA

`src/api/client.ts` ya lo resuelve: guarda el **access token en memoria** (30 min) y el **refresh
token en cookie HttpOnly** (`SameSite=None; Secure` en producción, por eso el frontend debe estar
en un dominio distinto al de la API). Ante un `401` refresca en silencio y reintenta **una sola
vez**, así un F5 no cierra la sesión. El login con Google sigue siendo 100% Django/allauth: al
autenticar, `google_auth_bridge` deja la cookie y redirige a `FRONTEND_URL/auth/callback`, y la
SPA llama a `/auth/refresh/` para tomar el control.

**Detalle importante:** en desarrollo la API se llama por `localhost` (no `127.0.0.1`), porque con
`SameSite=Lax` la cookie solo viaja entre orígenes que comparten el mismo *sitio* y el puerto
cuenta como sitio distinto.

## 7. Orden de migración, pantalla por pantalla (sin reescritura total)

1. `Home`
2. `Login` + `AuthCallback`
3. `Objetos`
4. `ObjetoDetalle`
5. `MisSolicitudes`
6. `panel/Dashboard`
7. `panel/ObjetosAdmin`
8. `panel/Solicitudes`
9. `panel/Categorias`
10. `panel/Usuarios` (incluida la firma digital)
11. `panel/ConfiguracionEntrega`

Las 1–7 están hechas; el resto usa `PanelPlaceholder` (ver `App.tsx`). **En cada paso Django sigue
sirviendo las demás rutas** (`objetos_reclamados/urls.py` permanece incluido), así que nunca hay
un momento "todo roto".

## 8. Checklist de equivalencia visual (por pantalla, antes de darla por terminada)

- [ ] Mismos colores, fuentes, radios y sombras (solo vía tokens)
- [ ] Anchos 393 / 768 / 1280 / 1440 sin scroll horizontal
- [ ] Modo claro **y** modo oscuro
- [ ] Mismos textos y mismos mensajes de validación y error
- [ ] Subida de foto y de firma con la misma compresión (cliente + servidor)
- [ ] Sin emojis; los mismos SVG
- [ ] `python manage.py test` y los tests de la API en verde
- [ ] Comparar contra las capturas de `img/capturas/` antes/después

## 9. Reglas de convivencia

- **No borres la app clásica** hasta que React tenga paridad verificada en las 11 pantallas: es tu
  red de seguridad y la documentación viva del diseño.
- Mantén `views/helpers.py`, los modelos y `formato_entrega.py` como única fuente de verdad; la API
  ya los expone, y `api/serializers.py` separa `ObjetoPublicoSerializer` de
  `ObjetoAdminSerializer` justamente para no filtrar datos del reclamante.
- Cualquier ajuste visual hecho en React debe **replicarse también en `estilos.css`** (o al
  revés), o la documentación del diseño deja de reflejar la realidad.

---

## Orden de ejecución recomendado si se retoma el proyecto

```bash
# 1. Entorno
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Base de datos y datos de arranque
cd objetos_reclamados
python manage.py migrate
python manage.py seed_demo

# 3. Servidor
python manage.py runserver

# 4. Pruebas antes de commitear
python manage.py test

# 5. Frontend (por separado, en otra terminal)
cd ..\frontend
npm install
npm run dev
```