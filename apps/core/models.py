from django.db import models

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