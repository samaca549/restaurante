import os
from dotenv import load_dotenv
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore, auth, db

# Primero calcular BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print("DEBUG BASE_DIR =", BASE_DIR)
print("DEBUG ENV EXISTS =", (BASE_DIR / ".env").exists())
print("DEBUG CREDENTIALS =", os.environ.get("FIREBASE_CREDENTIALS_JSON"))

# Luego cargar el .env desde la raíz
load_dotenv(BASE_DIR / ".env")

def init_firebase():
    if not firebase_admin._apps:
        cred_json_path = os.environ.get("FIREBASE_CREDENTIALS_JSON")
        rtdb_url = os.environ.get("FIREBASE_RTDB_URL")
        
        if not cred_json_path:
            raise ValueError("FIREBASE_CREDENTIALS_JSON no está en .env")
        if not rtdb_url:
            raise ValueError("FIREBASE_RTDB_URL no está en .env")

        try:
            cred = credentials.Certificate(cred_json_path)
            firebase_admin.initialize_app(
                cred,
                {'databaseURL': rtdb_url}
            )
            print(" Firebase Admin inicializado")
        except Exception as e:
            print(" Error cargando credenciales:", e)
            raise e

def get_firebase_clients():
    return firestore.client(), auth
