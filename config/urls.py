"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
]

# --- CONFIGURACIÓN PARA MODO DESARROLLO (DEBUG) ---
if settings.DEBUG:
    # 1. Multimedia (Fotos)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # 2. Estáticos (CSS/JS)
    # AHORA SÍ FUNCIONARÁ PORQUE LA CARPETA ESTÁ BIEN DEFINIDA EN SETTINGS
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])