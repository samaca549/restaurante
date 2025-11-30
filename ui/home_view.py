import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class HomeView(tk.Frame):
    def __init__(self, parent, controller):
        # COLOR DE FONDO (Crema suave)
        bg_color = "#FFF8E1" 
        super().__init__(parent, bg=bg_color)
        self.controller = controller

        # --- HEADER CON LOGO PEQUEÑO ---
        f_header = tk.Frame(self, bg="white", height=80, bd=1, relief="solid")
        f_header.pack(fill="x", side="top")
        f_header.pack_propagate(False)

        # Logo pequeño a la izquierda
        self.logo_small = self._cargar_logo_small()
        tk.Label(f_header, image=self.logo_small, bg="white").pack(side="left", padx=20)

        # Título y Rol
        f_titles = tk.Frame(f_header, bg="white")
        f_titles.pack(side="left", fill="y", pady=10)
        tk.Label(f_titles, text="SISTEMA RESTAURANTE", font=("Segoe UI", 14, "bold"), bg="white", fg="#EF6C00").pack(anchor="w")
        self.lbl_rol = tk.Label(f_titles, text="Cargando...", font=("Segoe UI", 10), bg="white", fg="#757575")
        self.lbl_rol.pack(anchor="w")

        # Botón Cerrar Sesión
        tk.Button(f_header, text="Cerrar Sesión", command=self.logout, 
                  bg="#ef5350", fg="white", bd=0, padx=15, font=("Segoe UI", 9, "bold")).pack(side="right", padx=20, pady=20)

        # --- GRID DE MENÚ (BOTONES) ---
        self.container_menu = tk.Frame(self, bg=bg_color)
        self.container_menu.pack(expand=True, fill="both", padx=50, pady=30)
        
        # Configurar grid (3 columnas)
        for i in range(3): self.container_menu.columnconfigure(i, weight=1)

    def _cargar_logo_small(self):
        try:
            if os.path.exists("img/logo.png"):
                img = Image.open("img/logo.png")
                # Logo pequeño para el header
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except: pass
        return ImageTk.PhotoImage(Image.new('RGB', (50, 50), color="#FFCC80"))

    def on_show(self):
        # Actualizar Rol y Botones según el usuario
        rol = self.controller.get_current_user_role()
        self.lbl_rol.config(text=f"Rol: {rol.upper()}")
        self.crear_botones(rol)

    def crear_botones(self, rol):
        # Limpiar botones anteriores
        for widget in self.container_menu.winfo_children(): widget.destroy()

        botones = []
        
        # --- BOTONES PARA TODOS (Mesero y Gerente) ---
        botones.append(("Nuevo Pedido", "PedidosView", "#4CAF50", "🍔"))
        botones.append(("Inventario", "InventarioView", "#2196F3", "📦"))
        botones.append(("Historial", "HistorialPedidosView", "#607D8B", "📜"))

        # --- BOTONES SOLO PARA GERENTE ---
        if rol == "gerente":
            botones.append(("Empleados", "EmpleadosView", "#9C27B0", "👥"))
            botones.append(("Finanzas", "FinanzasView", "#FF9800", "💰"))

        # Renderizar botones
        for i, (texto, vista, color, icon) in enumerate(botones):
            row, col = divmod(i, 3) # 3 columnas
            
            # Marco del botón (Frame)
            f_btn = tk.Frame(self.container_menu, bg="white", bd=0, cursor="hand2", highlightbackground="#ddd", highlightthickness=1)
            f_btn.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            # Evento click en todo el cuadro
            f_btn.bind("<Button-1>", lambda e, v=vista: self.controller.show_frame(v))
            
            tk.Label(f_btn, text=icon, font=("Segoe UI Emoji", 40), bg="white", fg=color).pack(pady=(25, 10))
            tk.Label(f_btn, text=texto, font=("Segoe UI", 12, "bold"), bg="white", fg="#333").pack(pady=(0, 25))
            
            # Propagar el click a los hijos (labels)
            for child in f_btn.winfo_children():
                child.bind("<Button-1>", lambda e, v=vista: self.controller.show_frame(v))

    def logout(self):
        self.controller.get_vm("login_vm").logout()