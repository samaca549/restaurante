import tkinter as tk
from tkinter import ttk, messagebox

class EmpleadosView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.vm = controller.get_vm("empleados_vm")
        
        # Variables internas
        self.current_uid = None
        self.mapa_empleados = {}
        
        # Configuración de estilo profesional
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 12), foreground="#333333")
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#333333")
        style.configure("TEntry", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10, width=20)
        style.configure("Delete.TButton", background="#f44336", foreground="white")
        style.map("Delete.TButton", background=[("active", "#d32f2f")])
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

        # --- Título ---
        ttk.Label(self, text="Administrar Empleados", style="Title.TLabel").pack(pady=10)
        
        # --- Navegación ---
        f_nav = ttk.Frame(self)
        f_nav.pack(fill="x", padx=10)
        ttk.Button(f_nav, text="< Volver al Menú", 
                   command=lambda: controller.show_frame("HomeView")).pack(side="left")
        ttk.Button(f_nav, text=" Recargar", command=self.vm.cargar_empleados).pack(side="right")

        # --- Lista de Empleados ---
        f_list = ttk.LabelFrame(self, text="Lista de Empleados", padding=10)
        f_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        cols = ("Email", "Rol")
        self.tree = ttk.Treeview(f_list, columns=cols, show="headings", height=10)
        self.tree.column("Email", width=300, anchor="w")
        self.tree.column("Rol", width=150, anchor="center")
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.pack(side="left", fill="both", expand=True)
        
        sb = ttk.Scrollbar(f_list, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)
        
        # Evento de selección
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # --- Formulario ---
        f_form = ttk.LabelFrame(self, text="Formulario de Empleado", padding=15)
        f_form.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(f_form, text="Email:").grid(row=0, column=0, sticky="e", padx=10, pady=5)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(f_form, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(f_form, text="Contraseña:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.pass_var = tk.StringVar()
        self.pass_entry = ttk.Entry(f_form, textvariable=self.pass_var, width=40, show="*")
        self.pass_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(f_form, text="Rol:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.rol_var = tk.StringVar(value="mesero")
        self.rol_combo = ttk.Combobox(f_form, textvariable=self.rol_var, values=["mesero", "gerente"], state="readonly", width=37)
        self.rol_combo.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Nota para contraseña en edición
        self.pass_note = ttk.Label(f_form, text="(Dejar en blanco para no cambiar)", font=("Segoe UI", 9, "italic"), foreground="gray")
        self.pass_note.grid(row=3, column=1, sticky="w", padx=10)
        self.pass_note.grid_remove()  # Ocultar inicialmente
        
        # Botones de acción
        f_buttons = ttk.Frame(f_form)
        f_buttons.grid(row=4, column=0, columnspan=2, pady=15)
        
        self.btn_accion = ttk.Button(f_buttons, text="Crear Empleado", command=self.on_accion)
        self.btn_accion.pack(side="left", padx=5)
        
        self.btn_eliminar = ttk.Button(f_buttons, text="Eliminar Empleado", command=self.on_eliminar, style="Delete.TButton", state="disabled")
        self.btn_eliminar.pack(side="left", padx=5)
        
        # --- Mensajes ---
        self.msg_label = ttk.Label(self, text="", font=("Segoe UI", 10, "bold"))
        self.msg_label.pack(pady=5)
        
        # --- Suscripciones ---
        self.vm.empleados_lista.subscribe(self.update_tree)
        self.vm.mensaje.subscribe(lambda m: self.update_message(m, "green"))
        self.vm.error.subscribe(lambda e: self.update_message(e, "red"))

    def on_show(self):
        self.vm.cargar_empleados()
        self.limpiar_formulario()

    def update_tree(self, empleados):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.mapa_empleados = {}
        for emp in empleados:
            iid = self.tree.insert("", "end", values=(emp.email, emp.rol.capitalize()))
            self.mapa_empleados[iid] = emp

    def on_select(self, event):
        selected_iid = self.tree.focus()
        if selected_iid:
            emp = self.mapa_empleados.get(selected_iid)
            if emp:
                self.current_uid = emp.uid
                self.email_var.set(emp.email)
                self.email_entry.config(state="disabled")
                self.rol_var.set(emp.rol)
                self.pass_var.set("")
                self.pass_note.grid()
                self.btn_accion.config(text="Actualizar Empleado")
                self.btn_eliminar.config(state="normal")
        else:
            self.limpiar_formulario()

    def limpiar_formulario(self):
        self.current_uid = None
        self.email_var.set("")
        self.email_entry.config(state="normal")
        self.pass_var.set("")
        self.rol_var.set("mesero")
        self.pass_note.grid_remove()
        self.btn_accion.config(text="Crear Empleado")
        self.btn_eliminar.config(state="disabled")

    def on_accion(self):
        email = self.email_var.get().strip()
        password = self.pass_var.get().strip()
        rol = self.rol_var.get().strip()
        
        if not rol:
            self.update_message("Seleccione un rol.", "red")
            return
        
        if self.current_uid:
            # Actualizar (password opcional)
            self.vm.actualizar_empleado(self.current_uid, rol, password if password else None)
        else:
            # Crear
            if not email or not password:
                self.update_message("Email y contraseña son obligatorios.", "red")
                return
            if not self.validar_email(email):
                self.update_message("Formato de email inválido.", "red")
                return
            if len(password) < 6:
                self.update_message("La contraseña debe tener al menos 6 caracteres.", "red")
                return
            self.vm.crear_empleado(email, password, rol)

    def on_eliminar(self):
        if self.current_uid and messagebox.askyesno("Confirmar", "¿Eliminar este empleado?"):
            self.vm.eliminar_empleado(self.current_uid)

    def update_message(self, msg, color):
        if msg:
            self.msg_label.config(text=msg, foreground=color)
            if color == "green":
                self.limpiar_formulario()
                self.after(5000, lambda: self.msg_label.config(text=""))
        else:
            self.msg_label.config(text="")

    def validar_email(self, email):
        import re
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None
