import os
import google.generativeai as genai
from data.firestore_service import FirestoreService

class GeminiService:
    # Cambiamos el modelo por defecto a 'gemini-2.5-flash' para optimizar costos
    DEFAULT_MODEL = 'gemini-2.5-flash' 
    
    def __init__(self, firestore_service: FirestoreService):
        self.fs = firestore_service
        self.model = None
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY no encontrada en .env")
            
            genai.configure(api_key=api_key)
            # Usamos el modelo Flash como modelo principal
            self.model = genai.GenerativeModel(self.DEFAULT_MODEL) 
            print(f"Servicio de IA ({self.DEFAULT_MODEL}) configurado.")
            
        except Exception as e:
            print(f"Advertencia: No se pudo iniciar Gemini. {e}")
            self.model = None

    def _generar_respuesta(self, prompt: str) -> str:
        if not self.model:
            return "El servicio de IA no está disponible."
        try:
            # Reutiliza el modelo configurado (ahora Flash)
            response = self.model.generate_content(prompt) 
            return response.text
        except Exception as e:
            return f"Error al contactar a Gemini: {e}"

    def _obtener_datos_conteo_platos(self) -> tuple[dict, str]:
        """Función auxiliar para obtener y formatear los datos de ventas."""
        pedidos_data = self.fs.get_all_pedidos()
        if not pedidos_data:
            return {}, "No hay pedidos para analizar."

        conteo_platos = {}
        for pedido in pedidos_data:
            for item in pedido.get("items", []):
                nombre = item.get("nombre")
                cantidad = item.get("cantidad", 0)
                conteo_platos[nombre] = conteo_platos.get(nombre, 0) + cantidad
        
        datos_str = "\n".join([f"- {nombre}: {qty} vendidos" for nombre, qty in conteo_platos.items()])
        return conteo_platos, datos_str

    def analizar_plato_mas_vendido(self) -> str:
        conteo_platos, datos_str = self._obtener_datos_conteo_platos()
        if not conteo_platos:
            return datos_str

        prompt = f"""
        Eres un analista de negocios de restaurante.
        Basado en el siguiente conteo de platos vendidos:
        {datos_str}
        
        Por favor, responde:
        1. ¿Cuál es el plato más vendido?
        2. ¿Cuál es el plato menos vendido?
        3. Dame una recomendación corta basada en esta información.
        """
        return self._generar_respuesta(prompt)

    # NUEVO MÉTODO PARA RECOMENDACIONES DE VENTA
    def pedir_recomendacion_ventas(self) -> str:
        """
        Pide a la IA recomendaciones estratégicas para mejorar las ventas, 
        basadas en los datos actuales.
        """
        conteo_platos, datos_str = self._obtener_datos_conteo_platos()
        if not conteo_platos:
            return datos_str

        # Identificamos el más y menos vendido para dar contexto al modelo
        mas_vendido = max(conteo_platos, key=conteo_platos.get)
        menos_vendido = min(conteo_platos, key=conteo_platos.get)
        
        prompt = f"""
        Eres un estratega de marketing y ventas para un restaurante.
        El plato más vendido es '{mas_vendido}'.
        El plato menos vendido es '{menos_vendido}'.
        Los datos completos de ventas son:
        {datos_str}
        
        Tu objetivo es generar una estrategia simple y práctica para aumentar las ventas totales del restaurante.
        1. Propón una promoción creativa que use el plato más vendido como gancho.
        2. Sugiere una acción para impulsar el plato menos vendido (ej. un bundle o un cambio de nombre).
        3. Da una idea para mejorar la experiencia del cliente que impulse la repetición de compra.
        """
        return self._generar_respuesta(prompt)

    def analizar_inventario_bajo(self) -> str:
        items = self.fs.get_inventario()
        if not items:
            return "No hay items en el inventario."

        # Convertimos los objetos a texto simple
        items_str = "\n".join([f"- {item.nombre}: {item.cantidad} {item.unidad}" for item in items])

        prompt = f"""
        Eres un gerente de inventario.
        Revisa la siguiente lista de inventario:
        {items_str}
        
        Por favor, identifica los items que están bajos (ej. menos de 10 unidades/kg).
        Dame una lista de compras priorizada.
        """
        return self._generar_respuesta(prompt)