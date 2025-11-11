import tkinter as tk
from tkinter import ttk

class EmpleadosView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.vm = controller.get_vm("empleados_vm")

        ttk.Label(self, text="Administrar Empleados", font=("Segoe UI", 20, "bold")).pack(pady=10)
        
        f_nav = ttk.Frame(self)
        f_nav.pack(fill="x", padx=10)
        ttk.Button(f_nav, text="< Volver al Menú", 
                   command=lambda: controller.show_frame("HomeView")).pack(side="left")

        # --- Formulario para crear ---
        f_form = ttk.LabelFrame(self, text="Crear Nuevo Empleado", padding=15)
        f_form.pack(pady=20, padx=20)
        
        ttk.Label(f_form, text="Email:").grid(row=0, column=0, sticky="e", padx=5)
        self.email_entry = ttk.Entry(f_form, width=30)
        self.email_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(f_form, text="Contraseña:").grid(row=1, column=0, sticky="e", padx=5)
        self.pass_entry = ttk.Entry(f_form, width=30, show="*")
        self.pass_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(f_form, text="Rol:").grid(row=2, column=0, sticky="e", padx=5)
        self.rol_combo = ttk.Combobox(f_form, values=["mesero", "gerente"], state="readonly")
        self.rol_combo.set("mesero")
        self.rol_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Button(f_form, text="Crear Empleado", command=self.on_crear).grid(row=3, column=0, columnspan=2, pady=15)
        
        self.msg_label = ttk.Label(self, text="")
        self.msg_label.pack(pady=10)

        # Suscribir a Observables
        self.vm.mensaje.subscribe(lambda m: self.update_message(m, "green"))
        self.vm.error.subscribe(lambda e: self.update_message(e, "red"))

    def on_crear(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        rol = self.rol_combo.get()
        self.vm.crear_empleado(email, password, rol)

    def update_message(self, msg, color):
        if msg:
            self.msg_label.config(text=msg, foreground=color)
            if color == "green":
                # Limpiar formulario si fue exitoso
                self.email_entry.delete(0, "end")
                self.pass_entry.delete(0, "end")
        else:
            self.msg_label.config(text="")
            
    def on_show(self):
        # Limpiar mensajes al mostrar
        self.vm.error.value = None
        self.vm.mensaje.value = None