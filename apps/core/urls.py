from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('bot-respuesta/', views.bot_respuesta, name='bot_respuesta'),
]