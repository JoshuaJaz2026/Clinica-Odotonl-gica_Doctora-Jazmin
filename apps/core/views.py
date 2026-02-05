from django.shortcuts import render
from django.http import JsonResponse
from .models import Servicio
# from django.db.models import Q  <-- No lo estás usando por ahora, pero puedes dejarlo si planeas usarlo luego.

def home(request):
    # Recuperamos todos los servicios de la base de datos
    servicios = Servicio.objects.all()
    return render(request, 'core/home.html', {'servicios': servicios})

def bot_respuesta(request):
    mensaje = request.GET.get('msg', '').lower()
    respuesta = "Lo siento, no entendí bien. ¿Puedes intentar con las opciones del menú?"
    
    # 1. Lógica de Saludos
    if 'hola' in mensaje or 'buenos' in mensaje:
        respuesta = "¡Hola! Soy el asistente virtual de la Dra. Jazmin. ¿En qué puedo ayudarte hoy?"

    # 2. Lógica de Citas
    elif 'cita' in mensaje or 'turno' in mensaje or 'agendar' in mensaje:
        respuesta = "¡Claro! Puedes agendar tu cita llenando el formulario que está más arriba en esta página. ¿Te gustaría que te lleve ahí?"
    
    # 3. Lógica INTELIGENTE: Buscar en la Base de Datos (Precios/Servicios)
    elif 'precio' in mensaje or 'costo' in mensaje or 'servicio' in mensaje:
        # Buscamos los servicios reales en tu base de datos
        servicios = Servicio.objects.all()[:3] # Traemos los primeros 3
        
        # --- AQUÍ ESTABA EL ERROR ---
        # Corregido: "for s in servicios" en lugar de "for s.servicios"
        texto_servicios = ", ".join([f"{s.titulo} (S/ {s.precio_estimado})" for s in servicios])
        
        # Si no hay servicios cargados, damos un mensaje genérico
        if servicios:
             respuesta = f"Nuestros precios referenciales son: {texto_servicios}... y más. ¿Deseas ver la lista completa?"
        else:
             respuesta = "La consulta básica cuesta S/ 30. Para tratamientos específicos, necesitamos evaluarte."

    # 4. Lógica de Ubicación/Horario
    elif 'donde' in mensaje or 'ubicacion' in mensaje or 'direccion' in mensaje:
        respuesta = "Estamos en Av. Principal 123, Lima. Justo frente al parque. ¡Es muy fácil llegar!"
        
    elif 'horario' in mensaje or 'hora' in mensaje:
        respuesta = "Atendemos de Lunes a Viernes de 9am a 8pm, y Sábados hasta las 6pm."

    return JsonResponse({'respuesta': respuesta})