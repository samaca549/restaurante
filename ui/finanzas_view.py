import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ======================================================
# COMPONENTE 1: TARJETA DE MÉTRICA (KPI CARD)
# ======================================================
class MetricCard(tk.Frame):
    def __init__(self, parent, title, icon, value="...", subtext="Actualizado", bg_color="#FFFFFF", text_color="#333"):
        super().__init__(parent, bg=bg_color, bd=0, highlightthickness=1, highlightbackground="#E0E0E0", relief="flat")
        self.pack_propagate(False)
        
        self.inner = tk.Frame(self, bg=bg_color)
        self.inner.pack(padx=2, pady=2, fill="both", expand=True)
        
        f_top = tk.Frame(self.inner, bg=bg_color)
        f_top.pack(fill="x", padx=15, pady=(15, 5))
        
        tk.Label(f_top, text=icon, font=("Segoe UI Emoji", 18), bg=bg_color, fg=text_color).pack(side="left")
        tk.Label(f_top, text=title.upper(), font=("Segoe UI", 9, "bold"), bg=bg_color, fg="#757575").pack(side="left", padx=10)
        
        self.lbl_value = tk.Label(self.inner, text=value, font=("Segoe UI", 24, "bold"), bg=bg_color, fg=text_color)
        self.lbl_value.pack(anchor="w", padx=15)
        
        self.lbl_sub = tk.Label(self.inner, text=subtext, font=("Segoe UI", 8), bg=bg_color, fg="#9E9E9E")
        self.lbl_sub.pack(anchor="w", padx=15, pady=(0, 15))
        
        self.bind("<Enter>", lambda e: self.config(highlightbackground="#BDBDBD"))
        self.bind("<Leave>", lambda e: self.config(highlightbackground="#E0E0E0"))

    def set_value(self, value):
        self.lbl_value.config(text=str(value))

# ======================================================
# COMPONENTE 2: WIDGET DE INSIGHT IA
# ======================================================
class InsightWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#311B92", bd=0, relief="flat")
        
        f_in = tk.Frame(self, bg="#311B92")
        f_in.pack(fill="both", expand=True, padx=20, pady=15)
        
        f_head = tk.Frame(f_in, bg="#311B92")
        f_head.pack(fill="x")
        tk.Label(f_head, text=" IA STRATEGIC INSIGHT", fg="#B388FF", bg="#311B92", font=("Segoe UI", 9, "bold")).pack(side="left")
        
        self.lbl_icon = tk.Label(f_in, text="💡", font=("Segoe UI Emoji", 28), bg="#311B92", fg="white")
        self.lbl_icon.pack(side="left", padx=(0, 15))
        
        # Ajustamos wraplength para responsividad
        self.lbl_text = tk.Label(f_in, text="Analizando patrones de venta...", 
                                 font=("Segoe UI", 14, "italic"), bg="#311B92", fg="white", 
                                 wraplength=900, justify="left", anchor="w")
        self.lbl_text.pack(side="left", fill="both", expand=True)

    def update_insight(self, tipo, texto):
        iconos = {
            "ALERTA": "⚠️", "EXITO": "🚀",
            "CONSEJO": "💡", "INFO": "ℹ️", "TENDENCIA": "📈"
        }
        icono = iconos.get(str(tipo).upper(), "✨")
        self.lbl_icon.config(text=icono)
        self.lbl_text.config(text=str(texto))
        self.lbl_text.config(fg="#311B92") 
        self.after(100, lambda: self.lbl_text.config(fg="white"))

