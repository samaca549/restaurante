import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Any, Dict

class FinanzasView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.vm = controller.get_vm("finanzas_vm")

        ttk.Label(self, text="Panel de Finanzas y Análisis", font=("Segoe UI", 20, "bold")).pack(pady=10)
        
        f_nav = ttk.Frame(self)
        f_nav.pack(fill="x", padx=10)
        ttk.Button(f_nav, text="< Volver al Menú", 
                   command=lambda: controller.show_frame("HomeView")).pack(side="left")

        # Usamos un Notebook (pestañas) para separar las secciones
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Pestaña 1: Reporte Financiero Clásico ---
        self.f_reporte_clasico = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.f_reporte_clasico, text="Reporte Financiero")
        self._setup_reporte_clasico(self.f_reporte_clasico)

        # --- Pestaña 2: Herramienta de Análisis de IA ---
        self.f_analisis_ia = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.f_analisis_ia, text="Análisis de IA (Gemini)")
        self._setup_analisis_ia(self.f_analisis_ia)

        # Suscribir ViewModels
        self.vm.reporte_finanzas.subscribe(self._update_reporte_clasico)
        self.vm.mensaje.subscribe(lambda m: self.msg_label.config(text=m))
        self.vm.gemini_respuesta.subscribe(self._update_gemini_response)


    def _setup_reporte_clasico(self, parent_frame):
        """Configura la UI del reporte financiero tradicional."""
        
        self.btn_generar = ttk.Button(parent_frame, text="Generar Reporte Financiero", command=self.vm.generar_reporte)
        self.btn_generar.pack(pady=10)
        
        # Mostrar resultados del reporte
        f_reporte = ttk.LabelFrame(parent_frame, text="Métricas Clave", padding=15)
        f_reporte.pack(padx=10, pady=10, fill="x")

        self.reporte_labels = {}
        row = 0
        for key, desc in [("ingreso_bruto", "Ingreso Total"), 
                          ("total_pedidos", "Total Pedidos"), 
                          ("ingreso_promedio", "Ingreso Promedio por Pedido")]:
            ttk.Label(f_reporte, text=f"{desc}:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
            lbl = ttk.Label(f_reporte, text="N/A", font=("Segoe UI", 12, "bold"))
            lbl.grid(row=row, column=1, sticky="e", padx=5, pady=5)
            self.reporte_labels[key] = lbl
            row += 1
            
        self.msg_label = ttk.Label(parent_frame, text="")
        self.msg_label.pack(pady=5)

    def _setup_analisis_ia(self, parent_frame):
        """Configura la UI para preguntas y respuestas a Gemini."""
        
        ttk.Label(parent_frame, text="Pregúntale a Gemini sobre tus datos de ventas o inventario:", font=("Segoe UI", 12)).pack(pady=5, anchor="w")

        # Campo de entrada para la pregunta
        f_input = ttk.Frame(parent_frame)
        f_input.pack(fill="x", pady=10)
        
        self.entry_prompt = ttk.Entry(f_input, width=80)
        self.entry_prompt.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_ask = ttk.Button(f_input, text="Preguntar a Gemini", command=self.ask_gemini_query)
        self.btn_ask.pack(side="right")
        
        # Área para la respuesta
        ttk.Label(parent_frame, text="Respuesta de la IA:", font=("Segoe UI", 10, "bold")).pack(pady=(10, 5), anchor="w")
        self.txt_response = scrolledtext.ScrolledText(parent_frame, wrap=tk.WORD, height=15, width=80, state='disabled')
        self.txt_response.pack(fill="both", expand=True)

    def on_show(self):
        """Se llama al mostrar la vista."""
        # Generar reporte automáticamente al entrar a la vista
        self.vm.generar_reporte() 
        # Si tienes algún estado de IA, podrías inicializarlo aquí también.
    
    def ask_gemini_query(self):
        """Maneja la acción de enviar la pregunta a Gemini."""
        prompt = self.entry_prompt.get().strip()
        if not prompt:
            self.vm.mensaje.value = "Por favor, ingresa una pregunta."
            return
        
        self.vm.mensaje.value = "Consultando a Gemini (esto puede tardar unos segundos)..."
        self.entry_prompt.delete(0, tk.END) # Limpiar el campo
        
        #  Llama al nuevo método en el ViewModel
        self.vm.ask_gemini_question(prompt)
        self.txt_response.config(state='normal')
        self.txt_response.delete(1.0, tk.END)
        self.txt_response.insert(tk.END, "Esperando respuesta...\n")
        self.txt_response.config(state='disabled')


    def _update_gemini_response(self, respuesta: str):
        """Actualiza el área de texto con la respuesta de la IA."""
        self.txt_response.config(state='normal')
        self.txt_response.delete(1.0, tk.END)
        self.txt_response.insert(tk.END, respuesta)
        self.txt_response.config(state='disabled')
        self.vm.mensaje.value = "Consulta de IA finalizada."


    def _update_reporte_clasico(self, reporte: Dict[str, Any]):
        """Actualiza las etiquetas del reporte financiero."""
        if not reporte: return
        
        self.reporte_labels["ingreso_bruto"].config(text=f"${reporte.get('ingreso_bruto', 0.0):,.2f}")
        self.reporte_labels["total_pedidos"].config(text=f"{reporte.get('total_pedidos', 0)}")
        self.reporte_labels["ingreso_promedio"].config(text=f"${reporte.get('ingreso_promedio', 0.0):,.2f}")
