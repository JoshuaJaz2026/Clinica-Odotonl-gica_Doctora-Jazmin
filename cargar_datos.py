import os
import django
from datetime import date, time, timedelta

# 1. Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# 2. Importar tus modelos
from django.contrib.auth.models import User
from apps.core.models import Servicio, Producto, Cita, Insumo

def run():
    print("🚀 Iniciando carga de datos masiva...")

    # --- A. CREANDO SERVICIOS (ESPECIALIDADES) ---
    servicios_data = [
        {"titulo": "Ortodoncia (Brackets)", "desc": "Corrección de la alineación de los dientes y mordida.", "precio": 150.00},
        {"titulo": "Endodoncia", "desc": "Tratamiento de conducto para salvar piezas dentales dañadas.", "precio": 300.00},
        {"titulo": "Profilaxis (Limpieza)", "desc": "Limpieza profunda con ultrasonido y flúor.", "precio": 50.00},
        {"titulo": "Blanqueamiento LED", "desc": "Aclara tus dientes hasta 3 tonos en una sesión.", "precio": 250.00},
        {"titulo": "Curación con Resina", "desc": "Restauración estética de caries con material 3M.", "precio": 70.00},
        {"titulo": "Odontopediatría", "desc": "Atención especializada y amigable para niños.", "precio": 60.00},
    ]

    for s in servicios_data:
        obj, created = Servicio.objects.get_or_create(
            titulo=s['titulo'],
            defaults={'descripcion': s['desc'], 'precio_estimado': s['precio']}
        )
        if created: print(f"   ✅ Servicio creado: {s['titulo']}")

    # --- B. CREANDO PRODUCTOS (TIENDA) ---
    productos_data = [
        {"nombre": "Cepillo Vitis Orthodontic", "precio": 18.50, "stock": 20},
        {"nombre": "Pasta Dental Sensodyne", "precio": 22.00, "stock": 15},
        {"nombre": "Hilo Dental Oral-B", "precio": 12.00, "stock": 30},
        {"nombre": "Cera para Brackets", "precio": 8.00, "stock": 50},
        {"nombre": "Enjuague Colgate Plax", "precio": 15.00, "stock": 10},
        {"nombre": "Cepillo Interproximal", "precio": 25.00, "stock": 12},
    ]

    for p in productos_data:
        obj, created = Producto.objects.get_or_create(
            nombre=p['nombre'],
            defaults={'descripcion': 'Producto recomendado por especialistas.', 'precio': p['precio'], 'stock': p['stock']}
        )
        if created: print(f"   ✅ Producto creado: {p['nombre']}")

    # --- C. CREANDO PACIENTE DE PRUEBA ---
    # Creamos un usuario para que puedas loguearte y probar
    usuario = "paciente_prueba"
    clave = "123456"
    
    user, created = User.objects.get_or_create(
        username=usuario,
        defaults={
            'first_name': 'Juan', 
            'last_name': 'Perez (Test)', 
            'email': 'juan@test.com',
            'is_staff': False
        }
    )
    if created:
        user.set_password(clave)
        user.save()
        print(f"   👤 Usuario creado: {usuario} (Clave: {clave})")
    else:
        print(f"   👤 Usuario {usuario} ya existía.")

    # --- D. CREANDO CITAS DE PRUEBA ---
    servicio_orto = Servicio.objects.get(titulo="Ortodoncia (Brackets)")
    servicio_limp = Servicio.objects.get(titulo="Profilaxis (Limpieza)")

    # Cita 1: Mañana a las 10am
    Cita.objects.get_or_create(
        paciente=user,
        fecha=date.today() + timedelta(days=1),
        hora=time(10, 0),
        defaults={'servicio': servicio_orto, 'estado': 'confirmada'}
    )
    
    # Cita 2: Pasado mañana a las 4pm
    Cita.objects.get_or_create(
        paciente=user,
        fecha=date.today() + timedelta(days=2),
        hora=time(16, 0),
        defaults={'servicio': servicio_limp, 'estado': 'pendiente'}
    )
    print("   ✅ Citas de prueba agendadas.")

    print("\n🎉 ¡CARGA COMPLETA! Ahora tu sistema tiene datos reales.")

if __name__ == '__main__':
    run()