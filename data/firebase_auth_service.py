import os
import requests
import json
from domain.models import Empleado
from firebase_admin import firestore

class AuthService:
    """
    Maneja el login (REST API) y la creación de usuarios (Admin SDK).
    Ya no requiere db_client en el constructor.
    """
    def __init__(self, auth_admin_client):
        self.auth_admin = auth_admin_client
        
        # Firestore desde firebase_admin
        self.db = firestore.client()
        self.users_col = self.db.collection("empleados")
        
        # WEB API KEY
        self.web_api_key = os.environ.get("FIREBASE_WEB_API_KEY")
        if not self.web_api_key:
            raise ValueError("FIREBASE_WEB_API_KEY no encontrada en .env")

        # Opcionales pero recomendables
        self.auth_domain = os.environ.get("FIREBASE_AUTH_DOMAIN")
        self.project_id = os.environ.get("FIREBASE_PROJECT_ID")

        self.rest_api_url = (
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.web_api_key}"
        )

    def login(self, email, password) -> Empleado:
        payload = json.dumps({
            "email": email,
            "password": password,
            "returnSecureToken": True
        })

        origin_header = (
            f"https://{self.auth_domain}" if self.auth_domain else "http://localhost"
        )

        headers = {
            "Content-Type": "application/json",
            "Referer": origin_header,
        }

        try:
            print(f"Autenticando {email} vía REST API...")
            response = requests.post(self.rest_api_url, data=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            uid = data["localId"]
            print(f"Login REST exitoso. UID: {uid}. Consultando rol...")

            empleado_data = self.get_empleado_doc(uid)
            if empleado_data:
                return Empleado.from_dict(empleado_data, uid)
            raise Exception(f"Usuario {uid} sin rol en Firestore")

        except requests.exceptions.HTTPError as err:
            error_json = err.response.json()
            error_msg = error_json.get("error", {}).get("message", "Error desconocido")
            raise Exception(f"Error de login: {error_msg}")
        except Exception as e:
            raise e

    def get_empleado_doc(self, uid: str) -> dict:
        print(f"Consultando Firestore UID: {uid} en 'empleados'...")
        try:
            doc = self.users_col.document(uid).get()
            if doc.exists:
                print("Rol encontrado:", doc.to_dict().get("rol"))
                return doc.to_dict()
            print("Documento NO encontrado")
            return None
        except Exception as e:
            print("Error consultando Firestore:", e)
            return None

    def create_user(self, email, password, rol) -> Empleado:
        try:
            print(f"Creando usuario {email} (rol {rol})...")
            user_record = self.auth_admin.create_user(
                email=email,
                password=password
            )
            uid = user_record.uid
            print(f"Usuario creado UID={uid}. Guardando rol en Firestore...")

            empleado = Empleado(uid=uid, email=email, rol=rol)
            self.users_col.document(uid).set(empleado.to_dict())

            return empleado
        except Exception as e:
            print("Error al crear usuario:", e)
            raise e
