import tkinter as tk
from tkinter import ttk, messagebox

class HistorialPedidosView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.vm = controller.get_vm("historial_vm") 
        
        ttk.Label(self, text=" Historial de Pedidos", font=("Segoe UI", 20, "bold")).pack(pady=10)

        f_nav = ttk.Frame(self)
        f_nav.pack(fill="x", padx=10)
        ttk.Button(f_nav, text="< Volver al Menú", 
                   command=lambda: controller.show_frame("HomeView")).pack(side="left")

        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # Panel Izquierdo
        f_left = ttk.LabelFrame(paned, text="Lista de Pedidos", padding=5)
        paned.add(f_left, weight=1)

        cols = ("ID", "Cliente", "Total")
        self.tree_pedidos = ttk.Treeview(f_left, columns=cols, show="headings")
        self.tree_pedidos.column("ID", width=60)
        self.tree_pedidos.column("Cliente", width=120)
        self.tree_pedidos.column("Total", width=80)
        for c in cols: self.tree_pedidos.heading(c, text=c)
        self.tree_pedidos.pack(fill="both", expand=True)
        self.tree_pedidos.bind("<<TreeviewSelect>>", self.on_pedido_select)

        # Panel Derecho
        f_right = ttk.LabelFrame(paned, text="Detalle", padding=5)
        paned.add(f_right, weight=1)

        cols_det = ("Cant", "Producto", "Precio")
        self.tree_detalle = ttk.Treeview(f_right, columns=cols_det, show="headings")
        for c in cols_det: self.tree_detalle.heading(c, text=c)
        self.tree_detalle.pack(fill="both", expand=True)

        # Botones
        f_btns = ttk.Frame(f_right)
        f_btns.pack(fill="x", pady=5)
        ttk.Button(f_btns, text="🔄 Recargar", command=self.vm.cargar_historial_pedidos).pack(side="left")
        ttk.Button(f_btns, text="🗑️ Eliminar", command=self.vm.eliminar_pedido_seleccionado).pack(side="right")

        # Suscripciones
        self.vm.lista_pedidos.subscribe(self.update_pedidos)
        self.vm.detalle_pedido_seleccionado.subscribe(self.update_detalle)
        self.vm.mensaje.subscribe(lambda m: messagebox.showinfo("Info", m) if m else None)

    def on_show(self):
        self.vm.cargar_historial_pedidos()

    def update_pedidos(self, pedidos):
        for i in self.tree_pedidos.get_children(): self.tree_pedidos.delete(i)
        for p in pedidos:
            pedido_id = p.get("id")
            self.tree_pedidos.insert("", "end", iid=pedido_id, values=(
                str(pedido_id)[-4:], p.get("cliente_nombre", "N/A"), f"${p.get('total',0):,.0f}"
            )) 

    def on_pedido_select(self, event):
        sel = self.tree_pedidos.focus()
        if sel:
            self.vm.seleccionar_pedido(sel)

    def update_detalle(self, items):
        for i in self.tree_detalle.get_children(): self.tree_detalle.delete(i)
        for item in items:
            self.tree_detalle.insert("", "end", values=(
                item.get("cantidad"), item.get("nombre"), f"${item.get('precio_unitario',0):,.0f}"
            ))
