import requests
import json
import os
from firebase_admin import auth, firestore
from dotenv import load_dotenv

load_dotenv()
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")

class AuthService:
    def __init__(self, db_firestore_client):
        self.db = db_firestore_client
        self.current_user = None 

    def login(self, email, password):
        if not FIREBASE_WEB_API_KEY:
            raise Exception("Falta FIREBASE_WEB_API_KEY en .env")

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

            local_id = data["localId"]
            id_token = data["idToken"]

            # 2. OBTENER ROL DESDE FIRESTORE (Buscamos por email, no por UID aquí)
            rol = 'mesero'
            if self.db:
                users_ref = self.db.collection('empleados')
                query = users_ref.where('email', '==', email).limit(1).stream()
                
                encontrado = False
                for doc in query:
                    user_data = doc.to_dict()
                    rol = user_data.get('rol', 'mesero')
                    encontrado = True
            
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

    def create_user(self, email, password, rol):
        """Crea en Auth y guarda en Firestore usando el UID de Auth como ID del documento."""
        try:
            # 1. Crear en Auth
            user = auth.create_user(email=email, password=password)
            
            # 2. Guardar en Firestore (usando el UID de Auth como ID del Documento)
            if self.db:
                self.db.collection('empleados').document(user.uid).set({ # <-- SET usando user.uid como ID
                    'email': email,
                    'rol': rol,
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
            # Asumimos que el doc.id es el UID de Auth
            data['doc_id'] = doc.id 
            data['uid_auth'] = doc.id 
            lista.append(data)
        return lista
        # En data/firebase_auth_service.py, dentro de la clase AuthService:

    
    def delete_user(self, uid: str):
        """Elimina el usuario de Auth Y su documento en Firestore."""
        try:
            # 1. Eliminar de Auth
            auth.delete_user(uid)
            
            # 2. Eliminar de Firestore (Directamente por ID)
            if self.db:
                self.db.collection('empleados').document(uid).delete()
                print(f"DEBUG: Documento eliminado en Firestore: {uid}")
        except Exception as e:
            raise Exception(f"Error eliminando usuario: {e}")
  

    def update_user(self, uid: str, rol: str, password: str | None = None):
      
        print(f"DEBUG: Solicitud de update recibida. Password es: '{password}' (Tipo: {type(password)})")

        # 1. Actualizar contraseña en Auth
       
        if password is not None and len(str(password).strip()) > 0:
            print(f"DEBUG: Intentando cambiar contraseña a: {password}")
            try:
                auth.update_user(uid, password=password)
                print(f"DEBUG:  Contraseña actualizada correctamente en Auth para {uid}")
            except Exception as auth_e:
                print(f"DEBUG:  Error al cambiar contraseña: {auth_e}")
               
        else:
            print("DEBUG:  Se omitió el cambio de contraseña (el campo estaba vacío o es None).")

        # 2. Actualizar Rol en Firestore
        if self.db:
            try:
                doc_ref = self.db.collection('empleados').document(uid)
                doc_ref.update({'rol': rol})
                print(f"DEBUG: ¡Éxito! Rol actualizado a {rol} para el documento {uid}")
            except Exception as e:
                raise Exception(f"Error actualizando rol en Firestore: {e}")
