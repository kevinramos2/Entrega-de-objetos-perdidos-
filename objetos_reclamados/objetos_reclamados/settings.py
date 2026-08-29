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

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Seguridad
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    # Dev only: nunca cambiar por un valor hardcodeado en producción.
    'django-insecure-#9fa_rv7^=0%r4jkdt24p@oe%1w6+=wcxkm0+reunx6urbz$7#'
)

DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes')

allowed_hosts = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts.split(',') if h.strip()]

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
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Restricción de dominio del correo institucional (adapter personalizado)
ALLOWED_EMAIL_DOMAINS = ALLOWED_EMAIL_DOMAINS or ['unal.edu.co']
SOCIALACCOUNT_ADAPTER = 'registro_objetos.adapters.CorreoInstitucionalAdapter'
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