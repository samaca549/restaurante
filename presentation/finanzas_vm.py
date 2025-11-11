import threading
from .observable import Observable
from data.firestore_service import FirestoreService
from data.gemini_service import GeminiService
from typing import Dict, Any

class FinanzasViewModel:
    """ViewModel para la vista de Finanzas, manejando reportes y consultas a Gemini."""
    def __init__(self, firestore_service: FirestoreService, gemini_service: GeminiService):
        self.fs = firestore_service
        self.gemini = gemini_service
        
        # --- Observables para la UI ---
        # Estos atributos son usados por FinanzasView para suscribirse.
        self.reporte_finanzas = Observable({}) # Dict[str, Any]
        self.mensaje = Observable("Listo.")
        self.gemini_respuesta = Observable("Esperando consulta...") # Este era el atributo faltante/no reconocido.
        
    # --- Métodos de Reporte Financiero Clásico (Usa dummy data del servicio) ---
    def _calcular_reporte(self) -> Dict[str, Any]:
        """Calcula el reporte de ventas (síncrono)."""
        pedidos = self.fs.get_all_pedidos() 
        
        total_pedidos = len(pedidos)
        ingreso_bruto = sum(p.get("total", 0.0) for p in pedidos)
        ingreso_promedio = ingreso_bruto / total_pedidos if total_pedidos > 0 else 0.0
        
        return {
            "total_pedidos": total_pedidos,
            "ingreso_bruto": ingreso_bruto,
            "ingreso_promedio": ingreso_promedio
        }

    def generar_reporte(self):
        """Inicia el cálculo del reporte en un hilo para no bloquear la UI."""
        def run_report():
            self.mensaje.value = "Calculando reporte financiero..."
            reporte = self._calcular_reporte()
            self.reporte_finanzas.value = reporte
            self.mensaje.value = "Reporte financiero generado."
        
        threading.Thread(target=run_report).start()

    # --- Métodos de Análisis de IA (Gemini) ---
    def _run_gemini_query(self, prompt: str):
        """Ejecuta la consulta a Gemini (bloqueante) y actualiza la respuesta."""
        try:
            # 1. Obtener la data relevante (ventas e inventario)
            conteo_platos, datos_ventas_str = self.gemini._obtener_datos_conteo_platos()
            items_inventario_list = self.fs.get_inventario()
            
            datos_inventario_str = "\n".join([f"- {item.nombre}: {item.cantidad} {item.unidad}" for item in items_inventario_list])

            # 2. Enmarcar el prompt con la data como contexto para la IA
            contexto = f"""
            Eres un asistente de análisis para un restaurante. Tienes acceso a los siguientes datos:
            --- DATOS DE VENTAS ---
            {datos_ventas_str or 'No hay datos de ventas disponibles.'}
            --- DATOS DE INVENTARIO ---
            {datos_inventario_str or 'No hay datos de inventario disponibles.'}
            --- FIN DE DATOS ---

            Por favor, responde concisa y profesionalmente a la siguiente pregunta del usuario, usando solo los datos proporcionados: '{prompt}'
            """
            
            # 3. Llamar al servicio Gemini (Bloqueante)
            respuesta = self.gemini._generar_respuesta(contexto)

            # 4. Actualizar el Observable
            self.gemini_respuesta.value = respuesta
            self.mensaje.value = "Consulta de IA finalizada."
            
        except Exception as e:
            self.gemini_respuesta.value = f"Ocurrió un error en el análisis de IA: {e}"
            self.mensaje.value = "Error en la consulta de IA."

    def ask_gemini_question(self, prompt: str):
        """Lanza la consulta a Gemini en un hilo separado para no congelar la UI."""
        self.mensaje.value = "Consultando a Gemini..."
        threading.Thread(target=self._run_gemini_query, args=(prompt,)).start()