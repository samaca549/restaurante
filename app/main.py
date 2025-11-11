import tkinter as tk
from data.firebase_config import init_firebase, get_firebase_clients
from data.gemini_service import GeminiService
from data.firestore_service import FirestoreService
from data.firebase_auth_service import AuthService
from ui.app_ui import AppUI
from presentation.observable import Observable # Necesario para los VMs

# Importación de ViewModels (Asegúrate que estas rutas existan)
from presentation.login_vm import LoginViewModel
from presentation.finanzas_vm import FinanzasViewModel
from presentation.pedidos_vm import PedidosViewModel
from presentation.inventario_vm import InventarioViewModel
from presentation.empleados_vm import EmpleadosViewModel


def main():
    # --- 1. Inicialización de Servicios ---
    
    # Inicializa Firebase Admin SDK (para acceder a la DB y Auth)
    try:
        init_firebase()
    except Exception as e:
        # Esto ocurre si falta el .env o las credenciales son incorrectas
        print(f"Error fatal al inicializar Firebase: {e}")
        return

    # Obtener clientes de Firebase (dummy o reales)
    db_firestore_client, auth_admin_client = get_firebase_clients()

    # Inicializar servicios base
    firestore_service = FirestoreService(db_firestore_client, auth_admin_client)
    auth_service = AuthService(auth_admin_client)
    
    # Inicializar servicio de IA
    gemini_service = GeminiService(firestore_service)
    ia_service = gemini_service # Alias

    # --- 2. Inicialización de ViewModels ---
    
    # Inicialización con dependencias:
    login_vm = LoginViewModel(auth_service)
    
    # 🚨 FIX PRINCIPAL: FinanzasViewModel ahora recibe sus dos dependencias: Firestore y Gemini (ia_service)
    finanzas_vm = FinanzasViewModel(
        firestore_service=firestore_service, 
        gemini_service=ia_service
    )
    
    pedidos_vm = PedidosViewModel(firestore_service, ia_service)
    inventario_vm = InventarioViewModel(firestore_service)
    empleados_vm = EmpleadosViewModel(auth_service)

    # Agrupar todos los ViewModels en un bundle
    vm_bundle = {
        "login_vm": login_vm,
        "finanzas_vm": finanzas_vm, # Se usa la variable finanzas_vm inicializada arriba
        "pedidos_vm": pedidos_vm,
        "inventario_vm": inventario_vm,
        "empleados_vm": empleados_vm,
    }
    
    # --- 3. Inicialización y Ejecución de la UI ---
    app = AppUI(vm_bundle=vm_bundle)
    app.mainloop()

if __name__ == "__main__":
    main()