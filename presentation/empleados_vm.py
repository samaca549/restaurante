from presentation.observable import Observable
from data.firebase_auth_service import AuthService

class EmpleadoDTO:
    def __init__(self, uid, email, rol):
        self.uid = uid # Puede ser uid de Auth o ID del documento
        self.email = email
        self.rol = rol

class EmpleadosViewModel:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
        self.empleados_lista = Observable([])
        self.mensaje = Observable(None)
        self.error = Observable(None)

    def cargar_empleados(self):
        """Carga desde Firestore para ver los roles correctos."""
        self.error.value = None
        try:
            # Usamos el nuevo método que lee la colección
            lista_raw = self.auth_service.get_all_users_firestore()
            lista_mapeada = []
            
            for item in lista_raw:
                # Ojo: item es un diccionario ahora
                uid = item.get('uid_auth') or item.get('doc_id')
                email = item.get('email', 'Sin email')
                rol = item.get('rol', 'mesero')
                
                lista_mapeada.append(EmpleadoDTO(uid, email, rol))
            
            self.empleados_lista.value = lista_mapeada
            
        except Exception as e:
            self.error.value = f"Error cargando: {e}"

    def crear_empleado(self, email, password, rol):
        self.error.value = None
        self.mensaje.value = None
        
        if not email or not password or not rol:
            self.error.value = "Datos incompletos."
            return
            
        try:
            self.auth_service.create_user(email, password, rol)
            self.mensaje.value = "Empleado creado y guardado en BD."
            self.cargar_empleados()
        except Exception as e:
            self.error.value = f"Error: {e}"

    def eliminar_empleado(self, uid: str):
        self.error.value = None
        self.mensaje.value = None
        
        if not uid:
            self.error.value = "UID requerido para eliminar."
            return
            
        try:
            self.auth_service.delete_user(uid)
            self.mensaje.value = "Empleado eliminado correctamente."
            self.cargar_empleados()
        except Exception as e:
            self.error.value = f"Error al eliminar: {e}"