# ======================================================
# VISTA PRINCIPAL - FINANZAS VIEW
# ======================================================
class FinanzasView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.vm = controller.get_vm("finanzas_vm")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Bg.TFrame", background="#F5F7FA")
        self.configure(style="Bg.TFrame")
        
        # --- HEADER (Fijo arriba) ---
        f_header = tk.Frame(self, bg="white", height=60, bd=1, relief="flat", highlightthickness=1, highlightbackground="#E0E0E0")
        f_header.pack(fill="x", side="top")
        f_header.pack_propagate(False)
        
        tk.Button(f_header, text="⬅ Volver", command=lambda: controller.show_frame("HomeView"),
                  bg="white", bd=0, font=("Segoe UI", 10), cursor="hand2").pack(side="left", padx=10)
        tk.Label(f_header, text="Dashboard Financiero", font=("Segoe UI", 16, "bold"), bg="white", fg="#263238").pack(side="left", padx=10)
        
        self.period_var = tk.StringVar(value="Mes Actual")
        ttk.Combobox(f_header, textvariable=self.period_var, values=["Mes Actual", "Última Semana", "Año Completo"], state="readonly").pack(side="right", padx=10)
        self.period_var.trace("w", lambda *args: self.vm.generar_reporte(self.period_var.get()))

        # --- SCROLLABLE CONTENT (RESPONSIVO - SIN HUECOS) ---
        canvas = tk.Canvas(self, bg="#F5F7FA", borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        self.main_container = tk.Frame(canvas, bg="#F5F7FA")
        
        # 1. Crear ventana en el canvas
        self.canvas_window = canvas.create_window((0, 0), window=self.main_container, anchor="nw")

        # 2. Configurar scrollregion al cambiar tamaño interno
        self.main_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # 3. TRUCO DE RESPONSIVIDAD: Ajustar el ancho de la ventana interna al ancho del canvas
        def _configure_canvas(event):
            canvas.itemconfig(self.canvas_window, width=event.width)
        
        canvas.bind("<Configure>", _configure_canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- WIDGETS INTERNOS ---
        
        # 1. WIDGET IA
        self.insight_widget = InsightWidget(self.main_container)
        self.insight_widget.pack(fill="x", pady=(20, 20), padx=20)
        
        # 2. KPIS
        f_kpi = tk.Frame(self.main_container, bg="#F5F7FA")
        f_kpi.pack(fill="x", pady=(0, 20), padx=20)
        # Configurar grid weights para que las tarjetas se estiren y llenen el ancho
        for i in range(4): f_kpi.columnconfigure(i, weight=1)
        
        self.card_ingreso = MetricCard(f_kpi, "Ingresos Brutos", "💰")
        self.card_ingreso.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.card_neto = MetricCard(f_kpi, "Ganancia Neta", "📈", bg_color="#E8F5E9")
        self.card_neto.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        self.card_pedidos = MetricCard(f_kpi, "Total Pedidos", "🧾")
        self.card_pedidos.grid(row=0, column=2, sticky="ew", padx=10, pady=5)
        self.card_ticket = MetricCard(f_kpi, "Ticket Promedio", "📊")
        self.card_ticket.grid(row=0, column=3, sticky="ew", padx=10, pady=5)
        
        # 3. GRÁFICOS
        f_charts = tk.Frame(self.main_container, bg="#F5F7FA")
        f_charts.pack(fill="x", pady=20, padx=20)
        f_charts.columnconfigure(0, weight=3) # El de línea es un poco más ancho
        f_charts.columnconfigure(1, weight=2)
        
        # Línea (Area)
        self.fig_line = Figure(figsize=(5, 4), dpi=100)
        self.fig_line.patch.set_facecolor('#F5F7FA')
        self.ax_line = self.fig_line.add_subplot(111)
        
        f_chart_line = tk.Frame(f_charts, bg="white", bd=1, relief="flat")
        f_chart_line.grid(row=0, column=0, sticky="nsew", padx=10)
        self.canvas_line = FigureCanvasTkAgg(self.fig_line, master=f_chart_line)
        self.canvas_line.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pie (Donut)
        self.fig_pie = Figure(figsize=(4, 4), dpi=100)
        self.fig_pie.patch.set_facecolor('#F5F7FA')
        self.ax_pie = self.fig_pie.add_subplot(111)
        
        f_chart_pie = tk.Frame(f_charts, bg="white", bd=1, relief="flat")
        f_chart_pie.grid(row=0, column=1, sticky="nsew", padx=10)
        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, master=f_chart_pie)
        self.canvas_pie.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # 4. TABLA
        f_table = ttk.LabelFrame(self.main_container, text="Historial Reciente", padding=10)
        f_table.pack(fill="x", pady=20, padx=20)
        
        cols = ("Fecha", "ID", "Cliente", "Total", "Ganancia")
        self.tree_trans = ttk.Treeview(f_table, columns=cols, show="headings", height=8)
        for col in cols: self.tree_trans.heading(col, text=col)
        self.tree_trans.column("ID", width=60)
        self.tree_trans.pack(fill="both", expand=True)
        
        # 5. CHAT
        f_chat = ttk.LabelFrame(self.main_container, text="Asistente IA", padding=10)
        f_chat.pack(fill="x", pady=20, padx=20)
        
        self.txt_chat = scrolledtext.ScrolledText(f_chat, state='disabled', height=5, font=("Segoe UI", 10))
        self.txt_chat.pack(fill="both", expand=True)
        
        f_input = tk.Frame(f_chat)
        f_input.pack(fill="x", pady=5)
        self.ent_prompt = ttk.Entry(f_input)
        self.ent_prompt.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.ent_prompt.bind("<Return>", lambda e: self.on_ask())
        
        self.btn_send = tk.Button(f_input, text="ENVIAR", command=self.on_ask, bg="#2196F3", fg="white", bd=0)
        self.btn_send.pack(side="right")
        
        # Etiqueta de estado para la IA
        self.lbl_ia_status = tk.Label(f_input, text="", fg="#FF9800", font=("Segoe UI", 8, "italic"))
        self.lbl_ia_status.pack(side="right", padx=5)

        # SUSCRIPCIONES (Wrappers seguros para Hilos)
        self.vm.reporte_finanzas.subscribe(lambda d: self.after(0, lambda: self.update_kpis(d)))
        self.vm.transacciones.subscribe(lambda d: self.after(0, lambda: self.update_transacciones(d)))
        self.vm.graficos_data.subscribe(lambda d: self.after(0, lambda: self.update_graficos(d)))
        self.vm.gemini_respuesta.subscribe(lambda d: self.after(0, lambda: self.update_chat(d)))
        self.vm.insight_flash.subscribe(lambda d: self.after(0, lambda: self.update_insight_widget(d)))
        
        self.after(1000, self._ciclo_insights_automaticos)

    def on_show(self):
        self.vm.generar_reporte_completo()

    def _ciclo_insights_automaticos(self):
        self.vm.obtener_insight_automatico()
        self.after(60000, self._ciclo_insights_automaticos)

    # --- UI UPDATE ---
    def update_kpis(self, data):
        if not data: return
        try:
            self.card_ingreso.set_value(f"${data.get('ingreso_bruto', 0):,.0f}")
            self.card_neto.set_value(f"${data.get('ganancia_neta', 0):,.0f}")
            self.card_pedidos.set_value(str(data.get('total_pedidos', 0)))
            self.card_ticket.set_value(f"${data.get('ingreso_promedio', 0):,.0f}")
        except: pass

    def update_transacciones(self, transacciones):
        for i in self.tree_trans.get_children(): self.tree_trans.delete(i)
        if not transacciones: return
        for trans in transacciones:
            try:
                self.tree_trans.insert("", "end", values=(
                    trans.get("fecha", "-"), trans.get("pedido_id", "-"), trans.get("cliente", "-"),
                    f"${trans.get('total', 0):,.0f}", f"${trans.get('ganancia', 0):,.0f}"
                ))
            except: pass

    def update_graficos(self, data):
        if not data: return
        try:
            # 1. AREA CHART
            fechas = data.get("tendencias_fechas", [])
            ventas = data.get("tendencias_ventas", [])
            self.ax_line.clear()
            
            if fechas and len(fechas) == len(ventas):
                color = "#1976D2"
                self.ax_line.plot(fechas, ventas, color=color, linewidth=2, marker='o', markersize=4)
                self.ax_line.fill_between(fechas, ventas, color=color, alpha=0.1)
                self.ax_line.set_title("Ventas Recientes", fontsize=10, fontweight='bold', color="#555")
                self.ax_line.grid(True, linestyle='--', alpha=0.5)
                self.ax_line.spines['top'].set_visible(False)
                self.ax_line.spines['right'].set_visible(False)
                self.ax_line.tick_params(axis='x', rotation=30, labelsize=8)
            else:
                self.ax_line.text(0.5, 0.5, "Sin datos", ha='center')
            self.canvas_line.draw()
            
            # 2. DONUT CHART (ARREGLADO Y SEGURO)
            productos = data.get("top_productos_nombres", [])
            cantidades = data.get("top_productos_cant", [])
            self.ax_pie.clear()
            
            if productos and len(productos) == len(cantidades):
                colores = ["#42A5F5", "#66BB6A", "#FFA726", "#EF5350", "#AB47BC"]
                
                # CORRECCIÓN: Guardamos todo en 'resultados' para evitar errores del linter
                resultados = self.ax_pie.pie(
                    cantidades, 
                    autopct='%1.0f%%', 
                    pctdistance=0.80,
                    colors=colores,
                    wedgeprops=dict(width=0.4, edgecolor='white')
                )
                
                # El primer elemento siempre son los 'wedges' para la leyenda
                wedges = resultados[0]
                
                # Opcional: Cambiar color de textos de porcentaje si existen (indice 2)
                if len(resultados) > 2:
                    for text in resultados[2]:
                        text.set_color('white')
                        text.set_fontsize(9)
                
                self.ax_pie.set_title("Top Productos", fontsize=10, fontweight='bold', color="#555")
                self.ax_pie.legend(wedges, productos, loc="center left", bbox_to_anchor=(0.9, 0, 0.5, 1), frameon=False, fontsize=8)
            else:
                self.ax_pie.text(0.5, 0.5, "Sin datos", ha='center')
            self.canvas_pie.draw()
            
        except Exception as e:
            print(f"Error Gráficos: {e}")

    def on_ask(self):
        prompt = self.ent_prompt.get().strip()
        if prompt:
            self.txt_chat.config(state='normal')
            self.txt_chat.insert(tk.END, f"Tú: {prompt}\n")
            self.txt_chat.config(state='disabled')
            self.ent_prompt.delete(0, 'end')
            
            # Feedback visual
            self.lbl_ia_status.config(text="IA pensando... ")
            self.btn_send.config(state="disabled")
            
            self.vm.ask_gemini_question(prompt)

    def update_chat(self, msg):
        self.txt_chat.config(state='normal')
        self.txt_chat.insert(tk.END, f"IA: {msg}\n\n")
        self.txt_chat.see(tk.END)
        self.txt_chat.config(state='disabled')
        
        # Quitar feedback
        self.lbl_ia_status.config(text="")
        self.btn_send.config(state="normal")

    def update_insight_widget(self, data):
        if data:
            try:
                tipo, texto = data
                self.insight_widget.update_insight(tipo, texto)
            except: pass
