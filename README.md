#  Entrega de Objetos Perdidos

Plataforma web para centralizar la gestión de **objetos perdidos y encontrados** en el campus universitario. Permite a los estudiantes **buscar y reclamar** sus objetos, y al personal administrativo **registrar, clasificar y hacer seguimiento** de cada entrega, con estadísticas y exportación de datos para análisis.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat-square&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/Base%20de%20datos-PostgreSQL-003B57?style=flat-square&logo=postgresql&logoColor=white)
![Auth](https://img.shields.io/badge/Auth-SSO%20Google%20%2F%20Local-4285F4?style=flat-square&logo=google&logoColor=white)

---

##  Tabla de contenidos

- [Motivación](#-motivación)
- [Funcionalidades](#-funcionalidades)
- [Roles](#-roles)
- [Flujo de trabajo](#-flujo-de-trabajo)
- [Capturas](#-capturas)
- [Tecnologías](#️-tecnologías)
- [Instalación y puesta en marcha](#️-instalación-y-puesta-en-marcha)
- [Variables de entorno](#-variables-de-entorno)
- [Seguridad](#-seguridad)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Despliegue](#-despliegue)
- [Autor](#-autor)

---

##  Motivación

Cada día se pierden y se recogen decenas de objetos en las instalaciones (termos, carnéts, celulares, cuadernos, ropa…). Este proyecto nace para resolver ese problema con una herramienta centralizada:

- **Estudiantes**: encuentran sus objetos sin tener que recorrer todos los edificios.
- **Administrativos**: llevan trazabilidad completa y recuperan el objeto en menos pasos.
- **Institución**: obtiene métricas reales (objetos más perdidos, lugares frecuentes, % de recuperación) para mejorar sus procesos.

---

##  Funcionalidades

### Rol estudiante
- Registro e inicio de sesión con **correo institucional** obligatorio (`@unal.edu.co`).
- Inicio de sesión con **Google (SSO)** restringido al dominio institucional.
- Explorar objetos disponibles con **búsqueda por texto**, **filtros por categoría** y **filtro por sede** (Sede Minas / Sede El Volador).
- Ver el detalle de cada objeto (foto, lugar, fecha, descripción, sede).
- **Solicitar el reclamo** de un objeto y consultar el estado en *Mis solicitudes*.
- **Notificación por correo** cuando el administrador aprueba o rechaza una solicitud (con datos de recogida y respuesta).
- Recuadros de **estadísticas** visibles para el estudiante ("+3 termos perdidos este mes", "28 % recuperados", etc.).

### Rol administrador
- **Dashboard** con indicadores y gráficas (Chart.js) del estado de los objetos y solicitudes.
- **CRUD completo de objetos** (categoría, foto, lugar, **sede**, estado, datos del reclamante).
- **Aprobar o rechazar solicitudes** de reclamo; al aprobar se registra al reclamante automáticamente y se le **notifica por correo**.
- **Gestión de cuentas** (crear/editar/activar/desactivar, asignar rol).
- **Gestión de categorías**.
- **Exportar datos en CSV** (incluye la sede) para análisis en Power BI / Excel.

---

##  Roles

| Rol | Qué puede hacer |
|-----|-----------------|
| Estudiante | Ver objetos, filtrar, solicitar reclamos, ver sus solicitudes y estadísticas. |
| Administrador | Todo lo anterior + panel de gestión completa y exportación de datos. |

*El superusuario del proyecto accede al [sitio de administración clásico de Django]() además del panel propio.*

---

##  Flujo de trabajo

```mermaid
flowchart LR
    A[Estudiante pierde un objeto] --> B[Se entrega en la oficina de objetos perdidos]
    B --> C[Administrador registra el objeto con foto y categoría]
    C --> D[Objeto queda en estado Disponible]
    D --> E[Estudiante lo busca y lo encuentra en el listado]
    E --> F[Estudiante envía solicitud de reclamo]
    F --> G[Administrador revisa y aprueba la solicitud]
    G --> H[Objeto pasa a Reclamado → Entregado]
    H --> I[Total actualizado en estadísticas y dashboard]
```

1. **Registro y login**: solo correos institucionales (local o Google).
2. **Publicación**: el administrador da de alta el objeto encontrado.
3. **Búsqueda**: el estudiante usa el buscador y los filtros de categoría.
4. **Solicitud**: el estudiante envía una solicitud de reclamo con su justificación.
5. **Revisión**: el administrador aprueba o rechaza; al aprobar se capturan los datos del reclamante desde su perfil.
6. **Seguimiento**: el estado del objeto cambia (Disponible → Reclamado → Entregado) y las estadísticas se actualizan.

---

##  Capturas

> Ejemplos:

| | |
|---|---|
| ![Inicio](img/capturas/home.png) | ![Listado de objetos](img/capturas/listado.png) |
| ![Detalle del objeto](img/capturas/detalle.png) | ![Panel del administrador](img/capturas/panel_inicio.png) |
| ![Solicitudes](img/capturas/solicitudes.png) | ![Exportar CSV](img/capturas/exportar.png) |

---

##  Tecnologías

- [Python 3.11](https://www.python.org/) · [Django 5.2](https://www.djangoproject.com/)
- [django-allauth](https://docs.allauth.org/) — SSO con Google restringido por dominio
- [Whitenoise](https://whitenoise.readthedocs.io/) — servir estáticos en producción
- [Gunicorn](https://gunicorn.org/) — servidor WSGI
- [SQLite](https://www.sqlite.org/) (local) · [PostgreSQL](https://www.postgresql.org/) (producción) · [Chart.js](https://www.chartjs.org/) · HTML/CSS/JS

---

##  Instalación y puesta en marcha

### Requisitos previos
- Python 3.10+
- Git

### Pasos

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/kevinramos2/Entrega-de-objetos-perdidos-.git
   cd Entrega-de-objetos-perdidos-
   ```

2. **Crear el entorno virtual**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Linux / macOS
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno (opcional en desarrollo)**
   ```bash
   # Windows (PowerShell)
   $env:DJANGO_SECRET_KEY="clave-de-desarrollo"
   $env:DJANGO_DEBUG="True"
   ```
   Sin `DJANGO_SECRET_KEY` el proyecto usa una clave de desarrollo automática.

5. **Migrar la base de datos**
   ```bash
   cd objetos_reclamados
   python manage.py migrate
   ```

6. **Cargar datos de demostración** *(opcional: usuarios y objetos de ejemplo)*
   ```bash
   python manage.py seed_demo
   ```

7. **Crear un superusuario** *(si no usaste seed_demo)*
   ```bash
   python manage.py createsuperuser
   ```

8. **Ejecutar el servidor**
   ```bash
   python manage.py runserver
   ```
   Abre [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

### Datos de demostración (seed_demo)

| Tipo | Usuario | Correo | Contraseña |
|------|---------|--------|------------|
| Administrador | `admin` | `admin@unal.edu.co` | `CambiaEsteAdmin123!` |
| Estudiante | `estudiante` | `estudiante@unal.edu.co` | `Estudiante123!` |

>  Cambia estas contraseñas antes de un despliegue real.

---

##  Variables de entorno

Toda la configuración sensible se lee desde variables de entorno o desde un archivo **`.env`** en la raíz del repositorio (el `.env` **nunca se sube a git**). En Render se definen como variables del servicio.

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DJANGO_SECRET_KEY` | Clave secreta de Django. **Obligatoria** si `DJANGO_DEBUG` es `False`. | *(clave de desarrollo)* |
| `DJANGO_DEBUG` | Activa el modo de depuración. | `True` en desarrollo |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos separados por coma. | `127.0.0.1,localhost` |
| `DATABASE_URL` | Cadena de conexión PostgreSQL. Si no existe, se usa SQLite local. | `postgres://usuario:clave@host:puerto/base` |
| `DJANGO_EMAIL_DOMAINS` | Dominios de correo autorizados separados por coma. | `unal.edu.co` |
| `DJANGO_ADMIN_EMAILS` | Correos que se **promueven automáticamente a administrador** al crear la cuenta o iniciar sesión (separados por coma). | `keramosl@unal.edu.co` |
| `GOOGLE_OAUTH_CLIENT_ID` | Client ID de Google OAuth 2.0. | *(vacío → oculta el botón de Google)* |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Client Secret de Google OAuth 2.0. | *(vacío → oculta el botón de Google)* |
| `SMTP_HOST` | Servidor SMTP de salida. Si está vacío (o falta `SMTP_USER`), los correos se imprimen en la **consola** (útil en desarrollo). | *(vacío → consola)* |
| `SMTP_USER` | Usuario SMTP (correo). Delimitador: si está vacío, no hay envío real. | *(vacío)* |
| `SMTP_PASSWORD` | Contraseña o *app password* del usuario SMTP. | *(vacío)* |
| `SMTP_PORT` | Puerto SMTP. | `587` |
| `SMTP_USE_TLS` | Usa TLS (STARTTLS). | `True` |
| `SMTP_USE_SSL` | Usa SSL directo. | `False` |
| `DEFAULT_FROM_EMAIL` | Remitente de los correos de notificación. | `objetos.perdidos@unal.edu.co` |
| `SITE_URL` | URL pública del sitio para los enlaces dentro de los correos. | `http://127.0.0.1:8000` local / `https://…onrender.com` en Render |

> **Correos en desarrollo**: sin `SMTP_HOST`/`SMTP_USER` definidos, Django usa el backend de **consola**, así que al aprobar/rechazar una solicitud verás el correo en la terminal. En **Render**, define `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_PORT` y `SITE_URL` (p. ej. `https://objetos-perdidos-d7uh.onrender.com`) para enviar avisos reales.

### ¿Dónde consigo la SECRET_KEY?

1. Genera una clave **aleatoria y única** con el propio Django:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
2. Guárdala en el archivo **`.env`** en la **raíz del repo** (crea el archivo si no existe):
   ```
   # .env  (NO se sube a git)
   DJANGO_SECRET_KEY=pega-la-clave-generada
   DJANGO_ADMIN_EMAILS=tu.correo@unal.edu.co
   DATABASE_URL=postgres://usuario:clave@host:puerto/base   # opcional en local
   ```
3. En **Render**, en lugar de `.env`, define las variables directamente en *Environment* del Web Service. **Nunca** pongas la clave suelta en el código ni la subas a GitHub.

### ¿Cómo obtengo la conexión PostgreSQL?

En Render: *New → PostgreSQL* (o *New → Add-ons → PostgreSQL*). Una vez creada, Render te da dos conexiones:
- **Internal Database URL**: `postgres://user:pass@....compute.amazonaws.com:5432/objetos_perdidos` — úsala dentro de Render (los servicios se comunican por red interna).
- **External Database URL**: para conectarte desde tu PC (p. ej. con DBeaver o un backup local).

Pega ese valor en `DATABASE_URL`.

> ⚠️ Si `DJANGO_DEBUG="False"` y falta `DJANGO_SECRET_KEY`, la aplicación **no arranca** (protección intencional). Igualmente, si `DJANGO_ALLOWED_HOSTS` no incluye el host del sitio, Django rechazará las peticiones (protección contra *host header poisoning*).

### Administrador automático por correo

La cuenta cuyo correo esté en `DJANGO_ADMIN_EMAILS` obtiene automáticamente el rol de **administrador** (`is_staff` + superusuario):
- Al registrarse con ese correo **o** al entrar con Google con ese correo se promueve en el acto (señal `post_save`).
- Para cuentas que ya existen en la base de datos, ejecuta una sola vez:
  ```bash
  python manage.py promocionar_admins
  ```
  De esta forma, **al entrar con tu correo UNAL el sistema ya te reconoce como administrador** y puedes usar el panel `/panel/` (añadir, editar y eliminar objetos, aprobar solicitudes, gestionar cuentas). El resto de estudiantes solo pueden **ver** objetos y solicitar reclamos.

---

##  Seguridad

- **Correo institucional obligatorio**: el registro local y el SSO de Google solo aceptan dominios autorizados (`unal.edu.co` por defecto). Los adaptadores de allauth bloquean el acceso con cuentas Gmail/personales.
- **Rate limiting del login**: se limita a **5 intentos fallidos en 15 minutos** por usuario y por IP; las nuevas contraseñas pasan los validadores de Django.
- **Protección CSRF**, sesiones de 2 horas que expiran al cerrar el navegador, cookies `HttpOnly`, `Secure` y `SameSite`.
- **Cabeceras seguras** en producción (HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy).
- **Validación de imágenes** (formato y tamaño ≤ 5 MB) y **taille de campos** en formularios para evitar desbordamientos e inyecciones.
- **Panel protegido**: el acceso al panel administrativo requiere el rol de administrador; cada vista del panel valida permisos.

---

##  Estructura del proyecto

```txt
Entrega-de-objetos-perdidos-/
├── objetos_reclamados/            # Proyecto Django
│   ├── objetos_reclamados/        # Configuración (settings, urls, wsgi)
│   │   ├── settings.py            # Configuración por variables de entorno
│   │   ├── urls.py                # Rutas globales
│   │   └── templates/             # Plantillas globales (404, 403)
│   ├── registro_objetos/          # Aplicación principal
│   │   ├── models.py              # Categoria, ObjetoReclamado, PerfilUsuario, SolicitudReclamacion
│   │   ├── views.py               # Vistas de estudiantes y panel
│   │   ├── forms.py               # Formularios con validación de dominio
│   │   ├── adapters.py            # Adapters allauth (dominio institucional)
│   │   ├── estadisticas.py        # Agregados para estudiantes y administradores
│   │   ├── admin.py               # Panel clásico de Django + reportes (Chart.js)
│   │   ├── management/commands/   # Comandos personalizados (seed_demo)
│   │   ├── migrations/            # Migraciones de la base de datos
│   │   ├── templates/             # Plantillas de la app y del panel
│   │   └── urls.py                # Rutas de la aplicación
│   ├── static/                    # CSS y JS propios
│   ├── manage.py                  # Utilidad de gestión
│   ├── db.sqlite3                 # Base de datos (SQLite)
│   └── runtime.txt                # Versión de Python para el despliegue
├── requirements.txt               # Dependencias del proyecto
├── README.md                      # Documentación
└── .gitignore
```

---

##  Despliegue

**Forma recomendada: Blueprint (configuración a código).**

El archivo [`render.yaml`](render.yaml) define el Web Service, el **PostgreSQL** y todas las variables. Para usarlo:

1. En Render: **Dashboard → New + → Blueprint** y elige este repositorio.
2. Render lee `render.yaml` y prepara el servicio + la base de datos.
3. Escribe el `DJANGO_SECRET_KEY` cuando Render lo pida y pulsa **Apply**.
4. El primer despliegue ejecuta `migrate` y `promocionar_admins` automáticamente.

Alternativa, configuración **manual** (sin blueprint):

1. **Base de datos**: crea un **PostgreSQL en Render** y copia su `Internal Database URL`.
2. **Runtime**: el archivo `runtime.txt` fija la versión de Python (`python-3.10.12`).
3. **Build**: instala `requirements.txt` y ejecuta `python manage.py collectstatic --noinput` (las migraciones van en migración previa al arranque: `python manage.py migrate`).
4. **Start**: `gunicorn objetos_reclamados.wsgi:application --bind 0.0.0.0:$PORT`
5. **Variables de entorno** en el panel del servicio:
   - `DJANGO_SECRET_KEY` (generada con `get_random_secret_key()`)
   - `DJANGO_DEBUG=0`
   - `DJANGO_ALLOWED_HOSTS=<tu-dominio>` (ej. `tuapp.onrender.com`)
   - `DATABASE_URL=<Internal Database URL del PostgreSQL>`
   - `DJANGO_ADMIN_EMAILS=tu.correo@unal.edu.co` (para que seas administrador automáticamente)
   - `GOOGLE_OAUTH_CLIENT_ID` y `GOOGLE_OAUTH_CLIENT_SECRET` (SSO Google)
   - En Google Cloud Console, añade las URIs de redirección:
     `https://<tu-dominio>/accounts/google/login/callback/`

### Migrar los datos existentes a PostgreSQL

La primera vez que apuntes a PostgreSQL la base de datos estará vacía. Dos opciones:

**Opción A — Empezar con los datos de demostración** *(recomendado para probar)*:
```bash
python manage.py migrate            # crea el esquema
python manage.py seed_demo          # categorías, usuarios demo y 9 objetos
python manage.py promocionar_admins # tu correo queda como administrador
```

**Opción B — Llevar los datos actuales de SQLite a PostgreSQL**:
```bash
# 1. En local (mientras la app aún usa SQLite) exporta los datos:
python manage.py dumpdata --natural-foreign --natural-primary \
  -e admin -e contenttypes -e sessions -e socialaccount -e allauth \
  -o datos.json

# 2. Con DATABASE_URL apuntando al PostgreSQL, importa:
python manage.py loaddata datos.json
```

---

##  Autor

**Kevin Ramos** — [@kevinramos2](https://github.com/kevinramos2)

Proyecto de gestión académico — Universidad Nacional de Colombia.
