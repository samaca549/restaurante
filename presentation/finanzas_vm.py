import threading
from collections import Counter, defaultdict
from datetime import datetime
from .observable import Observable
from data.firestore_service import FirestoreService
from data.gemini_service import GeminiService

class FinanzasViewModel:
    def __init__(self, firestore_service: FirestoreService, gemini_service: GeminiService):
        self.fs = firestore_service
        self.gemini = gemini_service
        
        # --- Observables (Ahora coinciden con la Vista) ---
        self.reporte_finanzas = Observable({}) 
        self.transacciones = Observable([])      # Faltaba este
        self.graficos_data = Observable({})      # Faltaba este
        
        self.mensaje = Observable("Listo.")
        self.gemini_respuesta = Observable("Esperando consulta...")
        self.insight_flash = Observable(None) 

    # --- Método principal llamado por la Vista ---
    def generar_reporte_completo(self, periodo="Mes Actual"):
        """Genera KPIs, Datos de Gráficos y Tabla de Transacciones"""
        self.mensaje.value = f"Analizando datos ({periodo})..."
        
        def run_report():
            try:
                # 1. Obtener pedidos (Simulado: filtrar por periodo si tuvieras la lógica)
                pedidos = self.fs.get_all_pedidos() 
                
                # --- A. CÁLCULO DE KPIs ---
                total_pedidos = len(pedidos)
                ingreso_bruto = sum(p.get("total", 0.0) for p in pedidos)
                
                # Simulamos costos (ej: 60% del ingreso) y clientes únicos
                costos_totales = ingreso_bruto * 0.60 
                ganancia_neta = ingreso_bruto - costos_totales
                
                # Extraer clientes únicos
                clientes_set = set(p.get("cliente", {}).get("nombre", "Anon") for p in pedidos)
                clientes_unicos = len(clientes_set)

                ingreso_promedio = ingreso_bruto / total_pedidos if total_pedidos > 0 else 0
                tickets = [p.get("total", 0.0) for p in pedidos]
                max_ticket = max(tickets, default=0)
                min_ticket = min(tickets, default=0)

                kpi_data = {
                    "total_pedidos": total_pedidos,
                    "ingreso_bruto": ingreso_bruto,
                    "ganancia_neta": ganancia_neta,
                    "ingreso_promedio": ingreso_promedio,
                    "max_ticket": max_ticket,
                    "min_ticket": min_ticket,
                    "clientes_unicos": clientes_unicos,
                    "costos_totales": costos_totales
                }
                
                # --- B. DATOS PARA LA TABLA (TRANSACCIONES) ---
                lista_transacciones = []
                for p in pedidos[-50:]: # Últimos 50 para no saturar
                    total = p.get("total", 0)
                    costo_estimado = total * 0.6 # Simulado
                    lista_transacciones.append({
                        "fecha": p.get("fecha", "Hoy"), # Asegúrate que tu pedido tenga fecha
                        "pedido_id": str(p.get("id", "???"))[-6:], # ID corto
                        "cliente": p.get("cliente", {}).get("nombre", "General"),
                        "total": total,
                        "costo": costo_estimado,
                        "ganancia": total - costo_estimado
                    })
                
                # --- C. DATOS PARA GRÁFICOS ---
                # 1. Tendencia de Ventas (Agrupar por Fecha)
                ventas_por_fecha = defaultdict(float)
                for p in pedidos:
                    # Asumiendo que p["fecha"] es un string "YYYY-MM-DD..."
                    fecha_raw = p.get("fecha", str(datetime.now().date()))
                    fecha_simple = fecha_raw.split(" ")[0] # Solo YYYY-MM-DD
                    ventas_por_fecha[fecha_simple] += p.get("total", 0)
                
                fechas_ordenadas = sorted(ventas_por_fecha.keys())
                ventas_ordenadas = [ventas_por_fecha[f] for f in fechas_ordenadas]

                # 2. Top Productos (Agrupar items)
                conteo_productos = Counter()
                for p in pedidos:
                    for item in p.get("items", []):
                        nombre = item.get("nombre", "Item")
                        cant = item.get("cantidad", 1)
                        conteo_productos[nombre] += cant
                
                top_5 = conteo_productos.most_common(5) # Top 5
                
                graficos_payload = {
                    "tendencias_fechas": fechas_ordenadas[-7:], # Últimos 7 días
                    "tendencias_ventas": ventas_ordenadas[-7:],
                    "top_productos_nombres": [x[0] for x in top_5],
                    "top_productos_cant": [x[1] for x in top_5]
                }

                # --- ACTUALIZAR OBSERVABLES (UI THREAD SAFE) ---
                self.reporte_finanzas.value = kpi_data
                self.transacciones.value = lista_transacciones
                self.graficos_data.value = graficos_payload
                self.mensaje.value = "Dashboard actualizado."

            except Exception as e:
                print(f"Error generando reporte: {e}")
                self.mensaje.value = "Error al procesar datos."

        threading.Thread(target=run_report).start()

    # --- Método para el Widget Automático (Insight Flash) ---
    def obtener_insight_automatico(self):
        """Genera un consejo estratégico corto basado en datos reales."""
        def run_insight():
            try:
                # 1. Obtener datos crudos
                conteo, texto_ventas = self.gemini._obtener_datos_conteo_platos()
                if not conteo:
                    self.insight_flash.value = ("INFO", "No hay suficientes datos de ventas hoy.")
                    return

                # 2. Prompt específico para formato "TIPO|TEXTO"
                prompt = f"""
                Eres un asesor financiero experto. Analiza estos datos de ventas:
                {texto_ventas}
                
                Genera UN SOLO insight o consejo estratégico MUY BREVE (max 20 palabras).
                Clasifícalo en una de estas categorías: 'ALERTA', 'EXITO', 'CONSEJO'.
                
                Responde ESTRICTAMENTE así: "CATEGORIA|Texto del consejo"
                Ejemplo: "EXITO|La hamburguesa doble lidera las ganancias hoy."
                """
                
                respuesta_raw = self.gemini._generar_respuesta(prompt)
                
                # 3. Procesar respuesta
                if "|" in respuesta_raw:
                    tipo, texto = respuesta_raw.split("|", 1)
                    self.insight_flash.value = (tipo.strip(), texto.strip())
                else:
                    self.insight_flash.value = ("CONSEJO", respuesta_raw)
                    
            except Exception as e:
                print(f"Error insight: {e}")

        threading.Thread(target=run_insight).start()

    # --- Chat con IA (Manual) ---
    def ask_gemini_question(self, prompt: str):
        def run_query():
            try:
                # Contexto completo para preguntas complejas
                conteo, texto_ventas = self.gemini._obtener_datos_conteo_platos()
                contexto = f"Datos Ventas:\n{texto_ventas}"
                
                full_prompt = f"{contexto}\n\nUsuario: {prompt}\nResponde como analista de negocios."
                resp = self.gemini._generar_respuesta(full_prompt)
                self.gemini_respuesta.value = resp
                self.mensaje.value = "Análisis completado."
            except Exception as e:
                self.gemini_respuesta.value = f"Error: {e}"
        
        self.mensaje.value = "Consultando a Gemini..."
        threading.Thread(target=run_query).start()