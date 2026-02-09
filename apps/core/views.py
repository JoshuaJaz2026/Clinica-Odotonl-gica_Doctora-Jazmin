from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Servicio, Cita  # <--- IMPORTANTE: Agregamos Cita aquí
from .forms import RegistroPacienteForm

# ---------------------------------------------------------
# VISTAS PÚBLICAS
# ---------------------------------------------------------

def home(request):
    """
    Vista principal que carga la landing page y los servicios.
    """
    servicios = Servicio.objects.all()
    return render(request, 'core/home.html', {'servicios': servicios})

def bot_respuesta(request):
    """
    Lógica del Chatbot para responder dudas automáticamente.
    """
    mensaje = request.GET.get('msg', '').lower()
    respuesta = "Lo siento, no entendí bien. ¿Puedes intentar con las opciones del menú?"
    
    # 1. Lógica de Saludos
    if 'hola' in mensaje or 'buenos' in mensaje:
        respuesta = "¡Hola! Soy el asistente virtual de la Dra. Jazmin. ¿En qué puedo ayudarte hoy?"

    # 2. Lógica de Citas
    elif 'cita' in mensaje or 'turno' in mensaje or 'agendar' in mensaje:
        respuesta = "¡Claro! Puedes agendar tu cita llenando el formulario que está más arriba en esta página, o registrándote en nuestro portal para gestionarlas mejor."
    
    # 3. Lógica INTELIGENTE: Buscar en la Base de Datos (Precios/Servicios)
    elif 'precio' in mensaje or 'costo' in mensaje or 'servicio' in mensaje:
        servicios_db = Servicio.objects.all()[:3]
        texto_servicios = ", ".join([f"{s.titulo} (S/ {s.precio_estimado})" for s in servicios_db])
        
        if servicios_db:
             respuesta = f"Nuestros precios referenciales son: {texto_servicios}... y más. Puedes ver todos en la sección de Servicios."
        else:
             respuesta = "La consulta básica cuesta S/ 30. Para tratamientos específicos, necesitamos evaluarte."

    # 4. Lógica de Ubicación/Horario
    elif 'donde' in mensaje or 'ubicacion' in mensaje or 'direccion' in mensaje:
        respuesta = "Estamos en Av. Principal 123, Lima. Justo frente al parque. ¡Es muy fácil llegar!"
        
    elif 'horario' in mensaje or 'hora' in mensaje:
        respuesta = "Atendemos de Lunes a Viernes de 9am a 8pm, y Sábados hasta las 6pm."

    # 5. Ayuda con el Login
    elif 'entrar' in mensaje or 'login' in mensaje or 'cuenta' in mensaje:
        respuesta = "Puedes acceder a tu cuenta haciendo clic en el botón 'Ingresar' del menú superior."

    return JsonResponse({'respuesta': respuesta})

# ---------------------------------------------------------
# SISTEMA DE USUARIOS Y CITAS (ACTUALIZADO)
# ---------------------------------------------------------

def registro(request):
    """
    Permite a un nuevo paciente crear su cuenta.
    """
    if request.method == 'POST':
        form = RegistroPacienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistroPacienteForm()
    
    return render(request, 'registration/registro.html', {'form': form})

@login_required
def dashboard(request):
    """
    Portal privado del paciente. Muestra sus citas reales.
    """
    # 1. Recuperar las citas de ESTE paciente (usuario logueado)
    # Las ordenamos por fecha para ver las más próximas primero
    mis_citas = Cita.objects.filter(paciente=request.user).order_by('fecha', 'hora')
    
    # 2. Recuperar servicios para el select del Modal de "Nueva Cita"
    servicios = Servicio.objects.all()
    
    context = {
        'nombre_paciente': request.user.first_name,
        'citas': mis_citas,      # <--- Pasamos las citas reales al HTML
        'servicios': servicios   # <--- Pasamos los servicios al HTML
    }
    return render(request, 'pacientes/dashboard.html', context)

@login_required
def crear_cita(request):
    """
    Procesa el formulario del Modal para guardar una nueva cita.
    """
    if request.method == 'POST':
        servicio_id = request.POST.get('servicio')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        
        # Validamos que el servicio exista
        servicio_obj = get_object_or_404(Servicio, id=servicio_id)
        
        # Creamos la cita en la base de datos
        Cita.objects.create(
            paciente=request.user,
            servicio=servicio_obj,
            fecha=fecha,
            hora=hora,
            estado='PENDIENTE' # Por defecto nace como pendiente
        )
        
        # Recargamos el dashboard para que el usuario vea su nueva cita
        return redirect('dashboard')
        
    # Si alguien intenta entrar por GET, lo mandamos al dashboard
    return redirect('dashboard')