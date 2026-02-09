from django.contrib import admin
from .models import Servicio, Cita

# 1. Configuración del Modelo SERVICIO
@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    # Solo mostramos columnas que realmente existen en la BD
    list_display = ('titulo', 'precio_estimado') 
    search_fields = ('titulo',)

# 2. Configuración del Modelo CITA (Panel de Control de la Doctora)
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    # IMPORTANTE: Para que 'list_editable' funcione, 'estado' DEBE estar aquí.
    list_display = ('paciente_nombre', 'servicio', 'fecha', 'hora', 'estado')
    
    # Filtros laterales
    list_filter = ('estado', 'fecha', 'servicio')
    
    # Barra de búsqueda
    search_fields = ('paciente__first_name', 'paciente__last_name', 'paciente__username')
    
    # Esto habilita el menú desplegable para cambiar estados rápido
    list_editable = ('estado',)
    
    # Orden: Las citas más recientes primero (el signo menos invierte el orden)
    ordering = ('-fecha', 'hora')
    
    list_per_page = 20

    # Función para mostrar nombre completo
    def paciente_nombre(self, obj):
        return f"{obj.paciente.first_name} {obj.paciente.last_name}"
    paciente_nombre.short_description = "Paciente"