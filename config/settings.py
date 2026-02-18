"""
Django settings for config project.
"""

from pathlib import Path
import os
import sys

# ---------------------------------------------------------
# 1. DEFINICIÓN DE RUTAS
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# ---------------------------------------------------------
# 2. SEGURIDAD
# ---------------------------------------------------------
# Intenta leer la clave desde Render, si no, usa la local por defecto
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-*8)=w4bkuv+i^mlw_@_e1)hob%5nvj*l!=d%u68weh%i3!#=1p')

# DEBUG será True en tu PC y False automáticamente al subirlo a Render
DEBUG = 'RENDER' not in os.environ

# Dominios autorizados para evitar el error DisallowedHost
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'clinica-jazmin-demo.onrender.com', # Dominio de tu servicio en Render
]

# Configuración necesaria para formularios seguros en versiones modernas de Django
CSRF_TRUSTED_ORIGINS = [
    'https://clinica-jazmin-demo.onrender.com'
]


# ---------------------------------------------------------
# 3. APLICACIONES INSTALADAS
# ---------------------------------------------------------
INSTALLED_APPS = [
    'jazzmin',  # <--- JAZZMIN SIEMPRE PRIMERO
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.core',
]


# ---------------------------------------------------------
# 4. MIDDLEWARE
# ---------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- Whitenoise para archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'


# ---------------------------------------------------------
# 5. TEMPLATES
# ---------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ---------------------------------------------------------
# 6. BASE DE DATOS
# ---------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ---------------------------------------------------------
# 7. VALIDACIÓN DE CONTRASEÑAS
# ---------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# ---------------------------------------------------------
# 8. IDIOMA Y ZONA HORARIA
# ---------------------------------------------------------
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------
# 9. ARCHIVOS ESTÁTICOS
# ---------------------------------------------------------
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'apps', 'core', 'static'),
]

# Configuración base para Whitenoise
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------
# 10. REDIRECCIONES Y CORREO
# ---------------------------------------------------------
LOGIN_URL = 'login' 
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_correo_real@gmail.com'
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'


# ---------------------------------------------------------
# 11. DISEÑO JAZZMIN (CONFIGURACIÓN VISUAL)
# ---------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "Portal Dra. Jazmin",
    "site_header": "Gestión Clínica",
    "site_brand": "Dra. Jazmin",
    "site_logo_classes": "fas fa-tooth",
    "welcome_sign": "Bienvenida al Panel de Control",
    "copyright": "Clínica Dental Digital",
    "search_model": ["core.Cita", "auth.User", "core.Paciente"],
    
    "topmenu_links": [
        {"name": "Ver Sitio Web", "url": "home", "permissions": ["auth.view_user"]},
        {"name": "Nueva Cita", "url": "admin:core_cita_add", "permissions": ["core.add_cita"]},
    ],
    
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",

        # --- ICONOS DE TUS MODELOS ---
        "core.Cita": "fas fa-calendar-check",
        "core.Servicio": "fas fa-tooth",
        "core.Documento": "fas fa-x-ray",
        "core.Paciente": "fas fa-user-injured",
        "core.Pago": "fas fa-cash-register",
        "core.Insumo": "fas fa-boxes",
        "core.Receta": "fas fa-prescription-bottle-alt",
        
        # --- NUEVOS ÍCONOS ---
        "core.FichaMedica": "fas fa-file-medical-alt", 
        "core.Producto": "fas fa-shopping-cart",       
    },
    
    "order_with_respect_to": [
        "core", 
        "core.Cita", 
        "core.Paciente", 
        "core.Receta",   
        "core.Servicio", 
        "core.Producto", 
        "core.Documento", 
        "core.Pago", 
        "core.Insumo",
        "auth"
    ],
    
    "custom_css": "css/dashboard_dental.css",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "materia",
    "navbar": "navbar-dark bg-primary",
    "sidebar": "sidebar-dark-primary",
    "no_navbar_border": True,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "layout_boxed": False,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": False,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# --- CONFIGURACIÓN AVANZADA PARA PRODUCCIÓN ---
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'