import tkinter as tk
from tkinter import ttk, simpledialog
# from domain.models import InventarioItem  # Descomenta si lo necesitas

class InventarioView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.vm = controller.get_vm("inventario_vm")
        
        self.mapa_items = {}
        self.sort_direction = {}

        # ============================================================
        # 1. CONFIGURACIÓN DEL SCROLL RESPONSIVE
        # ============================================================
        self.canvas = tk.Canvas(self, borderwidth=0, background="#f0f0f0")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Configurar el scrollregion cuando el frame interno cambia de tamaño
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # --- CORRECCIÓN CLAVE PARA QUE SE AGRANDE AL MAXIMIZAR ---
        # 1. Creamos la ventana y guardamos su ID
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # 2. Función que ajusta el ancho del frame interno al ancho del canvas
        def _configure_canvas(event):
            self.canvas.itemconfig(self.canvas_frame_id, width=event.width)

        # 3. Vinculamos el evento de redimensionado del canvas
        self.canvas.bind("<Configure>", _configure_canvas)
        # ---------------------------------------------------------

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.bind_all("<MouseWheel>", self._on_mousewheel)

        # ============================================================
        # 2. WIDGETS
        # ============================================================
        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

        # Título
        ttk.Label(self.scrollable_frame, text="📦 Gestión de Inventario", font=("Segoe UI", 20, "bold")).pack(pady=10)
        
        # Navegación
        f_nav = ttk.Frame(self.scrollable_frame)
        f_nav.pack(fill="x", padx=10)
        ttk.Button(f_nav, text="< Volver al Menú", 
                   command=lambda: controller.show_frame("HomeView")).pack(side="left")
        ttk.Button(f_nav, text="🔄 Recargar", command=self.vm.cargar_inventario).pack(side="right")

        # Panel de Creación
        f_create = ttk.LabelFrame(self.scrollable_frame, text="Agregar Nuevo Insumo", padding=10)
        f_create.pack(fill="x", padx=10, pady=10)

        f_input = ttk.Frame(f_create)
        f_input.pack() # Usamos pack aquí, pero grid adentro para centrarlo o expandirlo

        # Configuramos columnas del grid para que se vea ordenado
        ttk.Label(f_input, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.nombre_var = tk.StringVar()
        ttk.Entry(f_input, textvariable=self.nombre_var, width=25).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(f_input, text="Cantidad:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.cantidad_var = tk.StringVar()
        ttk.Entry(f_input, textvariable=self.cantidad_var, width=15).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(f_input, text="Unidad (kg/lt):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.unidad_var = tk.StringVar()
        ttk.Entry(f_input, textvariable=self.unidad_var, width=15).grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(f_input, text="➕ Crear Ítem", command=self.on_create_item).grid(row=0, column=6, padx=15, pady=5)

        # Panel de Recomendación IA
        f_recom = ttk.LabelFrame(self.scrollable_frame, text="Recomendación Automática de IA", padding=10)
        f_recom.pack(fill="x", padx=10, pady=10)
        # Usamos anchor="center" o expandimos
        self.rec_label = ttk.Label(f_recom, text="Cargando recomendación...", font=("Segoe UI", 12, "bold"), foreground="blue", wraplength=1000, justify="center")
        self.rec_label.pack(pady=5, fill="x")

        # Panel de Búsqueda y Tabla
        f_tree_container = ttk.Frame(self.scrollable_frame)
        f_tree_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Búsqueda
        f_search = ttk.Frame(f_tree_container)
        f_search.pack(fill="x", pady=5)
        ttk.Label(f_search, text="Buscar por nombre:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(f_search, textvariable=self.search_var, width=30).pack(side="left", padx=5)
        self.search_var.trace("w", lambda *args: self.update_tree(self.vm.inventario_lista.value))

        # Tabla
        cols = ("Nombre", "Cantidad", "Unidad")
        self.tree = ttk.Treeview(f_tree_container, columns=cols, show="headings", height=15)
        
        # Columnas expandibles
        self.tree.column("Nombre", width=250, anchor="w")
        self.tree.column("Cantidad", width=120, anchor="center")
        self.tree.column("Unidad", width=120, anchor="center")

        for col in cols:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by(c))
            
        self.tree.pack(side="left", fill="both", expand=True)

        sb_tree = ttk.Scrollbar(f_tree_container, orient="vertical", command=self.tree.yview)
        sb_tree.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb_tree.set)

        self.tree.bind("<Double-1>", self.on_item_double_click)
        
        ttk.Label(self.scrollable_frame, text="* Doble click en un ítem para editar su stock", 
                  font=("Segoe UI", 9, "italic"), foreground="gray").pack(pady=5)

        # Mensajes
        self.msg_label = ttk.Label(self.scrollable_frame, text="", font=("Segoe UI", 10, "bold"))
        self.msg_label.pack(pady=5)
        
        # Suscripciones
        self.vm.inventario_lista.subscribe(self.update_tree)
        self.vm.mensaje.subscribe(self.show_vm_message)
        self.vm.recomendacion.subscribe(self.update_recomendacion)

    # --- MÉTODOS ---
    def _on_mousewheel(self, event):
        try:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except: pass

    def on_create_item(self):
        nombre = self.nombre_var.get().strip()
        cant = self.cantidad_var.get().strip()
        unidad = self.unidad_var.get().strip()
        if nombre and cant and unidad:
            try:
                float(cant)
                self.vm.crear_nuevo_item(nombre, cant, unidad)
                self.nombre_var.set(""); self.cantidad_var.set(""); self.unidad_var.set("")
            except ValueError: self.update_message("La cantidad debe ser un número válido.", "red")
        else: self.update_message("Todos los campos son obligatorios.", "red")
        
    def on_show(self): self.vm.cargar_inventario()

    def update_tree(self, items):
        for i in self.tree.get_children(): self.tree.delete(i)
        self.mapa_items = {}
        query = self.search_var.get().lower()
        items_list = items if items else []
        filtered_items = [item for item in items_list if not query or query in item.nombre.lower()]
        for item in filtered_items:
            iid = self.tree.insert("", "end", values=(item.nombre, item.cantidad, item.unidad))
            self.mapa_items[iid] = item

    def sort_by(self, col):
        def safe_float(val):
            try: return float(val)
            except: return 0.0
        children = list(self.tree.get_children(''))
        items = [(self.tree.set(iid, col), iid) for iid in children]
        reverse = self.sort_direction.get(col, False)
        self.sort_direction[col] = not reverse
        key_func = lambda t: safe_float(t[0]) if col == "Cantidad" else (t[0].lower() if isinstance(t[0], str) else t[0])
        items.sort(key=key_func, reverse=reverse)
        for index, (val, iid) in enumerate(items): self.tree.move(iid, '', index)

    def on_item_double_click(self, event):
        selected_iid = self.tree.focus()
        if not selected_iid: return
        item_obj = self.mapa_items.get(selected_iid)
        if not item_obj: return
        nueva_cantidad = simpledialog.askfloat("Actualizar Stock", f"Nueva cantidad para '{item_obj.nombre}':", initialvalue=item_obj.cantidad, minvalue=0.0)
        if nueva_cantidad is not None: self.vm.actualizar_stock(item_obj, nueva_cantidad)

    def show_vm_message(self, msg): self.update_message(msg, "blue")
    def update_message(self, msg, color="green"):
        if msg:
            self.msg_label.config(text=msg, foreground=color)
            self.after(5000, lambda: self.msg_label.config(text=""))
    def update_recomendacion(self, rec): self.rec_label.config(text=rec)