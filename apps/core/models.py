from django.db import models
from django.contrib.auth.models import User
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

class Cita(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('REALIZADA', 'Realizada'),
    ]
    
    paciente = models.ForeignKey(User, on_delete=models.CASCADE)
    servicio = models.ForeignKey('Servicio', on_delete=models.CASCADE) # Comillas si Servicio está definido después, o quítalas si está antes
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    
    def __str__(self):
        return f"{self.paciente.username} - {self.fecha}"