import tkinter as tk
from tkinter import ttk, Listbox, messagebox
from domain.models import Plato
from domain.restaurante import Pedido

class PedidosView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.vm = controller.get_vm("pedidos_vm")
        
        self.selected_plato = None

        # Título
        ttk.Label(self, text="Tomar Pedido", font=("Segoe UI", 20, "bold")).pack(pady=10)
        
        # Frame de Navegación
        f_nav = ttk.Frame(self)
        f_nav.pack(fill="x", padx=10)
        ttk.Button(f_nav, text="< Volver al Menú", 
                   command=lambda: controller.show_frame("HomeView")).pack(side="left")

        # Frame de Cliente
        f_cliente = ttk.LabelFrame(self, text="Datos del Cliente", padding=10)
        f_cliente.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(f_cliente, text="Email:").grid(row=0, column=0, padx=5)
        self.cliente_email_entry = ttk.Entry(f_cliente, width=30)
        self.cliente_email_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(f_cliente, text="Nombre:").grid(row=0, column=2, padx=5)
        self.cliente_nombre_entry = ttk.Entry(f_cliente, width=30)
        self.cliente_nombre_entry.grid(row=0, column=3, padx=5)
        
        ttk.Button(f_cliente, text="Iniciar Pedido", command=self.iniciar_pedido).grid(row=0, column=4, padx=10)

        # --- Paneles ---
        f_main = ttk.Frame(self)
        f_main.pack(fill="both", expand=True, padx=10, pady=10)
        f_main.columnconfigure(0, weight=1) # Menú
        f_main.columnconfigure(1, weight=1) # Pedido
        f_main.columnconfigure(2, weight=1) # IA
        f_main.rowconfigure(0, weight=1)

        # --- Columna 1: Menú ---
        f_menu = ttk.LabelFrame(f_main, text="Menú (Platos)")
        f_menu.grid(row=0, column=0, sticky="nsew", padx=5)
        
        self.menu_listbox = Listbox(f_menu, font=("Segoe UI", 12), height=15)
        self.menu_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.menu_listbox.bind("<<ListboxSelect>>", self.on_menu_select)

        # --- Columna 2: Pedido Actual ---
        f_pedido = ttk.LabelFrame(f_main, text="Pedido Actual")
        f_pedido.grid(row=0, column=1, sticky="nsew", padx=5)
        
        f_add = ttk.Frame(f_pedido)
        f_add.pack(fill="x", pady=5)
        ttk.Label(f_add, text="Cantidad:").pack(side="left", padx=5)
        self.cantidad_entry = ttk.Entry(f_add, width=5)
        self.cantidad_entry.insert(0, "1")
        self.cantidad_entry.pack(side="left", padx=5)
        self.add_btn = ttk.Button(f_add, text="Añadir Plato", state="disabled", command=self.on_add_plato)
        self.add_btn.pack(side="left", padx=5)

        self.pedido_listbox = Listbox(f_pedido, font=("Segoe UI", 12))
        self.pedido_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.total_label = ttk.Label(f_pedido, text="Total: $0.00", font=("Segoe UI", 16, "bold"))
        self.total_label.pack(pady=10)
        
        self.finalizar_btn = ttk.Button(f_pedido, text="Finalizar Pedido", state="disabled", command=self.on_finalizar)
        self.finalizar_btn.pack(pady=10)

        # --- Columna 3: IA ---
        f_ia = ttk.LabelFrame(f_main, text="Asistente IA")
        f_ia.grid(row=0, column=2, sticky="nsew", padx=5)
        
        ttk.Button(f_ia, text="¿Qué plato se vende más?", command=self.vm.pedir_analisis_ia).pack(pady=10)
        self.ia_report_label = ttk.Label(f_ia, text="", wraplength=300, justify="left")
        self.ia_report_label.pack(fill="x", padx=10, pady=10)

        # Suscribir a Observables
        self.vm.platos_menu.subscribe(self.update_menu_list)
        self.vm.pedido_actual.subscribe(self.update_pedido_list)
        self.vm.mensaje.subscribe(self.show_mensaje)
        self.vm.reporte_ia.subscribe(lambda r: self.ia_report_label.config(text=r))

    def on_show(self):
        """Al mostrar la vista, cargar el menú."""
        self.vm.cargar_platos()
        # Limpiar datos anteriores
        self.vm.pedido_actual.value = None
        self.cliente_email_entry.delete(0, "end")
        self.cliente_nombre_entry.delete(0, "end")
        self.ia_report_label.config(text="")

    def iniciar_pedido(self):
        email = self.cliente_email_entry.get()
        nombre = self.cliente_nombre_entry.get()
        self.vm.iniciar_nuevo_pedido(email, nombre)

    def on_menu_select(self, event):
        try:
            idx = self.menu_listbox.curselection()[0]
            self.selected_plato = self.vm.platos_menu.value[idx]
            self.add_btn.config(state="normal")
        except IndexError:
            self.selected_plato = None
            self.add_btn.config(state="disabled")

    def on_add_plato(self):
        if not self.selected_plato: return
        try:
            cantidad = int(self.cantidad_entry.get())
            self.vm.agregar_plato_al_pedido(self.selected_plato, cantidad)
        except ValueError:
            self.show_mensaje("Error: La cantidad debe ser un número.")

    def on_finalizar(self):
        self.vm.finalizar_pedido()

    def update_menu_list(self, platos: list[Plato]):
        self.menu_listbox.delete(0, "end")
        for p in platos:
            self.menu_listbox.insert("end", f"{p.nombre} - ${p.precio:.2f}")

    def update_pedido_list(self, pedido: Pedido):
        self.pedido_listbox.delete(0, "end")
        if not pedido:
            self.total_label.config(text="Total: $0.00")
            self.finalizar_btn.config(state="disabled")
            return
            
        self.finalizar_btn.config(state="normal")
        for item in pedido.items:
            subtotal = item["precio_unitario"] * item["cantidad"]
            self.pedido_listbox.insert("end", f"{item['cantidad']}x {item['nombre']} - ${subtotal:.2f}")
        self.total_label.config(text=f"Total: ${pedido.total:.2f}")
        
    def show_mensaje(self, msg):
        if msg: messagebox.showinfo("Info Pedido", msg)