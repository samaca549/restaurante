import tkinter as tk
from tkinter import ttk, simpledialog

class InventarioView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.vm = controller.get_vm("inventario_vm")

        ttk.Label(self, text="Gestión de Inventario", font=("Segoe UI", 20, "bold")).pack(pady=10)
        
        f_nav = ttk.Frame(self)
        f_nav.pack(fill="x", padx=10)
        ttk.Button(f_nav, text="< Volver al Menú", 
                   command=lambda: controller.show_frame("HomeView")).pack(side="left")

        # --- Treeview para mostrar inventario ---
        f_tree = ttk.Frame(self)
        f_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        cols = ("Nombre", "Cantidad", "Unidad")
        self.tree = ttk.Treeview(f_tree, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(f_tree, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.bind("<Double-1>", self.on_item_double_click)

        # Mensajes
        self.msg_label = ttk.Label(self, text="")
        self.msg_label.pack(pady=5)
        
        # Suscribir
        self.vm.inventario_lista.subscribe(self.update_tree)
        self.vm.mensaje.subscribe(self.update_message)
    # --- Sección de Creación de Inventario (NUEVO) ---
        f_create = ttk.LabelFrame(self, text="Crear Nuevo Ítem", padding=10)
        f_create.pack(fill="x", padx=10, pady=10)

        # Usar un Frame interior para el layout de 3x2
        f_input = ttk.Frame(f_create)
        f_input.pack()

        ttk.Label(f_input, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(f_input, textvariable=self.nombre_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(f_input, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5)
        self.cantidad_var = tk.StringVar()
        ttk.Entry(f_input, textvariable=self.cantidad_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(f_input, text="Unidad:").grid(row=2, column=0, padx=5, pady=5)
        self.unidad_var = tk.StringVar()
        ttk.Entry(f_input, textvariable=self.unidad_var).grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(f_create, text="Crear Ítem", command=self.on_create_item).pack(pady=10)

        # ... (código treeview existente)

    def on_create_item(self):
        nombre = self.nombre_var.get()
        cantidad = self.cantidad_var.get()
        unidad = self.unidad_var.get()

        if nombre and cantidad and unidad:
            self.vm.crear_nuevo_item(nombre, cantidad, unidad)
            # Limpiar campos
            self.nombre_var.set("")
            self.cantidad_var.set("")
            self.unidad_var.set("")
        else:
            self.update_message("Todos los campos son obligatorios.", "red")
        
    def on_show(self):
        """Al mostrar, recargar los datos."""
        self.vm.cargar_inventario()

    def update_tree(self, items):
        # Limpiar tabla
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Llenar tabla
        # Guardamos el objeto de dominio en el tag 'item'
        for item in items:
            self.tree.insert("", "end", values=(item.nombre, item.cantidad, item.unidad), tags=(item,))

    def on_item_double_click(self, event):
        """Permite editar el stock al hacer doble clic."""
        selected_id = self.tree.focus()
        if not selected_id: return
        
        # Obtenemos el objeto de dominio que guardamos en 'tags'
        item_obj = self.tree.item(selected_id)["tags"][0]
        
        nueva_cantidad = simpledialog.askfloat(
            "Actualizar Stock",
            f"Ingrese la nueva cantidad para '{item_obj.nombre}' (Actual: {item_obj.cantidad}):",
            minvalue=0.0
        )
        
        if nueva_cantidad is not None:
            self.vm.actualizar_stock(item_obj, nueva_cantidad)

    def update_message(self, msg):
        if msg:
            self.msg_label.config(text=msg, foreground="green")
            # Limpiar mensaje después de 3 seg
            self.after(3000, lambda: self.msg_label.config(text=""))