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
# 2. MODELO CITA (Con validación de horarios)
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
        # Validación de choque de horarios
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
# 3. NUEVO: MODELO DOCUMENTO (Historial Clínico / Radiografías)
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
# 4. MODELO PACIENTE (Proxy)
# ---------------------------------------------------------
class Paciente(User):
    class Meta:
        proxy = True 
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'