from presentation.observable import Observable
from data.firebase_auth_service import AuthService
from domain.models import Empleado

class LoginViewModel:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
        
        # Observables que la UI escuchará
        self.current_user = Observable(None) # Tipo: Empleado
        self.error_message = Observable(None)
        self.info_message = Observable(None)

    def login(self, email, password):
        self.error_message.value = None
        if not email or not password:
            self.error_message.value = "Email y contraseña son obligatorios."
            return

        try:
            empleado = self.auth_service.login(email, password)
            self.current_user.value = empleado # <-- Esto dispara la navegación
            self.info_message.value = f"Bienvenido {empleado.email}!"
        except Exception as e:
            self.current_user.value = None
            self.error_message.value = str(e)
            
    def logout(self):
        self.current_user.value = None
        self.info_message.value = "Sesión cerrada."