from presentation.observable import Observable
from data.firebase_auth_service import AuthService

class EmpleadoDTO:
    def __init__(self, uid, email, rol):
        self.uid = uid # Es el UID de Auth (y Doc ID)
        self.email = email
        self.rol = rol

class EmpleadosViewModel:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
        self.empleados_lista = Observable([])
        self.mensaje = Observable(None)
        self.error = Observable(None)

    def cargar_empleados(self):
        self.error.value = None
        try:
            lista_raw = self.auth_service.get_all_users_firestore()
            lista_mapeada = []
            
            for item in lista_raw:
                # Usamos doc_id (que ahora es el UID de Auth)
                uid = item.get('doc_id') 
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

    def actualizar_empleado(self, uid: str, rol: str, password: str | None = None):
        self.error.value = None
        self.mensaje.value = None

        if not uid:
            self.error.value = "No se ha seleccionado un empleado (Falta UID)."
            return

        try:
            # Llama al servicio, que ahora accede al documento directamente por UID
            self.auth_service.update_user(uid, rol, password)
            self.mensaje.value = "Empleado actualizado correctamente."
            self.cargar_empleados()
        except Exception as e:
            self.error.value = f"Error al actualizar: {e}"

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
