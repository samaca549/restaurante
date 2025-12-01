import tkinter as tk
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv
import os

# Servicios
from data.firebase_auth_service import AuthService
from data.firestore_service import FirestoreService
from data.gemini_service import GeminiService

# ViewModels
from presentation.login_vm import LoginViewModel
from presentation.pedidos_vm import PedidosViewModel
from presentation.inventario_vm import InventarioViewModel
from presentation.empleados_vm import EmpleadosViewModel
from presentation.finanzas_vm import FinanzasViewModel
from presentation.historial_vm import HistorialPedidosViewModel

# UI Principal
from ui.app_ui import AppUI

def main():
    # Cargar variables de entorno (.env) para la API KEY de Gemini
    load_dotenv()

    # --- A. INICIALIZAR FIREBASE ---
    if not firebase_admin._apps:
        try:
            # Busca el archivo de credenciales
            if os.path.exists("serviceAccountKey.json"):
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            else:
                print("ERROR CRÍTICO: No se encontró 'serviceAccountKey.json'.")
                return
        except Exception as e:
            print(f"Error iniciando Firebase: {e}")
            return

    # Cliente de Base de Datos (Firestore)
    db = firestore.client()
    
    # Cliente de Autenticación (Auth)
    # Lo obtenemos del módulo para pasarlo al servicio
    auth_client = auth

    # --- B. INICIALIZAR SERVICIOS (INYECTAR DEPENDENCIAS) ---
    
    # 1. Autenticación (Para Login)
    auth_service = AuthService(db_firestore_client=db)
    
    # 2. Datos (Firestore)
    # IMPORTANTE: Aquí pasamos (db, auth_client) como pide tu código actualizado
    firestore_service = FirestoreService(firestore_client=db, auth_client=auth_client)
    
    # 3. Inteligencia Artificial (Gemini)
    # Le pasamos firestore_service para que pueda leer el historial
    ia_service = GeminiService(firestore_service)

    # --- C. INICIALIZAR VIEWMODELS (BUNDLE) ---
    # Creamos el paquete de lógica que usará la interfaz
    vm_bundle = {
        "login_vm": LoginViewModel(auth_service),
        
        # Pedidos: Usa Firestore para guardar y IA para recomendar
        "pedidos_vm": PedidosViewModel(firestore_service, ia_service),
        
        # Inventario: Usa Firestore para stock e IA para análisis
        "inventario_vm": InventarioViewModel(firestore_service, ia_service), 
        
        "empleados_vm": EmpleadosViewModel(auth_service),
        
        # Finanzas: Usa Firestore para historial e IA para análisis financiero potente
        "finanzas_vm": FinanzasViewModel(firestore_service, ia_service),
        
        "historial_vm": HistorialPedidosViewModel(firestore_service)
    }

    # --- D. ARRANCAR APLICACIÓN ---
    print("Sistema iniciado correctamente. Abriendo ventana...")
    
    # Inicializamos la ventana principal pasando los ViewModels y el servicio de IA
    app = AppUI(vm_bundle=vm_bundle, ia_service=ia_service)
    
    # Bloqueo principal de la interfaz gráfica
    app.mainloop()

if __name__ == "__main__":
    main()