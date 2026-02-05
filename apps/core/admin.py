from django.contrib import admin
from .models import Servicio

# Esto activa la tabla en el panel
@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'precio_estimado', 'created_at')
    search_fields = ('titulo',)