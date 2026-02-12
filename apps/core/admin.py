from django import forms 
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db import models 

# --- IMPORTS PARA PDF (RECETAS) ---
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# --- IMPORTS PARA EXCEL ---
import xlwt
from django.http import HttpResponse
from datetime import datetime

# IMPORTAMOS TODOS LOS MODELOS
from .models import Servicio, Cita, Paciente, Documento, Pago, Insumo, Receta 

# ---------------------------------------------------------------
# 0. INLINES
# ---------------------------------------------------------------
class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 1
    fields = ('titulo', 'archivo', 'notas', 'fecha_subida')
    readonly_fields = ('fecha_subida',)

class PagoInline(admin.StackedInline):
    model = Pago
    can_delete = False
    verbose_name_plural = 'Registro de Pago (Caja)'

# ---------------------------------------------------------------
# 1. FORMULARIOS
# ---------------------------------------------------------------
class PacienteAdminForm(forms.ModelForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance.pk is None: 
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("¡Error! Este correo ya está registrado.")
        else: 
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("¡Error! Este correo pertenece a otro usuario.")
        return email

# ---------------------------------------------------------------
# 2. CONFIGURACIÓN DE MODELOS
# ---------------------------------------------------------------
@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'precio_estimado')
    search_fields = ('titulo',)

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente_nombre', 'boton_whatsapp', 'servicio', 'fecha', 'hora', 'estado_pago_visual', 'estado')
    list_filter = ('estado', 'fecha', 'servicio')
    date_hierarchy = 'fecha'
    inlines = [PagoInline] 
    actions = ['marcar_como_finalizada', 'marcar_como_cancelada', 'exportar_a_excel']

    def paciente_nombre(self, obj):
        return f"{obj.paciente.first_name} {obj.paciente.last_name}"
    
    def estado_pago_visual(self, obj):
        if hasattr(obj, 'pago'):
            saldo = obj.pago.saldo_pendiente
            if saldo <= 0:
                return format_html('<span style="color: green; font-weight: bold;">PAGADO</span>')
            else:
                return format_html(f'<span style="color: red; font-weight: bold;">DEBE S/ {saldo}</span>')
        return "Sin registro"
    estado_pago_visual.short_description = "Estado de Pago"

    def boton_whatsapp(self, obj):
        telefono = getattr(obj.paciente, 'telefono', '') 
        if not telefono: telefono = "999999999"
        mensaje = f"Hola {obj.paciente.first_name}, cita confirmada para el {obj.fecha}."
        url = f"https://wa.me/51{telefono}?text={mensaje}"
        return format_html('<a href="{}" target="_blank" style="background-color: #25D366; color: white; padding: 4px 12px; border-radius: 20px; text-decoration: none; font-weight: bold; font-size: 12px;">WhatsApp</a>', url)

    @admin.action(description='✅ Finalizar Citas')
    def marcar_como_finalizada(self, request, queryset):
        queryset.update(estado='finalizada')

    @admin.action(description='❌ Cancelar Citas')
    def marcar_como_cancelada(self, request, queryset):
        queryset.update(estado='cancelada')

    @admin.action(description='📊 Exportar a Excel')
    def exportar_a_excel(self, request, queryset):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="Reporte_{datetime.now().strftime("%Y%m%d")}.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Citas')
        headers = ['Paciente', 'Servicio', 'Fecha', 'Hora', 'Estado', 'Pago', 'Monto']
        for col, h in enumerate(headers): ws.write(0, col, h, xlwt.XFStyle())
        for row, obj in enumerate(queryset, 1):
            pago_info = "Sin pago"
            monto = 0
            if hasattr(obj, 'pago'):
                pago_info = obj.pago.estado_pago
                monto = obj.pago.monto_pagado
            ws.write(row, 0, f"{obj.paciente.first_name} {obj.paciente.last_name}")
            ws.write(row, 1, obj.servicio.titulo)
            ws.write(row, 2, str(obj.fecha))
            ws.write(row, 3, str(obj.hora))
            ws.write(row, 4, obj.get_estado_display())
            ws.write(row, 5, pago_info)
            ws.write(row, 6, str(monto))
        wb.save(response)
        return response

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('cita', 'monto_total', 'monto_pagado', 'saldo_pendiente', 'metodo', 'fecha_pago')
    list_filter = ('metodo', 'fecha_pago')

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'paciente', 'fecha_subida')

