from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse 
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache # <--- IMPORTANTE: IMPORTAMOS ESTO
from django.contrib import messages
from .models import Servicio, Cita, Receta, Producto 
from .forms import RegistroPacienteForm

# --- IMPORTACIONES PARA EL CORREO ---
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

# --- IMPORTACIONES PARA PDF (REPORTLAB) ---
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# ---------------------------------------------------------
# VISTAS PÚBLICAS
# ---------------------------------------------------------

def home(request):
    servicios = Servicio.objects.all()
    return render(request, 'core/home.html', {'servicios': servicios})

def bot_respuesta(request):
    mensaje = request.GET.get('msg', '').lower()
    respuesta = "Lo siento, no entendí bien. ¿Puedes intentar con las opciones del menú?"
    
    if 'hola' in mensaje or 'buenos' in mensaje:
        respuesta = "¡Hola! Soy el asistente virtual de la Dra. Jazmin. ¿En qué puedo ayudarte hoy?"
    elif 'cita' in mensaje or 'turno' in mensaje or 'agendar' in mensaje:
        respuesta = "¡Claro! Puedes agendar tu cita llenando el formulario que está más arriba en esta página, o registrándote en nuestro portal para gestionarlas mejor."
    elif 'precio' in mensaje or 'costo' in mensaje or 'servicio' in mensaje:
        servicios_db = Servicio.objects.all()[:3]
        texto_servicios = ", ".join([f"{s.titulo} (S/ {s.precio_estimado})" for s in servicios_db])
        if servicios_db:
             respuesta = f"Nuestros precios referenciales son: {texto_servicios}... y más. Puedes ver todos en la sección de Servicios."
        else:
             respuesta = "La consulta básica cuesta S/ 30. Para tratamientos específicos, necesitamos evaluarte."
    elif 'donde' in mensaje or 'ubicacion' in mensaje or 'direccion' in mensaje:
        respuesta = "Estamos en Av. Principal 123, Lima. Justo frente al parque. ¡Es muy fácil llegar!"
    elif 'horario' in mensaje or 'hora' in mensaje:
        respuesta = "Atendemos de Lunes a Viernes de 9am a 8pm, y Sábados hasta las 6pm."
    elif 'entrar' in mensaje or 'login' in mensaje or 'cuenta' in mensaje:
        respuesta = "Puedes acceder a tu cuenta haciendo clic en el botón 'Ingresar' del menú superior."

    return JsonResponse({'respuesta': respuesta})

# ---------------------------------------------------------
# SISTEMA DE USUARIOS Y CITAS
# ---------------------------------------------------------

def registro(request):
    if request.method == 'POST':
        form = RegistroPacienteForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido/a {user.first_name}! Tu cuenta ha sido creada.")
            return redirect('dashboard')
        else:
            messages.error(request, "Hubo un problema con tu registro. Revisa los errores abajo.")
    else:
        form = RegistroPacienteForm()
    return render(request, 'registration/registro.html', {'form': form})

# ---------------------------------------------------------
# PORTAL DEL PACIENTE (PROTEGIDO)
# ---------------------------------------------------------

@never_cache # <--- ESTO EVITA QUE EL BOTÓN 'ATRÁS' MUESTRE LA PÁGINA TRAS LOGOUT
@login_required
def dashboard(request):
    """
    Portal privado del paciente. Muestra citas Y RECETAS.
    """
    mis_citas = Cita.objects.filter(paciente=request.user).order_by('fecha', 'hora')
    mis_recetas = Receta.objects.filter(paciente=request.user).order_by('-fecha_emision')
    
    servicios = Servicio.objects.all()
    
    context = {
        'nombre_paciente': request.user.first_name,
        'citas': mis_citas,
        'recetas': mis_recetas,
        'servicios': servicios
    }
    return render(request, 'pacientes/dashboard.html', context)

@login_required
def crear_cita(request):
    if request.method == 'POST':
        servicio_id = request.POST.get('servicio')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        
        servicio_obj = get_object_or_404(Servicio, id=servicio_id)
        
        Cita.objects.create(
            paciente=request.user,
            servicio=servicio_obj,
            fecha=fecha,
            hora=hora,
            estado='pendiente'
        )
        
        try:
            asunto = 'Confirmación de Reserva - Clínica Dra. Jazmin'
            contexto_email = {
                'nombre': request.user.first_name,
                'tratamiento': servicio_obj.titulo,
                'fecha': fecha,
                'hora': hora,
            }
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
            messages.success(request, "¡Cita agendada! Te hemos enviado un correo de confirmación.")
        except Exception as e:
            print(f"❌ Error enviando correo: {e}")
            messages.warning(request, "Cita agendada, pero no pudimos enviar el correo de confirmación.")
        
        return redirect('dashboard')
    return redirect('dashboard')

def test_email_design(request):
    contexto_falso = {
        'nombre': 'Joshua (Vista Previa)',
        'tratamiento': 'Ortodoncia Invisible',
        'fecha': '2026-02-14',
        'hora': '15:30',
    }
    return render(request, 'emails/confirmacion_cita.html', contexto_falso)

# ---------------------------------------------------------
# NUEVA VISTA: DESCARGAR RECETA PDF (PACIENTE)
# ---------------------------------------------------------
@never_cache # <--- Protegemos también la receta
@login_required
def descargar_receta_pdf(request, receta_id):
    receta = get_object_or_404(Receta, id=receta_id, paciente=request.user)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "CLÍNICA DENTAL DRA. JAZMIN")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, "Av. Principal 123 - Lima, Perú | Tel: 999-999-999")
    p.line(50, height - 80, width - 50, height - 80)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 110, f"PACIENTE: {receta.paciente.first_name} {receta.paciente.last_name}")
    p.setFont("Helvetica", 10)
    p.drawString(400, height - 110, f"FECHA: {receta.fecha_emision.strftime('%d/%m/%Y')}")

    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, height - 150, "DIAGNÓSTICO:")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 165, receta.diagnostico)

    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, height - 200, "INDICACIONES MÉDICAS (RP):")
    
    text_object = p.beginText(50, height - 220)
    text_object.setFont("Helvetica", 10)
    lines = receta.medicamentos.split('\n')
    for line in lines:
        text_object.textLine(line)
    p.drawText(text_object)

    p.line(50, 150, 250, 150)
    p.setFont("Helvetica", 9)
    p.drawString(80, 135, "Firma Dra. Jazmín")
    p.drawString(50, 50, "Documento generado digitalmente desde el Portal del Paciente.")
    
    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

# ---------------------------------------------------------
# TIENDA Y PAGOS 🛒
# ---------------------------------------------------------

@never_cache # <--- Protegemos la tienda
@login_required
def tienda(request):
    """ Muestra los productos disponibles """
    productos = Producto.objects.filter(stock__gt=0) # Solo los que tienen stock
    return render(request, 'pacientes/tienda.html', {'productos': productos})

@login_required
def pagar_cita(request, cita_id):
    """ Simulación de Pasarela de Pago para Citas """
    cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
    
    # Redirigimos a WhatsApp para confirmar el Yape/Plin
    telefono_clinica = "51999999999" # Pon el número real
    mensaje = f"Hola, soy {request.user.first_name}. Quiero pagar mi cita de {cita.servicio.titulo} (S/ {cita.servicio.precio_estimado}) programada para el {cita.fecha}."
    
    url_whatsapp = f"https://wa.me/{telefono_clinica}?text={mensaje}"
    return redirect(url_whatsapp)