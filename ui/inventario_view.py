import tkinter as tk
from tkinter import ttk, simpledialog
from domain.models import InventarioItem  # Añadido para anotaciones si es necesario

class InventarioView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.vm = controller.get_vm("inventario_vm")
        
        # Diccionario para mapear ID del Treeview -> Objeto InventarioItem
        self.mapa_items = {}

        # Dirección de ordenamiento por columna (False: asc, True: desc)
        self.sort_direction = {}

        # Configuración de estilo para mejora visual
        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

        # --- Título ---
        ttk.Label(self, text="📦 Gestión de Inventario", font=("Segoe UI", 20, "bold")).pack(pady=10)
        
        # --- Navegación ---
        f_nav = ttk.Frame(self)
        f_nav.pack(fill="x", padx=10)
        ttk.Button(f_nav, text="< Volver al Menú", 
                   command=lambda: controller.show_frame("HomeView")).pack(side="left")
        ttk.Button(f_nav, text="🔄 Recargar", command=self.vm.cargar_inventario).pack(side="right")

        # --- Panel de Creación (Mejorado con grid y validaciones) ---
        f_create = ttk.LabelFrame(self, text="Agregar Nuevo Insumo", padding=10)
        f_create.pack(fill="x", padx=10, pady=10)

        f_input = ttk.Frame(f_create)
        f_input.pack()

        # Grid de inputs con más espacio
        ttk.Label(f_input, text="Nombre:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.nombre_var = tk.StringVar()
        ttk.Entry(f_input, textvariable=self.nombre_var, width=25).grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(f_input, text="Cantidad:").grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.cantidad_var = tk.StringVar()
        ttk.Entry(f_input, textvariable=self.cantidad_var, width=15).grid(row=0, column=3, padx=10, pady=5)

        ttk.Label(f_input, text="Unidad (kg/lt):").grid(row=0, column=4, padx=10, pady=5, sticky="e")
        self.unidad_var = tk.StringVar()
        ttk.Entry(f_input, textvariable=self.unidad_var, width=15).grid(row=0, column=5, padx=10, pady=5)

        ttk.Button(f_input, text="➕ Crear Ítem", command=self.on_create_item).grid(row=0, column=6, padx=20, pady=5)

        # --- Panel de Recomendación IA (Nuevo: Cuadro automático) ---
        f_recom = ttk.LabelFrame(self, text="Recomendación Automática de IA", padding=10)
        f_recom.pack(fill="x", padx=10, pady=10)
        self.rec_label = ttk.Label(f_recom, text="Cargando recomendación...", font=("Segoe UI", 12, "bold"), foreground="blue")
        self.rec_label.pack(pady=5)

        # --- Panel de Búsqueda y Tabla ---
        f_tree = ttk.Frame(self)
        f_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Búsqueda (Nueva funcionalidad)
        f_search = ttk.Frame(f_tree)
        f_search.pack(fill="x", pady=5)
        ttk.Label(f_search, text="Buscar por nombre:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(f_search, textvariable=self.search_var, width=30).pack(side="left", padx=5)
        self.search_var.trace("w", lambda *args: self.update_tree(self.vm.inventario_lista.value))

        # Tabla (Treeview con scroll y sortable)
        cols = ("Nombre", "Cantidad", "Unidad")
        self.tree = ttk.Treeview(f_tree, columns=cols, show="headings", height=15)
        
        self.tree.column("Nombre", width=250, anchor="w")
        self.tree.column("Cantidad", width=120, anchor="center")
        self.tree.column("Unidad", width=120, anchor="center")

        for col in cols:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by(c))
            
        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(f_tree, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        # Evento Doble Click para editar
        self.tree.bind("<Double-1>", self.on_item_double_click)
        
        ttk.Label(self, text="* Doble click en un ítem para editar su stock", 
                  font=("Segoe UI", 9, "italic"), foreground="gray").pack(pady=5)

        # --- Mensajes ---
        self.msg_label = ttk.Label(self, text="", font=("Segoe UI", 10, "bold"))
        self.msg_label.pack(pady=5)
        
        # --- Suscripciones ---
        self.vm.inventario_lista.subscribe(self.update_tree)
        self.vm.mensaje.subscribe(self.show_vm_message)
        self.vm.recomendacion.subscribe(self.update_recomendacion)

    def on_create_item(self):
        nombre = self.nombre_var.get().strip()
        cant = self.cantidad_var.get().strip()
        unidad = self.unidad_var.get().strip()

        if nombre and cant and unidad:
            try:
                float(cant)  # Validación numérica
                self.vm.crear_nuevo_item(nombre, cant, unidad)
                # Limpiar campos
                self.nombre_var.set("")
                self.cantidad_var.set("")
                self.unidad_var.set("")
            except ValueError:
                self.update_message("La cantidad debe ser un número válido.", "red")
        else:
            self.update_message("Todos los campos son obligatorios.", "red")
        
    def on_show(self):
        self.vm.cargar_inventario()

    def update_tree(self, items):
        # Limpiar tabla y mapa
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.mapa_items = {}
        
        # Aplicar filtro de búsqueda
        query = self.search_var.get().lower()
        filtered_items = [item for item in items if not query or query in item.nombre.lower()]
        
        # Llenar tabla
        for item in filtered_items:
            iid = self.tree.insert("", "end", values=(item.nombre, item.cantidad, item.unidad))
            self.mapa_items[iid] = item

    def sort_by(self, col):
        # Función auxiliar para convertir a float de forma segura
        def safe_float(val):
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0

        # Obtener items actuales
        children = list(self.tree.get_children(''))
        items = [(self.tree.set(iid, col), iid) for iid in children]

        # Determinar dirección (toggle)
        reverse = self.sort_direction.get(col, False)
        self.sort_direction[col] = not reverse

        # Definir la función key basada en la columna (sin redefinir nombres)
        if col == "Cantidad":
            key_func = lambda t: safe_float(t[0])
        else:
            key_func = lambda t: t[0].lower() if isinstance(t[0], str) else t[0]

        # Ordenar
        items.sort(key=key_func, reverse=reverse)

        # Reorganizar
        for index, (val, iid) in enumerate(items):
            self.tree.move(iid, '', index)

    def on_item_double_click(self, event):
        selected_iid = self.tree.focus()
        if not selected_iid: return
        
        item_obj = self.mapa_items.get(selected_iid)
        if not item_obj: return

        nueva_cantidad = simpledialog.askfloat(
            "Actualizar Stock",
            f"Nueva cantidad para '{item_obj.nombre}' ({item_obj.unidad}):",
            initialvalue=item_obj.cantidad,
            minvalue=0.0
        )
        
        if nueva_cantidad is not None:
            self.vm.actualizar_stock(item_obj, nueva_cantidad)

    def show_vm_message(self, msg):
        self.update_message(msg, "blue")

    def update_message(self, msg, color="green"):
        if msg:
            self.msg_label.config(text=msg, foreground=color)
            self.after(5000, lambda: self.msg_label.config(text=""))  # Aumentado a 5s para mejor visibilidad

    def update_recomendacion(self, rec):
        self.rec_label.config(text=rec)