import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class LoginView(tk.Frame):
    def __init__(self, parent, controller):
        # COLOR DE FONDO (Crema suave)
        bg_color = "#FFF8E1" 
        super().__init__(parent, bg=bg_color)
        self.controller = controller
        self.vm = controller.get_vm("login_vm")

        # Configuración para centrar
        self.pack(fill="both", expand=True)
        
        # Frame central (Caja blanca con sombra simulada)
        self.center_frame = tk.Frame(self, bg="white", bd=1, relief="solid")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=520)

        # --- LOGO ---
        self.logo_img = self._cargar_logo()
        tk.Label(self.center_frame, image=self.logo_img, bg="white").pack(pady=(30, 10))

        # Título
        tk.Label(self.center_frame, text="Bienvenido", font=("Segoe UI", 18, "bold"), 
                 bg="white", fg="#333").pack(pady=(0, 20))

        # Inputs
        tk.Label(self.center_frame, text="Correo Electrónico", bg="white", fg="#666", anchor="w").pack(fill="x", padx=30)
        self.ent_email = ttk.Entry(self.center_frame, font=("Segoe UI", 11))
        self.ent_email.pack(fill="x", padx=30, pady=(0, 15))
        # Pre-llenado opcional para pruebas
        # self.ent_email.insert(0, "gerente@test.com")

        tk.Label(self.center_frame, text="Contraseña", bg="white", fg="#666", anchor="w").pack(fill="x", padx=30)
        self.ent_pass = ttk.Entry(self.center_frame, show="•", font=("Segoe UI", 11))
        self.ent_pass.pack(fill="x", padx=30, pady=(0, 20))

        # Botón Login
        self.btn_login = tk.Button(self.center_frame, text="INICIAR SESIÓN", 
                                   bg="#FF9800", fg="white", font=("Segoe UI", 10, "bold"), 
                                   bd=0, cursor="hand2", pady=12,
                                   command=self.handle_login)
        self.btn_login.pack(fill="x", padx=30, pady=10)

        # Mensajes
        self.lbl_msg = tk.Label(self.center_frame, text="", bg="white", fg="red", font=("Segoe UI", 9), wraplength=300)
        self.lbl_msg.pack(pady=5)

        # Suscripciones
        self.vm.error_message.subscribe(lambda msg: self.lbl_msg.config(text=msg, fg="red") if msg else None)
        self.vm.info_message.subscribe(lambda msg: self.lbl_msg.config(text=msg, fg="green") if msg else None)

    def _cargar_logo(self):
        """Carga img/logo.png redimensionado"""
        try:
            if os.path.exists("img/logo.png"):
                img = Image.open("img/logo.png")
                # Logo grande para el login
                img = img.resize((120, 120), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except: pass
        # Placeholder si no hay logo
        return ImageTk.PhotoImage(Image.new('RGB', (120, 120), color="#FFCC80"))

    def handle_login(self):
        self.vm.login(self.ent_email.get(), self.ent_pass.get())