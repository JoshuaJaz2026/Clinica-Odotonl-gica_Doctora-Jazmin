from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError # <--- Necesario para el error de correo duplicado

class RegistroPacienteForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        # Personalizamos las etiquetas para que se vean mejor
        labels = {
            'username': 'Usuario (para iniciar sesión)',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
        }

    # --- VALIDACIÓN DE CORREO ÚNICO ---
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verificamos si existe alguien con ese correo en la base de datos
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado. Intente iniciar sesión.")
        return email

    def __init__(self, *args, **kwargs):
        super(RegistroPacienteForm, self).__init__(*args, **kwargs)
        
        # --- MAGIA DE TAILWIND ---
        # Recorremos todos los campos del formulario y les inyectamos las clases de estilo
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'block w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition duration-200 ease-in-out text-gray-900 sm:text-sm'
            field.widget.attrs['placeholder'] = 'Ingresa tu ' + field.label.lower()
            
            # Opcional: Quitamos los textos de ayuda largos de Django por defecto para limpiar el diseño
            # field.help_text = '' 

        # Personalizamos los placeholders específicos
        self.fields['email'].widget.attrs['placeholder'] = 'ejemplo@correo.com'
        self.fields['username'].widget.attrs['placeholder'] = 'Ej: juanperez99'
        
        # Simplificamos el texto de ayuda de la contraseña
        if 'password1' in self.fields:
             self.fields['password1'].help_text = "Usa al menos 8 caracteres, combina letras y números."