from presentation.observable import Observable
from data.firebase_auth_service import AuthService

class EmpleadosViewModel:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
        self.mensaje = Observable(None)
        self.error = Observable(None)

    def crear_empleado(self, email, password, rol):
        self.error.value = None
        self.mensaje.value = None
        if not email or not password or not rol:
            self.error.value = "Email, password y rol son obligatorios."
            return
        if rol not in ["gerente", "mesero"]:
            self.error.value = "Rol debe ser 'gerente' o 'mesero'."
            return
            
        try:
            empleado = self.auth_service.create_user(email, password, rol)
            self.mensaje.value = f"Empleado {empleado.email} (rol: {rol}) creado con éxito."
        except Exception as e:
            self.error.value = f"Error al crear empleado: {e}"