# ---------------------------------------------------------
# 3. CONFIGURACIÓN DE INVENTARIO 📦
# ---------------------------------------------------------
@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad_visual', 'unidad', 'fecha_vencimiento', 'estado_visual')
    list_filter = ('unidad',)
    search_fields = ('nombre',)
    ordering = ('cantidad',)

    def cantidad_visual(self, obj):
        if obj.cantidad <= obj.stock_minimo:
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', obj.cantidad)
        return obj.cantidad
    cantidad_visual.short_description = "Stock Actual"

    def estado_visual(self, obj):
        if obj.cantidad == 0:
            return format_html('<span style="background-color: red; color: white; padding: 3px 10px; border-radius: 10px;">AGOTADO</span>')
        elif obj.cantidad <= obj.stock_minimo:
            return format_html('<span style="background-color: orange; color: black; padding: 3px 10px; border-radius: 10px;">BAJO STOCK</span>')
        return format_html('<span style="color: green;">✔ Disponible</span>')
    estado_visual.short_description = "Estado"

# ---------------------------------------------------------
# 4. CONFIGURACIÓN DE RECETAS 💊 (CON PDF)
# ---------------------------------------------------------
@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'cita', 'fecha_emision', 'proxima_cita')
    list_filter = ('fecha_emision',)
    search_fields = ('paciente__first_name', 'diagnostico', 'medicamentos')
    readonly_fields = ('fecha_emision',)
    
    # ACCIÓN NUEVA PARA IMPRIMIR
    actions = ['imprimir_receta_pdf'] 
    
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 10, 'cols': 80})},
    }

    # --- FUNCIÓN GENERADORA DE PDF ---
    @admin.action(description='🖨️ Imprimir Receta (PDF)')
    def imprimir_receta_pdf(self, request, queryset):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        for receta in queryset:
            # ENCABEZADO
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, height - 50, "CLÍNICA DENTAL DRA. JAZMIN")
            p.setFont("Helvetica", 10)
            p.drawString(50, height - 70, "Av. Principal 123 - Lima, Perú | Tel: 999-999-999")
            p.line(50, height - 80, width - 50, height - 80)

            # DATOS PACIENTE
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, height - 110, f"PACIENTE: {receta.paciente.first_name} {receta.paciente.last_name}")
            p.setFont("Helvetica", 10)
            p.drawString(400, height - 110, f"FECHA: {receta.fecha_emision.strftime('%d/%m/%Y')}")
            
            # DIAGNÓSTICO
            p.setFont("Helvetica-Bold", 11)
            p.drawString(50, height - 150, "DIAGNÓSTICO:")
            p.setFont("Helvetica", 10)
            p.drawString(50, height - 165, receta.diagnostico)

            # MEDICAMENTOS
            p.setFont("Helvetica-Bold", 11)
            p.drawString(50, height - 200, "INDICACIONES MÉDICAS (RP):")
            
            text_object = p.beginText(50, height - 220)
            text_object.setFont("Helvetica", 10)
            # Separamos por saltos de línea para que se vea ordenado
            lines = receta.medicamentos.split('\n')
            for line in lines:
                text_object.textLine(line)
            p.drawText(text_object)

            # PIE DE PÁGINA
            p.line(50, 150, 250, 150)
            p.setFont("Helvetica", 9)
            p.drawString(80, 135, "Firma Dra. Jazmín")
            p.drawString(50, 50, "Nota: Esta receta es válida por 30 días.")
            if receta.proxima_cita:
                p.drawString(50, 35, f"Próxima cita sugerida: {receta.proxima_cita}")
            
            p.showPage() # Fin de página

        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Receta_{datetime.now().strftime("%Y%m%d")}.pdf"'
        return response

# ---------------------------------------------------------------
# 5. USUARIOS
# ---------------------------------------------------------------
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    form = PacienteAdminForm 
    list_display = ('username', 'first_name', 'last_name', 'email', 'es_activo')
    inlines = [DocumentoInline]
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=False)
    fields = ('username', 'first_name', 'last_name', 'email', 'password', 'is_active')
    def es_activo(self, obj): return obj.is_active
    es_activo.boolean = True
    def save_model(self, request, obj, form, change):
        if not change or 'password' in form.changed_data:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

try: admin.site.unregister(User)
except admin.sites.NotRegistered: pass

@admin.register(User)
class StaffUserAdmin(UserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=True)