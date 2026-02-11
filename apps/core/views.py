from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages # <--- Importante para mostrar errores en el HTML
from .models import Servicio, Cita
from .forms import RegistroPacienteForm

# --- IMPORTACIONES PARA EL CORREO ---
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

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
# SISTEMA DE USUARIOS Y CITAS (CON CORREO)
# ---------------------------------------------------------

def registro(request):
    """
    Permite a un nuevo paciente crear su cuenta.
    Valida que el correo no exista (gracias a forms.py).
    """
    if request.method == 'POST':
        form = RegistroPacienteForm(request.POST)
        if form.is_valid():
            # Guardamos el usuario pero sin enviarlo a la BD todavía
            user = form.save(commit=False)
            
            # Aseguramos explícitamente que NO sea Staff (es un paciente)
            user.is_staff = False
            user.save()
            
            # Iniciamos sesión automáticamente
            login(request, user)
            
            # Mensaje de éxito
            messages.success(request, f"¡Bienvenido/a {user.first_name}! Tu cuenta ha sido creada.")
            return redirect('dashboard')
        else:
            # Si hay errores (ej: correo duplicado), los enviamos al template
            messages.error(request, "Hubo un problema con tu registro. Revisa los errores abajo.")
    else:
        form = RegistroPacienteForm()
    
    return render(request, 'registration/registro.html', {'form': form})

@login_required
def dashboard(request):
    """
    Portal privado del paciente. Muestra sus citas reales.
    """
    mis_citas = Cita.objects.filter(paciente=request.user).order_by('fecha', 'hora')
    servicios = Servicio.objects.all()
    
    context = {
        'nombre_paciente': request.user.first_name,
        'citas': mis_citas,
        'servicios': servicios
    }
    return render(request, 'pacientes/dashboard.html', context)

@login_required
def crear_cita(request):
    """
    Procesa el formulario, guarda la cita y ENVÍA EL CORREO HTML.
    """
    if request.method == 'POST':
        servicio_id = request.POST.get('servicio')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        
        # Validar servicio
        servicio_obj = get_object_or_404(Servicio, id=servicio_id)
        
        # 1. Guardar la Cita en BD
        Cita.objects.create(
            paciente=request.user,
            servicio=servicio_obj,
            fecha=fecha,
            hora=hora,
            estado='pendiente' # Asegúrate que coincida con tu modelo (minúsculas/mayúsculas)
        )
        
        # 2. ENVIAR CORREO AUTOMÁTICO
        try:
            asunto = 'Confirmación de Reserva - Clínica Dra. Jazmin'
            
            # Datos para rellenar la plantilla HTML
            contexto_email = {
                'nombre': request.user.first_name,
                'tratamiento': servicio_obj.titulo,
                'fecha': fecha,
                'hora': hora,
            }
            
            # Renderizamos el HTML
            html_message = render_to_string('emails/confirmacion_cita.html', contexto_email)
            plain_message = strip_tags(html_message)
            
            send_mail(
                asunto,
                plain_message,
                settings.EMAIL_HOST_USER,
                [request.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            print("✅ Correo enviado correctamente a:", request.user.email)
            messages.success(request, "¡Cita agendada! Te hemos enviado un correo de confirmación.")
            
        except Exception as e:
            print(f"❌ Error enviando correo: {e}")
            messages.warning(request, "Cita agendada, pero no pudimos enviar el correo de confirmación.")
        
        return redirect('dashboard')
        
    return redirect('dashboard')

# --- VISTA TEMPORAL PARA VER EL DISEÑO DEL CORREO ---
def test_email_design(request):
    # Datos falsos para probar el diseño visual
    contexto_falso = {
        'nombre': 'Joshua (Vista Previa)',
        'tratamiento': 'Ortodoncia Invisible',
        'fecha': '2026-02-14',
        'hora': '15:30',
    }
    # Renderizamos el HTML del correo directamente en el navegador
    return render(request, 'emails/confirmacion_cita.html', contexto_falso)