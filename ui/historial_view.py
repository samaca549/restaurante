import tkinter as tk
from tkinter import ttk, Listbox, messagebox
from datetime import datetime

class HistorialPedidosView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Obtener el ViewModel específico para esta vista
        try:
            self.vm = controller.get_vm("historial_vm")
        except KeyError:
            # Manejo de error simple si el VM no está registrado
            messagebox.showerror("Error de VM", "No se pudo cargar el ViewModel 'historial_vm'")
            return

        # --- Título y Navegación ---
        ttk.Label(self, text="Historial de Pedidos", font=("Segoe UI", 20, "bold")).pack(pady=10)
        
        f_nav = ttk.Frame(self)
        f_nav.pack(fill="x", padx=10)
        ttk.Button(f_nav, text="< Volver al Menú", 
                   command=lambda: controller.show_frame("HomeView")).pack(side="left")

        # --- Controles ---
        f_controles = ttk.Frame(self, padding=10)
        f_controles.pack(fill="x")
        
        self.load_btn = ttk.Button(f_controles, text="Cargar Pedidos", command=self.vm.cargar_historial_pedidos)
        self.load_btn.pack(side="left", padx=5)
        
        self.delete_btn = ttk.Button(f_controles, text="Eliminar Pedido Seleccionado", 
                                     command=self.on_delete, state="disabled")
        self.delete_btn.pack(side="left", padx=5)

        # --- Paneles de Listas ---
        f_main = ttk.Frame(self)
        f_main.pack(fill="both", expand=True, padx=10, pady=10)
        f_main.columnconfigure(0, weight=1) # Lista de Pedidos
        f_main.columnconfigure(1, weight=1) # Detalle
        f_main.rowconfigure(0, weight=1)

        # --- Columna 1: Lista de Pedidos ---
        f_lista = ttk.LabelFrame(f_main, text="Pedidos")
        f_lista.grid(row=0, column=0, sticky="nsew", padx=5)
        
        self.pedidos_listbox = Listbox(f_lista, font=("Segoe UI", 11), height=15)
        self.pedidos_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.pedidos_listbox.bind("<<ListboxSelect>>", self.on_pedido_select)

        # --- Columna 2: Detalle del Pedido ---
        f_detalle = ttk.LabelFrame(f_main, text="Detalle del Pedido")
        f_detalle.grid(row=0, column=1, sticky="nsew", padx=5)
        
        self.detalle_listbox = Listbox(f_detalle, font=("Segoe UI", 11))
        self.detalle_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Suscribirse a los Observables del VM ---
        self.vm.lista_pedidos.subscribe(self.actualizar_lista_pedidos)
        self.vm.detalle_pedido_seleccionado.subscribe(self.actualizar_detalle_pedido)
        self.vm.mensaje.subscribe(self.show_mensaje)

    def on_show(self):
        """Llamado cuando la vista se muestra."""
        # Cargar automáticamente al mostrar
        self.vm.cargar_historial_pedidos()
        self.delete_btn.config(state="disabled")

    def on_delete(self):
        """Confirmar antes de borrar."""
        if not self.vm.selected_pedido_id:
            return
            
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este pedido? Esta acción no se puede deshacer."):
            self.vm.eliminar_pedido_seleccionado()

    def on_pedido_select(self, event):
        """El usuario hizo clic en la lista de pedidos."""
        try:
            idx_tuple = self.pedidos_listbox.curselection()
            if not idx_tuple:
                return 
                
            idx = idx_tuple[0]
            self.vm.seleccionar_pedido_por_indice(idx)
            self.delete_btn.config(state="normal") # Habilitar el botón de borrar
        except IndexError:
            self.delete_btn.config(state="disabled")

    def actualizar_lista_pedidos(self, pedidos: list[dict]):
        """Rellena la lista de la izquierda."""
        self.pedidos_listbox.delete(0, "end")
        
        if not pedidos:
            self.pedidos_listbox.insert("end", " (No hay pedidos en el historial)")
            return

        for p in pedidos:
            # Convertir el timestamp de Firestore (si existe) a algo legible
            try:
                fecha = p.get('fecha_creacion', 'Fecha desconocida')
                if hasattr(fecha, 'strftime'): # Es un objeto datetime
                    fecha_str = fecha.strftime('%Y-%m-%d %H:%M')
                elif isinstance(fecha, str):
                    # Intentar parsear si es string (p.ej. ISO)
                    fecha_str = datetime.fromisoformat(fecha).strftime('%Y-%m-%d %H:%M')
                else:
                    fecha_str = str(fecha)
            except Exception:
                fecha_str = "Fecha inválida"

            total = p.get('total', 0.0)
            cliente_id = p.get('cliente_id', 'Cliente desc.')
            
            # Mostramos un resumen del pedido
            display_text = f"[{fecha_str}] - ${total:.2f} (ID: ...{p['id'][-6:]})"
            self.pedidos_listbox.insert("end", display_text)

    def actualizar_detalle_pedido(self, items: list[dict]):
        """Rellena la lista de la derecha con los items."""
        self.detalle_listbox.delete(0, "end")
        
        if not items:
            self.detalle_listbox.insert("end", " (Seleccione un pedido para ver su detalle)")
            return

        for item in items:
            nombre = item.get('nombre', 'N/A')
            cantidad = item.get('cantidad', 0)
            precio = item.get('precio_unitario', 0.0)
            subtotal = cantidad * precio
            
            display_text = f"{cantidad}x {nombre} - ${subtotal:.2f}"
            self.detalle_listbox.insert("end", display_text)

    def show_mensaje(self, msg):
        """Muestra un popup con información."""
        if msg:
            messagebox.showinfo("Historial de Pedidos", msg)