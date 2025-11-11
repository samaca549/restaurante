import tkinter as tk
from tkinter import ttk
from typing import Dict

# Importamos todas las vistas (Frames)
from ui.login_view import LoginView
from ui.home_view import HomeView
from ui.pedidos_view import PedidosView
from ui.inventario_view import InventarioView
from ui.empleados_view import EmpleadosView
from ui.finanzas_view import FinanzasView
from ui.historial_view import HistorialPedidosView
# (Puedes añadir una vista de IA si quieres)

class AppUI(tk.Tk):
    """
    Ventana principal de Tkinter.
    Actúa como el "Controlador" que maneja el cambio de vistas (frames).
    """
    def __init__(self, vm_bundle: Dict):
        super().__init__()
        self.title("Sistema de Restaurante")
        self.geometry("1024x768")
        
        self.vm_bundle = vm_bundle
        
        # Contenedor principal
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Vistas a cargar
        vistas = (LoginView, HomeView, PedidosView, InventarioView, EmpleadosView, FinanzasView, HistorialPedidosView)

        for F in vistas:
            frame_name = F.__name__
            # Creamos la instancia de la vista (Frame)
            frame = F(container, self) # 'self' es el controlador
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Suscribirnos al login_vm para navegar
        login_vm = self.get_vm("login_vm")
        login_vm.current_user.subscribe(self.on_auth_change)
        
        self.show_frame("LoginView")

    def show_frame(self, frame_name: str):
        """Muestra un frame por su nombre."""
        print(f"Navegando a: {frame_name}")
        frame = self.frames[frame_name]
        
        # Si el frame tiene un método 'on_show', lo llamamos
        # (útil para recargar datos cuando se muestra la vista)
        if hasattr(frame, 'on_show'):
            frame.on_show()
            
        frame.tkraise()

    def get_vm(self, vm_name: str):
        """Permite a las vistas obtener su ViewModel."""
        vm = self.vm_bundle.get(vm_name)
        if not vm:
            raise ValueError(f"ViewModel '{vm_name}' no encontrado.")
        return vm
        
    def get_current_user_role(self) -> str:
        """Helper para saber el rol del usuario logueado."""
        user = self.get_vm("login_vm").current_user.value
        return user.rol if user else "None"

    def on_auth_change(self, user):
        """
        Escucha el Observable 'current_user' del LoginViewModel.
        Navega a Home si hay usuario, o a Login si no.
        """
        if user:
            self.show_frame("HomeView")
        else:
            self.show_frame("LoginView")