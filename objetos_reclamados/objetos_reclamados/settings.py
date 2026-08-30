"""
Configuración de Django para el proyecto objetos_reclamados.

Incluye:
  - Aplicaciones del sitio (registro_objetos)
  - Autenticación local + social (Google con correo institucional)
  - Seguridad: secretos desde variables de entorno, protección CSRF,
    parámetros HSTS/Cookies en producción y validación de ALLOWED_HOSTS.
  - Estáticos (Whitenoise) y medios configurados para producción.

Variables de entorno (opcionales en desarrollo, obligatorias en producción):
  DJANGO_SECRET_KEY        Clave secreta de la aplicación.
  DJANGO_DEBUG             "True"/"False" (por defecto True en desarrollo).
  DJANGO_ALLOWED_HOSTS     Hosts permitidos separados por coma.
  DJANGO_EMAIL_DOMAINS     Dominios de correo permitidos (ej. unal.edu.co).
  GOOGLE_OAUTH_CLIENT_ID   Cliente OAuth de Google (login con G Suite/Google).
  GOOGLE_OAUTH_CLIENT_SECRET  Secreto OAuth de Google.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
RAIZ_PROYECTO = BASE_DIR.parent

# Carga variables desde un archivo .env si existe (raíz del repo o del proyecto).
# Las variables de entorno reales (p. ej. las de Render) tienen prioridad.
load_dotenv(RAIZ_PROYECTO / '.env')
load_dotenv(BASE_DIR / '.env')

# ---------------------------------------------------------------------------
# Seguridad
# ---------------------------------------------------------------------------
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes')

# Modo diagnóstico: con DJANGO_SHOW_ERRORS=1 se dibuja el traceback en la
# página de error 500 (útil cuando Render no muestra logs). Nunca en producción.
SHOW_TRACEBACKS = os.getenv('DJANGO_SHOW_ERRORS', '0').lower() in ('1', 'true', 'yes')

# Los errores (500) siempre se imprimen a la consola para poder verlos en los
# logs de Render, aunque DJANGO_DEBUG esté desactivado.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'consola_formato': {
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        },
    },
    'handlers': {
        'consola': {
            'class': 'logging.StreamHandler',
            'formatter': 'consola_formato',
        },
    },
    'loggers': {
        'django': {'handlers': ['consola'], 'level': 'INFO'},
        'django.request': {
            'handlers': ['consola'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# En producción la clave debe venir de una variable de entorno o .env.
# Nunca uses una clave hardcodeada en producción.
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-only-no-usar-en-produccion'  # solo local
    else:
        raise RuntimeError('DJANGO_SECRET_KEY es obligatoria cuando DJANGO_DEBUG=False.')

allowed_hosts = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts.split(',') if h.strip()]

# En Render el hostname real lo inyecta la plataforma y las URLs son *.onrender.com.
# Los blueprints pueden asignar nombres con sufijos (ej. objetos-perdidos-d7uh.onrender.com).
render_host = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if render_host:
    ALLOWED_HOSTS.append(render_host)

if os.getenv('RENDER'):
    ALLOWED_HOSTS.append('.onrender.com')

if DEBUG:
    # El cliente de pruebas de Django usa el host 'testserver'
    ALLOWED_HOSTS.append('testserver')

if not DEBUG and not os.getenv('DJANGO_ALLOWED_HOSTS'):
    raise RuntimeError(
        'DJANGO_ALLOWED_HOSTS es obligatorio cuando DJANGO_DEBUG=False.'
    )

# Aplicación definition
INSTALLED_APPS = [
    'registro_objetos',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Autenticación social (Google / correo institucional)
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Servir estáticos en producción (evita dependencia del servidor web)
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'objetos_reclamados.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'objetos_reclamados' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'registro_objetos.context_processors.globales',
            ],
        },
    },
]

WSGI_APPLICATION = 'objetos_reclamados.wsgi.application'

# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------
# Si existe DATABASE_URL se usa PostgreSQL (p. ej. el PostgreSQL de Render).
# En desarrollo local, sin DATABASE_URL, se usa SQLite.
import dj_database_url  # noqa: E402

DATABASES = {'default': dj_database_url.config(conn_max_age=600)} if os.getenv('DATABASE_URL') else {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------------------------------------------------------------------------
# Emails con rol de administrador automático
# Una cuenta cuyo correo esté en DJANGO_ADMIN_EMAILS se promueve a
# administrador (is_staff=True) en el momento en que se crea o inicia sesión.
# ---------------------------------------------------------------------------
EMAILS_ADMINISTRADOR = {
    e.strip().lower()
    for e in os.getenv(
        'DJANGO_ADMIN_EMAILS',
        'keramosl@unal.edu.co',  # Cuenta institucional del autor del proyecto
    ).split(',')
    if e.strip()
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Internacionalización
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Archivos estáticos y medios
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Límites de subida para las fotos de objetos
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

# ---------------------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------------------
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    # Login con Google (correo institucional)
    'allauth.account.auth_backends.AuthenticationBackend',
    # Login clásico con usuario y contraseña
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'panel_inicio'
LOGOUT_REDIRECT_URL = 'inicio'

# ---- Autenticación social (Google / correo institucional) ----------------
# Dominios autorizados para crear/ingresar con correo institucional.
# Se separan por coma: "unal.edu.co,unalvirtual.edu.co"
ALLOWED_EMAIL_DOMAINS = [
    d.strip().lower()
    for d in os.getenv('DJANGO_EMAIL_DOMAINS', 'unal.edu.co').split(',')
    if d.strip()
]

GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '')
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', '')

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': GOOGLE_OAUTH_CLIENT_ID,
            'secret': GOOGLE_OAUTH_CLIENT_SECRET,
            'key': '',
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {
            'access_type': 'online',
            # prompt=login: obliga a Google a pedir credenciales de nuevo en
            # cada inicio de sesión (no entra directo con la sesión guardada).
            'prompt': 'login',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Restricción de dominio del correo institucional (adapter personalizado)
ALLOWED_EMAIL_DOMAINS = ALLOWED_EMAIL_DOMAINS or ['unal.edu.co']
SOCIALACCOUNT_ADAPTER = 'registro_objetos.adapters.CorreoInstitucionalAdapter'

# Cuentas que ya existen con el mismo correo institucional (p. ej. el admin)
# deben enlazarse a su cuenta de Google en lugar de pedir un alta nueva.
# Google + restricción de dominio hacen esto seguro.
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
ACCOUNT_ADAPTER = 'registro_objetos.adapters.CuentaDominioAdapter'
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'none'  # El dominio institucional ya valida la identidad
ACCOUNT_LOGIN_REDIRECT_URL = 'panel_inicio'
ACCOUNT_SIGNUP_REDIRECT_URL = 'panel_inicio'
LOGIN_REDIRECT_URL = 'panel_inicio'

# ---------------------------------------------------------------------------
# Seguridad HTTP (se activan en producción)
# ---------------------------------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL', 'False').lower() in ('1', 'true')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SECURE_HSTS_SECONDS = 31536000          # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# Valor por defecto razonable en desarrollo
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60 * 60 * 2  # 2 horas
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'