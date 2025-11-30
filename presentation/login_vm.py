from presentation.observable import Observable
from data.firebase_auth_service import AuthService

class EmpleadoObj:
    def __init__(self, uid, email, rol):
        self.uid = uid
        self.email = email
        self.rol = rol

class LoginViewModel:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
        self.current_user = Observable(None)
        self.error_message = Observable(None)
        self.info_message = Observable(None)

    def login(self, email, password):
        self.error_message.value = None
        self.info_message.value = "Verificando..."
        
        if not email or not password:
            self.error_message.value = "Ingrese datos completos."
            return

        try:
            # Llama al servicio que ahora lee Firestore
            user_data = self.auth_service.login(email, password)
            
            usuario_final = EmpleadoObj(
                uid=user_data['uid'],
                email=user_data['email'],
                rol=user_data['rol']
            )
            
            self.info_message.value = f"Bienvenido {usuario_final.rol}"
            self.current_user.value = usuario_final # Esto dispara el cambio de pantalla en la Vista
            
        except Exception as e:
            self.current_user.value = None
            self.error_message.value = str(e)

    def logout(self):
        self.auth_service.logout()
        self.current_user.value = None