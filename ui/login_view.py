import tkinter as tk
from tkinter import ttk

class LoginView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.vm = controller.get_vm("login_vm")

        # Layout
        f_main = ttk.Frame(self, padding=20)
        f_main.place(relx=0.5, rely=0.5, anchor="center") # Centrar
        
        ttk.Label(f_main, text="Iniciar Sesión", font=("Segoe UI", 24, "bold")).pack(pady=20)

        ttk.Label(f_main, text="Email:").pack(anchor="w")
        self.email_var = tk.StringVar(value="gerente@test.com")
        self.email_entry = ttk.Entry(f_main, width=40, textvariable=self.email_var)
        self.email_entry.pack(pady=5)

        ttk.Label(f_main, text="Contraseña:").pack(anchor="w")
        self.pass_var = tk.StringVar(value="123456")
        self.pass_entry = ttk.Entry(f_main, width=40, show="*", textvariable=self.pass_var)
        self.pass_entry.pack(pady=5)

        self.login_btn = ttk.Button(f_main, text="Ingresar", command=self.on_login)
        self.login_btn.pack(pady=20, ipadx=10, ipady=5)
        
        self.msg_label = ttk.Label(f_main, text="", font=("Segoe UI", 10))
        self.msg_label.pack()

        # Suscribirnos a los Observables del ViewModel
        self.vm.error_message.subscribe(self.update_message_label)
        self.vm.info_message.subscribe(self.update_message_label)

    def on_login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        self.msg_label.config(text="Iniciando sesión...", foreground="blue")
        self.login_btn.config(state="disabled")
        # Llamamos al ViewModel
        self.vm.login(email, password)
        self.login_btn.config(state="normal")

    def update_message_label(self, message):
        if not message: return
        
        if "Error" in message or "incorrecto" in message:
            self.msg_label.config(text=message, foreground="red")
        else:
            self.msg_label.config(text=message, foreground="green")