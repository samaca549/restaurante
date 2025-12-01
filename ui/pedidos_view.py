import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw 
import os
import threading
import random 

# =======================================================
# 1. WIDGET DE CONSEJO PRODUCTIVO (ESTILO AZUL)
# =======================================================
class PromoWidget(tk.Frame):
    def __init__(self, parent, **kwargs):
        # Fondo azul claro para diferenciarlo de comida
        super().__init__(parent, bg="#E3F2FD", bd=1, relief="solid", **kwargs) 
        self.columnconfigure(1, weight=1)
        
        # Título
        tk.Label(self, text=" 💡 TIP DE GESTIÓN (IA) ", bg="#E3F2FD", fg="#1565C0", 
                 font=("Segoe UI", 9, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(5,0))

        # Icono fijo (Cerebro/Idea)
        self.lbl_icon = tk.Label(self, text="🧠", font=("Segoe UI Emoji", 40), bg="#E3F2FD")
        self.lbl_icon.grid(row=1, column=0, rowspan=2, padx=10, pady=10)

        # Texto del consejo
        self.lbl_texto = tk.Label(self, text="Analizando...", bg="#E3F2FD", fg="#333",
                                  font=("Segoe UI", 11, "italic"), wraplength=280, justify="left")
        self.lbl_texto.grid(row=1, column=1, sticky="nw", padx=5, pady=15)

    def actualizar_consejo(self, texto):
        self.lbl_texto.config(text=f"{texto}")

# =======================================================
# 2. FUNCIÓN AUXILIAR DE CARGA DE IMAGEN (ROBUSTA)
# =======================================================
def _cargar_imagen_comun(plato, width, height):
    """Carga imagen sin fallar por ImageDraw."""
    
    # 1. Limpieza de nombre
    nombre = "plato"
    if plato and hasattr(plato, 'nombre') and plato.nombre:
        nombre = plato.nombre.lower().strip()
    
    reemplazos = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n"), ("(", ""), (")", ""), (".", ""))
    for a, b in reemplazos:
        nombre = nombre.replace(a, b)
    
    nombre_limpio = nombre.replace(" ", "_")
    while "__" in nombre_limpio: nombre_limpio = nombre_limpio.replace("__", "_")

    # 2. Buscar archivo real
    rutas = [f"img/{nombre_limpio}.png", f"img/{nombre_limpio}.jpg", f"img/{nombre_limpio}.jpeg"]
    archivo = None
    for r in rutas:
        if os.path.exists(r):
            archivo = r
            break
    
    # 3. Intentar cargar imagen
    try:
        if archivo:
            pil_img = Image.open(archivo)
            pil_img = pil_img.resize((width, height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(pil_img)
    except: pass
    
    # 4. Placeholder SEGURO (Si falla Draw, devuelve cuadro liso)
    try:
        img = Image.new('RGB', (width, height), color="#FF9800")
        d = ImageDraw.Draw(img)
        # Solo dibujamos si tenemos texto, si falla, no pasa nada
        iniciales = "??"
        if plato and hasattr(plato, 'nombre') and plato.nombre:
             iniciales = plato.nombre[:2].upper()
        
        # Coordenadas simples para evitar errores de cálculo
        d.text((width/2 - 10, height/2 - 10), iniciales, fill="white")
        return ImageTk.PhotoImage(img)
    except Exception as e:
        # ULTIMO RECURSO: Si ImageDraw falla (raro), devolvemos cuadro negro
        img = Image.new('RGB', (width, height), color="gray")
        return ImageTk.PhotoImage(img)

# =======================================================
# 3. SCROLLABLE FRAME
# =======================================================
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg="#f0f2f5", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# =======================================================
# 4. TARJETA DE PLATO
# =======================================================
class PlatoCard(tk.Frame):
    def __init__(self, parent, plato, on_click_img, on_qty_change):
        super().__init__(parent, bg="white", bd=0, relief="flat")
        self.plato = plato
        self.on_click_img = on_click_img
        self.on_qty_change = on_qty_change
        self.cantidad = 0

        self.container = tk.Frame(self, bg="white", padx=0, pady=0)
        self.container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Usamos la función global segura
        self.img_obj = _cargar_imagen_comun(plato, 150, 110)
        self.lbl_img = tk.Label(self.container, image=self.img_obj, bg="white", cursor="hand2")
        self.lbl_img.pack(fill="x")
        self.lbl_img.bind("<Button-1>", lambda e: self.on_click_img(self.plato))

        f_info = tk.Frame(self.container, bg="white", padx=8, pady=5)
        f_info.pack(fill="both", expand=True)
        tk.Label(f_info, text=plato.nombre, font=("Segoe UI", 11, "bold"), bg="white", fg="#333", wraplength=130).pack(anchor="w")
        tk.Label(f_info, text=f"${plato.precio:,.0f}", font=("Segoe UI", 10), bg="white", fg="#666").pack(anchor="w")

        f_btns = tk.Frame(self.container, bg="white", pady=5)
        f_btns.pack(fill="x", padx=5, pady=5)
        tk.Button(f_btns, text="−", font=("Arial", 12, "bold"), bg="#ffebee", fg="#c62828", bd=0, width=3, command=self._restar).pack(side="left")
        self.lbl_qty = tk.Label(f_btns, text="0", font=("Segoe UI", 12, "bold"), bg="white", width=3)
        self.lbl_qty.pack(side="left", expand=True)
        tk.Button(f_btns, text="+", font=("Arial", 12, "bold"), bg="#e8f5e9", fg="#2e7d32", bd=0, width=3, command=self._sumar).pack(side="right")
        self.update_ui()

    def _sumar(self): self.cantidad += 1; self.update_ui(); self.on_qty_change(self.plato, self.cantidad)
    def _restar(self): 
        if self.cantidad > 0: self.cantidad -= 1; self.update_ui(); self.on_qty_change(self.plato, self.cantidad)
    def set_cantidad(self, qty): self.cantidad = qty; self.update_ui()
    def update_ui(self):
        self.lbl_qty.config(text=str(self.cantidad))
        if self.cantidad > 0: self.config(bg="#2196f3", padx=2, pady=2) 
        else: self.config(bg="#ddd", padx=1, pady=1)

# =======================================================
# 5. VISTA PRINCIPAL (PedidosView)
# =======================================================
class PedidosView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.vm = controller.get_vm("pedidos_vm")
        self.cards_map = {} 

        self.columnconfigure(0, weight=3) 
        self.columnconfigure(1, weight=1) 
        self.rowconfigure(1, weight=1)

        self._setup_header()

        # PANEL IZQUIERDO
        f_left = tk.Frame(self, bg="#f0f2f5")
        f_left.grid(row=1, column=0, sticky="nsew")
        
        # A) Usamos el Widget NUEVO (TIP AZUL)
        self.promo_widget = PromoWidget(f_left)
        self.promo_widget.pack(fill="x", padx=15, pady=(10, 5))

        tk.Label(f_left, text="🍔 Menú Disponible", font=("Segoe UI", 18, "bold"), 
                 bg="#f0f2f5", fg="#333").pack(anchor="w", padx=20, pady=5)
        
        self.scroll_menu = ScrollableFrame(f_left)
        self.scroll_menu.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # PANEL DERECHO
        f_ticket = tk.Frame(self, bg="white", bd=1, relief="solid")
        f_ticket.grid(row=1, column=1, sticky="nsew", padx=0)
        f_ticket.pack_propagate(False)

        tk.Label(f_ticket, text="Tu Orden", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=15)
        
        style = ttk.Style()
        style.configure("Ticket.Treeview", font=("Segoe UI", 10), rowheight=25)
        self.tree = ttk.Treeview(f_ticket, columns=("cant", "item", "precio"), show="headings", height=10, style="Ticket.Treeview")
        self.tree.heading("cant", text="#"); self.tree.column("cant", width=30, anchor="center")
        self.tree.heading("item", text="Producto"); self.tree.column("item", width=120, anchor="w")
        self.tree.heading("precio", text="Total"); self.tree.column("precio", width=60, anchor="e")
        self.tree.pack(fill="both", expand=True, padx=5)

        f_total = tk.Frame(f_ticket, bg="#fafafa", pady=10)
        f_total.pack(fill="x", side="bottom")
        self.lbl_total = tk.Label(f_total, text="$0.00", font=("Segoe UI", 22, "bold"), bg="#fafafa", fg="#2e7d32")
        self.lbl_total.pack()
        self.btn_pay = tk.Button(f_total, text="FINALIZAR PEDIDO", font=("Segoe UI", 11, "bold"), bg="#333", fg="white", cursor="hand2", state="disabled", pady=10, command=self.on_finalizar)
        self.btn_pay.pack(fill="x", padx=15, pady=10)

        self.vm.platos_menu.subscribe(self.render_menu)
        self.vm.pedido_actual.subscribe(self.update_ticket)
        self.vm.mensaje.subscribe(self.show_message)
        
        self.after(60000, self._ciclo_recomendacion_ia)

    def on_show(self):
        self.vm.cargar_platos()
        
        # 1. Consejo Rápido (Aleatorio)
        consejos_rapidos = [
            "Revisa si hay productos por vencer en inventario.",
            "Considera crear una promoción de Happy Hour.",
            "Analiza cuál es el plato menos vendido de la semana.",
            "Asegúrate de que el equipo esté motivado hoy.",
            "Verifica la limpieza del área de mesas."
        ]
        self.promo_widget.actualizar_consejo(random.choice(consejos_rapidos))
        
        # 2. IA Real en segundo plano
        threading.Thread(target=self._tarea_background_ia, daemon=True).start()

        # Limpieza
        for card in self.cards_map.values(): card.set_cantidad(0)
        self.tree.delete(*self.tree.get_children())
        self.lbl_total.config(text="$0.00")
        self.ent_nombre.delete(0, 'end')
        self.ent_email.delete(0, 'end')

    def _ciclo_recomendacion_ia(self):
        threading.Thread(target=self._tarea_background_ia, daemon=True).start()
        self.after(60000, self._ciclo_recomendacion_ia)

    def _tarea_background_ia(self):
        try:
            ia_service = getattr(self.controller, 'ia_service', None)
            if not ia_service: return

            # Llamada al método corregido en ia_service
            consejo = ia_service.obtener_consejo_productivo()
            
            if consejo:
                self.after(0, lambda: self.promo_widget.actualizar_consejo(consejo))
        except Exception as e:
            print(f"Error hilo IA: {e}")

    # SETUP Y EVENTOS
    def _setup_header(self):
        f_head = tk.Frame(self, bg="white", height=60)
        f_head.grid(row=0, column=0, columnspan=2, sticky="ew")
        f_head.pack_propagate(False)
        tk.Button(f_head, text="🔙 Volver", command=lambda: self.controller.show_frame("HomeView"), bg="#eee", bd=0).pack(side="left", padx=10)
        tk.Label(f_head, text="Cliente:", bg="white").pack(side="left", padx=5)
        self.ent_nombre = ttk.Entry(f_head, width=15); self.ent_nombre.pack(side="left")
        tk.Label(f_head, text="Email:", bg="white").pack(side="left", padx=5)
        self.ent_email = ttk.Entry(f_head, width=20); self.ent_email.pack(side="left")
        tk.Button(f_head, text="▶ Iniciar", bg="#007bff", fg="white", bd=0, command=self.iniciar_pedido).pack(side="left", padx=10)

    def iniciar_pedido(self): self.vm.iniciar_nuevo_pedido(self.ent_email.get(), self.ent_nombre.get())

    def render_menu(self, platos):
        for w in self.scroll_menu.scrollable_frame.winfo_children(): w.destroy()
        self.cards_map = {}
        COLUMNS = 4 
        for i, plato in enumerate(platos):
            row, col = divmod(i, COLUMNS)
            card = PlatoCard(self.scroll_menu.scrollable_frame, plato, self.handle_card_click, self.handle_qty_change)
            card.grid(row=row, column=col, padx=10, pady=10)
            self.cards_map[plato.id] = card

    def handle_card_click(self, plato):
        self.vm.sumar_unidad(plato)
        new_qty = self.vm.cantidades_temp.get(plato.id, 0)
        if plato.id in self.cards_map: self.cards_map[plato.id].set_cantidad(new_qty)

    def handle_qty_change(self, plato, cantidad):
        success = self.vm.actualizar_cantidad_plato(plato, cantidad)
        if not success and plato.id in self.cards_map: self.cards_map[plato.id].set_cantidad(0)

    def update_ticket(self, pedido):
        self.tree.delete(*self.tree.get_children())
        if not pedido or not pedido.items:
            self.lbl_total.config(text="$0.00"); self.btn_pay.config(state="disabled", bg="#555"); return
        for item in pedido.items:
            sub = item['cantidad'] * item['precio_unitario']
            self.tree.insert("", "end", values=(item['cantidad'], item['nombre'], f"${sub:,.0f}"))
        self.lbl_total.config(text=f"${pedido.total:,.0f}"); self.btn_pay.config(state="normal", bg="#212121")

    def on_finalizar(self):
        self.vm.finalizar_pedido()
        for card in self.cards_map.values(): card.set_cantidad(0)

    def show_message(self, msg):
        if msg: messagebox.showinfo("Sistema", msg)