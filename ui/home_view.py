import tkinter as tk
from tkinter import ttk

class HomeView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        f_main = ttk.Frame(self)
        f_main.pack(expand=True)

        self.lbl_title = ttk.Label(f_main, text="Menú Principal", font=("Segoe UI", 24, "bold"))
        self.lbl_title.pack(pady=20)
        
        self.lbl_welcome = ttk.Label(f_main, text="", font=("Segoe UI", 12))
        self.lbl_welcome.pack(pady=5)

        btn_style = {"pady": 10, "ipadx": 30, "ipady": 10}

        ttk.Button(f_main, text="Tomar Pedido", 
                   command=lambda: controller.show_frame("PedidosView")).pack(**btn_style)
        
        ttk.Button(f_main, text="Ver Inventario", 
                   command=lambda: controller.show_frame("InventarioView")).pack(**btn_style)
        ttk.Button(f_main, text="Ver Finanzas", 
                   command=lambda: controller.show_frame("FinanzasView")).pack(**btn_style)
        ttk.Button(f_main, text="Ver Historial_pedidos", 
                   command=lambda: controller.show_frame("HistorialPedidosView")).pack(**btn_style)
        
        # Este botón es solo para gerentes
        self.btn_admin = ttk.Button(f_main, text="Administrar Empleados", 
                                    command=lambda: controller.show_frame("EmpleadosView"))
        self.btn_admin.pack(**btn_style)
        
        ttk.Button(f_main, text="Cerrar Sesión", 
                   command=self.on_logout).pack(pady=40)

    def on_show(self):
        """Se llama cada vez que la vista se muestra."""
        rol = self.controller.get_current_user_role()
        email = self.controller.get_vm("login_vm").current_user.value.email
        self.lbl_welcome.config(text=f"Usuario: {email} (Rol: {rol})")
        
        # Ocultamos el botón de admin si no es gerente
        if rol == 'gerente':
            self.btn_admin.pack(pady=10, ipadx=30, ipady=10)
        else:
            self.btn_admin.pack_forget()

    def on_logout(self):
        login_vm = self.controller.get_vm("login_vm")
        login_vm.logout()