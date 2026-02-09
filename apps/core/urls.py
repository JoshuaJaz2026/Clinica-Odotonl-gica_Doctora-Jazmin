from django.urls import path
from django.contrib.auth import views as auth_views # Importante para login/logout
from . import views

urlpatterns = [
    # Tus rutas existentes
    path('', views.home, name='home'),
    path('bot-respuesta/', views.bot_respuesta, name='bot_respuesta'),
    
    # --- NUEVAS RUTAS DE USUARIOS ---
    path('registro/', views.registro, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('mi-portal/', views.dashboard, name='dashboard'),
    path('crear-cita/', views.crear_cita, name='crear_cita'),
]