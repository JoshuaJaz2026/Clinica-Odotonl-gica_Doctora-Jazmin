from django.shortcuts import render
from .models import Servicio

def home(request):
    # Recuperamos todos los servicios de la base de datos
    servicios = Servicio.objects.all()
    return render(request, 'core/home.html', {'servicios': servicios})