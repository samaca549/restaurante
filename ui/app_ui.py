import tkinter as tk
from tkinter import ttk
from typing import Dict

# Importamos todas las vistas
from ui.login_view import LoginView
from ui.home_view import HomeView
from ui.pedidos_view import PedidosView
from ui.inventario_view import InventarioView
from ui.empleados_view import EmpleadosView
from ui.finanzas_view import FinanzasView
from ui.historial_view import HistorialPedidosView

class AppUI(tk.Tk):
    def __init__(self, vm_bundle: Dict, ia_service=None): # <--- AÑADIDO ia_service
        super().__init__()
        self.title("Sistema de Restaurante")
        self.geometry("1024x768")
        
        self.vm_bundle = vm_bundle
        
        # --- AQUÍ GUARDAMOS EL SERVICIO PARA QUE LAS VISTAS LO USEN ---
        self.ia_service = ia_service 
        # --------------------------------------------------------------

        self.current_frame_name = None 

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        vistas = (LoginView, HomeView, PedidosView, InventarioView, EmpleadosView, FinanzasView, HistorialPedidosView)

        for F in vistas:
            frame_name = F.__name__
            try:
                # Creamos la instancia de la vista
                frame = F(container, self) # 'self' lleva ahora self.ia_service dentro
                self.frames[frame_name] = frame
                frame.grid(row=0, column=0, sticky="nsew")
            except Exception as e:
                print(f"Error al cargar la vista {frame_name}: {e}")

        login_vm = self.get_vm("login_vm")
        login_vm.current_user.subscribe(self.on_auth_change)
        
        if self.current_frame_name is None:
            self.show_frame("LoginView")

    def show_frame(self, frame_name: str):
        if self.current_frame_name == frame_name:
            return 

        # print(f"Navegando a: {frame_name}") # Debug opcional
        
        if frame_name not in self.frames:
            print(f"ERROR: La vista {frame_name} no existe.")
            return

        frame = self.frames[frame_name]
        
        if hasattr(frame, 'on_show'):
            try:
                frame.on_show()
            except Exception as e:
                print(f"Error en on_show de {frame_name}: {e}")
            
        frame.tkraise()
        self.current_frame_name = frame_name

    def get_vm(self, vm_name: str):
        vm = self.vm_bundle.get(vm_name)
        if not vm:
            raise ValueError(f"ViewModel '{vm_name}' no encontrado.")
        return vm
        
    def get_current_user_role(self) -> str:
        user_observable = self.get_vm("login_vm").current_user
        user = user_observable.value
        if user:
            if isinstance(user, dict):
                return user.get('rol', 'None')
            return getattr(user, 'rol', 'None')
        return "None"

    def on_auth_change(self, user):
        if user:
            self.show_frame("HomeView")
        else:
            self.show_frame("LoginView")