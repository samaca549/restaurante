import requests
import json
import os
from firebase_admin import auth, firestore
from dotenv import load_dotenv

load_dotenv()
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")

class AuthService:
    def __init__(self, db_firestore_client):
        """
        Recibe el cliente de Firestore para leer/escribir roles.
        """
        self.db = db_firestore_client
        self.current_user = None 

    def login(self, email, password):
        if not FIREBASE_WEB_API_KEY:
            raise Exception("Falta FIREBASE_WEB_API_KEY en .env")

        # 1. Validar contraseña con Google
        request_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {"email": email, "password": password, "returnSecureToken": True}

        try:
            response = requests.post(request_url, headers=headers, data=json.dumps(payload))
            data = response.json()

            if "error" in data:
                msg = data["error"]["message"]
                if "INVALID_PASSWORD" in msg or "EMAIL_NOT_FOUND" in msg:
                    raise Exception("Credenciales incorrectas.")
                raise Exception(f"Error login: {msg}")

            # Datos básicos
            local_id = data["localId"] # UID de Auth
            id_token = data["idToken"]

            # 2. OBTENER ROL DESDE FIRESTORE 
            rol = 'mesero' # Default
            
            if self.db:
                print(f"DEBUG: Buscando en Firestore email: {email}")
         
                users_ref = self.db.collection('empleados')
                query = users_ref.where('email', '==', email).limit(1).stream()
                
                encontrado = False
                for doc in query:
                    user_data = doc.to_dict()
                    rol = user_data.get('rol', 'mesero')
                    print(f"DEBUG: ¡Encontrado! Rol en BD es: {rol}")
                    encontrado = True
                
                if not encontrado:
                    print("DEBUG: Usuario autenticado, pero no existe en la colección 'empleados'.")
            
            # 3. Guardar sesión en memoria
            self.current_user = {
                "uid": local_id,
                "email": email,
                "rol": rol,
                "token": id_token
            }
            return self.current_user

        except Exception as e:
            raise e

    def logout(self):
        self.current_user = None

    # --- GESTIÓN DE EMPLEADOS (CRUD) ---

    def create_user(self, email, password, rol):
        """Crea en Auth (Login) Y guarda en Firestore para que el login funcione."""
        try:
            # 1. Crear en Auth (para autenticación)
            user = auth.create_user(email=email, password=password)
            
            # 2. Guardar en Firestore (Datos y Rol)
            if self.db:
                self.db.collection('empleados').add({
                    'email': email,
                    'rol': rol,
                    'uid_auth': user.uid # Guardamos referencia al UID de Auth
                })
            
            return user
        except Exception as e:
            raise Exception(f"Error creando usuario: {e}")

    def get_all_users_firestore(self):
        """Trae la lista desde Firestore (donde están los roles)."""
        if not self.db: return []
        
        lista = []
        docs = self.db.collection('empleados').stream()
        for doc in docs:
            data = doc.to_dict()
            # Añadimos el ID del documento por si necesitamos editar/borrar
            data['doc_id'] = doc.id 
            lista.append(data)
        return lista

    def delete_user(self, uid: str):
        """Elimina el usuario de Auth Y su documento en Firestore."""
        try:
            # 1. Eliminar de Auth (si uid es el UID de Auth)
            auth.delete_user(uid)
            
            # 2. Eliminar de Firestore (buscando por 'uid_auth' == uid)
            if self.db:
                users_ref = self.db.collection('empleados')
                query = users_ref.where('uid_auth', '==', uid).limit(1).stream()
                
                for doc in query:
                    doc.reference.delete()
                    print(f"DEBUG: Documento eliminado en Firestore: {doc.id}")
                    return  # Salimos si encontramos y eliminamos
                
                print("DEBUG: No se encontró documento en Firestore para eliminar.")
            
        except Exception as e:
            raise Exception(f"Error eliminando usuario: {e}")
