from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# ---------------------------------------------------------
# 1. MODELO SERVICIO
# ---------------------------------------------------------
class Servicio(models.Model):
    titulo = models.CharField(max_length=100, verbose_name="Nombre del Servicio")
    descripcion = models.TextField(verbose_name="Descripción")
    imagen = models.ImageField(upload_to='servicios/', verbose_name="Imagen")
    precio_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

# ---------------------------------------------------------
# 2. MODELO CITA
# ---------------------------------------------------------
class Cita(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Paciente")
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, verbose_name="Servicio")
    fecha = models.DateField(verbose_name="Fecha de Cita")
    hora = models.TimeField(verbose_name="Hora de Cita")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente', verbose_name="Estado")

    def __str__(self):
        return f"{self.paciente.first_name} - {self.fecha} ({self.hora})"

    def clean(self):
        existe_cita = Cita.objects.filter(
            fecha=self.fecha, 
            hora=self.hora
        ).exclude(pk=self.pk).exists()

        if existe_cita:
            raise ValidationError({
                'hora': f'Lo sentimos, ya existe una cita programada para el {self.fecha} a las {self.hora}.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Cita, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"

# ---------------------------------------------------------
# 3. MODELO PAGO
# ---------------------------------------------------------
class Pago(models.Model):
    METODOS = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('yape_plin', 'Yape / Plin'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
    ]

    cita = models.OneToOneField(Cita, on_delete=models.CASCADE, related_name='pago', verbose_name="Cita Asociada")
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo Total (S/)")
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Abonado (S/)")
    metodo = models.CharField(max_length=20, choices=METODOS, verbose_name="Método de Pago")
    fecha_pago = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Transacción")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas (Nro Operación/Detalles)")

    @property
    def saldo_pendiente(self):
        return self.monto_total - self.monto_pagado

    @property
    def estado_pago(self):
        if self.saldo_pendiente <= 0: return "COMPLETO"
        elif self.monto_pagado > 0: return "PARCIAL"
        return "PENDIENTE"

    def __str__(self):
        return f"Pago de {self.cita.paciente.first_name} - S/ {self.monto_pagado}"

    class Meta:
        verbose_name = "Pago / Ingreso"
        verbose_name_plural = "Control de Caja (Pagos)"

# ---------------------------------------------------------
# 4. MODELO DOCUMENTO
# ---------------------------------------------------------
class Documento(models.Model):
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documentos', verbose_name="Paciente")
    titulo = models.CharField(max_length=100, verbose_name="Título del documento/estudio")
    archivo = models.FileField(upload_to='historias_clinicas/', verbose_name="Archivo (Radiografía o PDF)")
    notas = models.TextField(blank=True, verbose_name="Notas u Observaciones")
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    def __str__(self):
        return f"{self.titulo} - {self.paciente.first_name}"

    class Meta:
        verbose_name = "Documento/Radiografía"
        verbose_name_plural = "Historial Clínico (Documentos)"

# ---------------------------------------------------------
# 5. MODELO PACIENTE (Proxy)
# ---------------------------------------------------------
class Paciente(User):
    class Meta:
        proxy = True 
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'

# ---------------------------------------------------------
# 6. MODELO INSUMO (Inventario) 📦
# ---------------------------------------------------------
class Insumo(models.Model):
    UNIDADES = [
        ('unidad', 'Unidades'),
        ('caja', 'Cajas'),
        ('litro', 'Litros'),
        ('botella', 'Botellas'),
        ('paquete', 'Paquetes'),
    ]

    nombre = models.CharField(max_length=100, verbose_name="Nombre del Material")
    cantidad = models.PositiveIntegerField(verbose_name="Stock Actual")
    stock_minimo = models.PositiveIntegerField(default=5, verbose_name="Alerta de Stock Mínimo")
    unidad = models.CharField(max_length=20, choices=UNIDADES, default='unidad')
    fecha_vencimiento = models.DateField(null=True, blank=True, verbose_name="Caducidad")
    
    @property
    def estado_stock(self):
        if self.cantidad == 0: return "AGOTADO"
        elif self.cantidad <= self.stock_minimo: return "BAJO"
        return "OK"

    def __str__(self):
        return f"{self.nombre} ({self.cantidad} {self.unidad})"

    class Meta:
        verbose_name = "Insumo / Material"
        verbose_name_plural = "Inventario (Almacén)"

# ---------------------------------------------------------
# 7. MODELO RECETA MÉDICA 💊
# ---------------------------------------------------------
class Receta(models.Model):
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recetas', verbose_name="Paciente")
    cita = models.ForeignKey(Cita, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cita Relacionada")
    
    diagnostico = models.TextField(verbose_name="Diagnóstico")
    medicamentos = models.TextField(verbose_name="Medicamentos e Indicaciones", help_text="Ej: Amoxicilina 500mg - Tomar cada 8 horas por 5 días.")
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Emisión")
    proxima_cita = models.DateField(null=True, blank=True, verbose_name="Sugerencia Próxima Cita")

    def __str__(self):
        return f"Receta para {self.paciente.first_name} ({self.fecha_emision.strftime('%d/%m/%Y')})"

    class Meta:
        verbose_name = "Receta Médica"
        verbose_name_plural = "Gestión de Recetas"

# ---------------------------------------------------------
# 8. MODELO FICHA MÉDICA (ANAMNESIS) 🩺 (NUEVO)
# ---------------------------------------------------------
class FichaMedica(models.Model):
    paciente = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ficha_medica', verbose_name="Paciente")
    
    es_alergico = models.BooleanField(default=False, verbose_name="¿Tiene Alergias?")
    alergias_detalle = models.CharField(max_length=200, blank=True, verbose_name="¿A qué es alérgico?", help_text="Ej: Penicilina, Látex")
    
    tiene_enfermedad = models.BooleanField(default=False, verbose_name="¿Enfermedad Crónica?")
    enfermedad_detalle = models.CharField(max_length=200, blank=True, verbose_name="Nombre de la enfermedad", help_text="Ej: Diabetes, Hipertensión")
    
    toma_medicamentos = models.BooleanField(default=False, verbose_name="¿Toma Medicamentos?")
    medicamentos_detalle = models.CharField(max_length=200, blank=True, verbose_name="¿Cuáles?", help_text="Ej: Aspirina diaria")
    
    esta_embarazada = models.BooleanField(default=False, verbose_name="¿Está embarazada?")
    observaciones = models.TextField(blank=True, verbose_name="Otras observaciones médicas")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    def __str__(self):
        return f"Ficha de {self.paciente.first_name}"

    class Meta:
        verbose_name = "Ficha Médica"
        verbose_name_plural = "Fichas Médicas"

# ---------------------------------------------------------
# 9. MODELO PRODUCTO (TIENDA) 🛒 (NUEVO)
# ---------------------------------------------------------
class Producto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Producto")
    descripcion = models.TextField(verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (S/)")
    imagen = models.ImageField(upload_to='productos/', verbose_name="Foto del Producto")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock Disponible")
    
    def __str__(self):
        return f"{self.nombre} - S/ {self.precio}"

    class Meta:
        verbose_name = "Producto en Venta"
        verbose_name_plural = "Tienda (Productos)"