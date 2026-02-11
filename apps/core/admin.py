from django import forms 
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Servicio, Cita, Paciente, Documento # <--- Importamos Documento

# --- IMPORTS PARA EXCEL ---
import xlwt
from django.http import HttpResponse
from datetime import datetime

# ---------------------------------------------------------------
# 0. CONFIGURACIÓN DEL HISTORIAL CLÍNICO (INLINE) 📁
# ---------------------------------------------------------------
class DocumentoInline(admin.TabularInline):
    """Permite subir archivos directamente desde la ficha del paciente"""
    model = Documento
    extra = 1  # Espacio vacío para subir un nuevo archivo
    fields = ('titulo', 'archivo', 'notas', 'fecha_subida')
    readonly_fields = ('fecha_subida',)

# ---------------------------------------------------------------
# 1. FORMULARIO DE VALIDACIÓN
# ---------------------------------------------------------------
class PacienteAdminForm(forms.ModelForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance.pk is None: 
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("¡Error! Este correo ya está registrado por otro paciente.")
        else: 
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("¡Error! Este correo pertenece a otro usuario.")
        return email

# ---------------------------------------------------------------
# 2. Configuración del Modelo SERVICIO
# ---------------------------------------------------------------
@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'precio_estimado')
    search_fields = ('titulo',)
    list_filter = ('precio_estimado',)
    ordering = ('titulo',)

# ---------------------------------------------------------------
# 3. Configuración del Modelo CITA (Con Exportación a Excel)
# ---------------------------------------------------------------
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente_nombre', 'boton_whatsapp', 'servicio', 'fecha', 'hora', 'estado')
    list_filter = ('estado', 'fecha', 'servicio')
    date_hierarchy = 'fecha'
    
    search_fields = ('paciente__first_name', 'paciente__last_name', 'paciente__username', 'servicio__titulo')
    search_help_text = "Busque por nombre del paciente, apellido o tratamiento."
    
    list_editable = ('estado',)
    ordering = ('-fecha', 'hora')
    list_per_page = 20
    
    actions = ['marcar_como_finalizada', 'marcar_como_cancelada', 'exportar_a_excel']

    def paciente_nombre(self, obj):
        return f"{obj.paciente.first_name} {obj.paciente.last_name}"
    paciente_nombre.short_description = "Paciente"
    paciente_nombre.admin_order_field = 'paciente__first_name'

    def boton_whatsapp(self, obj):
        telefono = getattr(obj.paciente, 'telefono', '') 
        if not telefono: telefono = "999999999"
        mensaje = f"Hola {obj.paciente.first_name}, le recordamos su cita de {obj.servicio} para el {obj.fecha} a las {obj.hora}."
        url = f"https://wa.me/51{telefono}?text={mensaje}"
        return format_html(
            '''<a href="{}" target="_blank" style="background-color: #25D366; color: white; padding: 4px 12px; border-radius: 20px; text-decoration: none; font-weight: bold; font-size: 12px; display: inline-flex; align-items: center; gap: 5px;"><i class="fab fa-whatsapp"></i> Confirmar</a>''', 
            url
        )
    boton_whatsapp.short_description = "Recordatorio"

    @admin.action(description='✅ Marcar seleccionadas como Finalizadas')
    def marcar_como_finalizada(self, request, queryset):
        queryset.update(estado='finalizada')

    @admin.action(description='❌ Marcar seleccionadas como Canceladas')
    def marcar_como_cancelada(self, request, queryset):
        queryset.update(estado='cancelada')

    @admin.action(description='📊 Exportar seleccionadas a Excel')
    def exportar_a_excel(self, request, queryset):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="Agenda_Dental_{datetime.now().strftime("%Y%m%d")}.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Citas')
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columnas = ['Paciente', 'Servicio', 'Fecha', 'Hora', 'Estado']
        for col_num in range(len(columnas)):
            ws.write(0, col_num, columnas[col_num], font_style)
        font_style = xlwt.XFStyle()
        for row_num, obj in enumerate(queryset, 1):
            ws.write(row_num, 0, f"{obj.paciente.first_name} {obj.paciente.last_name}")
            ws.write(row_num, 1, obj.servicio.titulo)
            ws.write(row_num, 2, str(obj.fecha))
            ws.write(row_num, 3, str(obj.hora))
            ws.write(row_num, 4, obj.get_estado_display())
        wb.save(response)
        return response

# ---------------------------------------------------------------
# 4. Configuración para PACIENTES (Con Historial Integrado) 👤
# ---------------------------------------------------------------
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    form = PacienteAdminForm 
    list_display = ('username', 'first_name', 'last_name', 'email', 'es_activo')
    
    # Integramos los documentos para que aparezcan al final de la ficha
    inlines = [DocumentoInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=False, is_superuser=False)
    
    search_fields = ('first_name', 'last_name', 'username', 'email')
    search_help_text = "Busque por usuario, nombre o correo."
    list_filter = ('is_active', 'date_joined')
    fields = ('username', 'first_name', 'last_name', 'email', 'password', 'is_active')

    def es_activo(self, obj):
        return obj.is_active
    es_activo.boolean = True
    es_activo.short_description = 'Activo'

    def save_model(self, request, obj, form, change):
        if not change or 'password' in form.changed_data:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

# ---------------------------------------------------------------
# 5. Registro de DOCUMENTOS (Independiente) 📄
# ---------------------------------------------------------------
@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'paciente', 'fecha_subida')
    search_fields = ('titulo', 'paciente__first_name', 'paciente__last_name')
    list_filter = ('fecha_subida',)

# ---------------------------------------------------------------
# 6. Configuración para USUARIOS STAFF
# ---------------------------------------------------------------
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class StaffUserAdmin(UserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=True)