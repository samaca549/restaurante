import tkinter as tk
from data.firebase_config import init_firebase, get_firebase_clients
from data.gemini_service import GeminiService
from data.firestore_service import FirestoreService
from data.firebase_auth_service import AuthService
from ui.app_ui import AppUI

# Importación de ViewModels
from presentation.login_vm import LoginViewModel
from presentation.finanzas_vm import FinanzasViewModel
from presentation.pedidos_vm import PedidosViewModel
from presentation.inventario_vm import InventarioViewModel
from presentation.empleados_vm import EmpleadosViewModel
from presentation.historial_vm import HistorialPedidosViewModel

def main():
    # --- 1. Inicialización de Servicios ---
    try:
        init_firebase()
    except Exception as e:
        print(f"Error fatal al inicializar Firebase: {e}")
        return

    # Obtener clientes ya autenticados
    db_firestore_client, auth_admin_client = get_firebase_clients()

    # Inicializar servicios base
    firestore_service = FirestoreService(db_firestore_client, auth_admin_client)
    
    # --- CORRECCIÓN AQUÍ: Pasamos AMBOS clientes ---
    auth_service = AuthService( db_firestore_client)
    
    # Inicializar servicio de IA
    ia_service = GeminiService(firestore_service) 

    # --- 2. Inicialización de ViewModels ---
    
    login_vm = LoginViewModel(auth_service)
    
    finanzas_vm = FinanzasViewModel(
        firestore_service=firestore_service, 
        gemini_service=ia_service
    )
    
    historial_vm = HistorialPedidosViewModel(firestore_service)
    
    pedidos_vm = PedidosViewModel(firestore_service, ia_service)
    
    inventario_vm = InventarioViewModel(firestore_service, ia_service)
    
    empleados_vm = EmpleadosViewModel(auth_service)

    # Bundle de ViewModels
    vm_bundle = {
        "login_vm": login_vm,
        "finanzas_vm": finanzas_vm,
        "pedidos_vm": pedidos_vm,
        "inventario_vm": inventario_vm,
        "empleados_vm": empleados_vm,
        "historial_vm": historial_vm 
    }
    
    # --- 3. Ejecución de la UI ---
    app = AppUI(vm_bundle=vm_bundle)
    app.mainloop()

if __name__ == "__main__":
    main()