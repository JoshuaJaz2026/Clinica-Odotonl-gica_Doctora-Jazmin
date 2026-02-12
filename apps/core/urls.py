from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- RUTAS PÚBLICAS ---
    path('', views.home, name='home'),
    path('bot-respuesta/', views.bot_respuesta, name='bot_respuesta'),
    
    # --- RUTAS DE USUARIOS ---
    path('registro/', views.registro, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # --- PORTAL DEL PACIENTE ---
    path('mi-portal/', views.dashboard, name='dashboard'),
    
    # --- FUNCIONALIDAD DE CITAS ---
    path('crear-cita/', views.crear_cita, name='crear_cita'),

    # --- RUTA TEMPORAL ---
    path('ver-email/', views.test_email_design, name='test_email'),

    # --- NUEVA RUTA: DESCARGAR PDF ---
    path('receta/pdf/<int:receta_id>/', views.descargar_receta_pdf, name='descargar_receta'),
]