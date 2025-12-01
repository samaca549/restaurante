import os
import sys

# --- IMPORTACIÓN SEGURA DE LA LIBRERÍA ---
try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
except ImportError:
    print(" ERROR: La librería google-generativeai no está instalada.")
    genai = None
    GenerationConfig = None

# Asumiendo que esta es una clase disponible
from data.firestore_service import FirestoreService

class GeminiService:
    # Modelo recomendado por velocidad y costo
    DEFAULT_MODEL = "gemini-2.0-flash" 

    def __init__(self, firestore_service: FirestoreService):
        self.fs = firestore_service
        self.model = None

        # 1. Obtener API Key de las variables de entorno
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key or not genai:
            print(" ADVERTENCIA: 'GEMINI_API_KEY' no encontrada o librería faltante.")
        else:
            try:
                # 2. Configuración
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(self.DEFAULT_MODEL)
                print(f"Gemini conectado correctamente: {self.DEFAULT_MODEL}")
            except Exception as e:
                print(f" Error al conectar con Gemini: {e}")
                self.model = None

    # ------------------------------------------
    # UTILIDAD INTERNA
    # ------------------------------------------
    def _generar_respuesta(self, prompt: str) -> str:
        if not self.model:
            return "Servicio de IA no disponible (Verifica tu API KEY)."

        try:
            # Llamada a la API con configuración para respuestas más creativas pero precisas
            config = GenerationConfig(temperature=0.7)
            response = self.model.generate_content(prompt, generation_config=config)
            
            # Mejor manejo de posibles respuestas vacías o con seguridad bloqueada
            if response and response.text:
                return response.text.strip()
            
            # Manejo de casos de bloqueo (si fuera necesario)
            if response and response.prompt_feedback and response.prompt_feedback.block_reason:
                return f"La respuesta fue bloqueada por seguridad: {response.prompt_feedback.block_reason.name}"
                
            return "La IA no generó una respuesta de texto."
        except Exception as e:
            # Se imprime el error completo para depuración, pero se devuelve un mensaje genérico
            print(f" Error en generación: {e}")
            return "Ocurrió un error al consultar a la IA."

    # --- Se omiten los métodos de datos (1. y 1.5) ya que no requieren cambios ---
    def _obtener_datos_conteo_platos(self):
        """Procesa pedidos para obtener estadísticas simples."""
        try:
            pedidos = self.fs.get_all_pedidos()
            if not pedidos: return {}, "No hay pedidos registrados."

            conteo = {}
            total_dinero = 0

            for pedido in pedidos:
                # Se mantiene la lógica de extracción segura
                total = pedido.get("total", 0) if isinstance(pedido, dict) else getattr(pedido, "total", 0)
                total_dinero += total
                
                items = pedido.get("items", []) if isinstance(pedido, dict) else getattr(pedido, "items", [])
                for item in items:
                    nombre = item.get("nombre", "Desconocido") if isinstance(item, dict) else getattr(item, "nombre", "Desconocido")
                    cantidad = item.get("cantidad", 0) if isinstance(item, dict) else getattr(item, "cantidad", 0)
                    conteo[nombre] = conteo.get(nombre, 0) + cantidad

            detalles = "\n".join([f"- {n}: {c} unid." for n, c in conteo.items()])
            resumen = f"Ventas Totales: ${total_dinero:,.0f}\nDesglose:\n{detalles}"
            return conteo, resumen
        except Exception as e:
            print(f" Error procesando pedidos: {e}")
            return {}, "Error al procesar datos."

    def obtener_contexto_financiero_completo(self):
        """Prepara un resumen detallado con FECHAS y ITEMS individuales para el análisis de la IA."""
        try:
            pedidos = self.fs.get_all_pedidos()
            if not pedidos: return "No hay historial de ventas disponible."

            lineas = ["--- HISTORIAL DE TRANSACCIONES DETALLADO ---"]
            lineas.append("FORMATO: FECHA | ID | TOTAL | ITEMS")
            
            total_global = 0
            
            for p in pedidos:
                # Extracción segura (dict o objeto)
                if isinstance(p, dict):
                    fecha = p.get("fecha", "N/A")
                    pid = str(p.get("id", "??"))[-4:]
                    total = p.get("total", 0)
                    items_list = p.get("items", [])
                else:
                    fecha = getattr(p, "fecha", "N/A")
                    pid = str(getattr(p, "id", "??"))[-4:]
                    total = getattr(p, "total", 0)
                    items_list = getattr(p, "items", [])
                
                total_global += total
                
                items_str = ", ".join([
                    f"{i.get('nombre')}({i.get('cantidad')})" 
                    if isinstance(i, dict) else f"{getattr(i, 'nombre')}({getattr(i, 'cantidad')})"
                    for i in items_list
                ])
                
                lineas.append(f"{fecha} | {pid} | ${total} | {items_str}")

            lineas.append(f"RESUMEN FINAL: Ventas Totales acumuladas: ${total_global}")
            return "\n".join(lineas)

        except Exception as e:
            print(f"Error generando contexto: {e}")
            return f"Error leyendo datos: {e}"

    # ---------------------------------------------------------
    # 2. RECOMENDACIÓN DE MENÚ (FLASH - CORREGIDO Y MEJORADO)
    # ---------------------------------------------------------
    def obtener_recomendacion_flash(self, lista_platos):
        """Genera una recomendación de neuromarketing para un plato específico."""
        if not lista_platos: 
            return None, "Sin menú disponible."

        nombres = ", ".join([p.nombre for p in lista_platos])

        # Se mejora el prompt para ser más directo con el formato
        prompt = f"""
        Eres un experto en Neuromarketing Gastronómico.
        Menú disponible: [{nombres}].

        Tu misión:
        1. Elige el plato que genere más deseo impulsivo.
        2. Crea una frase corta, sensorial y persuasiva (máx 10 palabras).
        3. FORMATO OBLIGATORIO Y ÚNICO: NOMBRE_DEL_PLATO|FRASE
        
        Ejemplo: Hamburguesa Doble|¡Jugosa, gigante y llena de queso, pídela ya!
        """

        res = self._generar_respuesta(prompt)

        # Se asegura que la respuesta devuelta a la UI sea limpia y en el formato esperado
        if "|" in res:
            try:
                # Separar solo una vez para evitar problemas si la frase tiene un '|'
                n, f = res.split("|", 1) 
                return n.strip(), f.strip()
            except ValueError: 
                pass # Si falla el split, se usa el manejo por defecto

        # Manejo por defecto/fallback si la IA no sigue el formato
        nombre_default = lista_platos[0].nombre if lista_platos else "Plato"
        # Devuelve el texto generado como frase, eliminando cualquier | residual
        return nombre_default, res.replace("|", " ") 

    # --- Se omiten los demás métodos (3. a 6.) ya que no requieren cambios estructurales ---
    def pedir_recomendacion_ventas(self) -> str:
        _, datos = self._obtener_datos_conteo_platos()
        prompt = f"""
        Actúa como Gerente Comercial Senior.
        Datos de ventas actuales:
        {datos}
        
        Dame una estrategia de guerrilla marketing (máximo 1 párrafo) para duplicar estas ventas HOY.
        Sé agresivo y práctico.
        """
        return self._generar_respuesta(prompt)

    # ---------------------------------------------------------
    # 4. STOCK CRÍTICO (MODIFICADO CON BENCHMARKS Y COMPARACIÓN)
    # ---------------------------------------------------------
    def obtener_recomendacion_inventario(self, lista_items):
        if not lista_items: return None, "Inventario vacío."

        items_str = ", ".join(f"{i.nombre} ({i.cantidad} {i.unidad})" for i in lista_items)

        prompt = f"""
        Eres Jefe de Logística. Insumos actuales: [{items_str}].
        
        USA ESTA TABLA DE REFERENCIA DE STOCK IDEAL (MÍNIMO SEGURO):
        - Carne/Hamburguesa/Proteínas: 100 unidades (o 15 kg)
        - Panes: 100 unidades
        - Quesos/Lácteos: 5 kg (o 20 unidades si es por loncha)
        - Verduras (Tomate, Lechuga, Cebolla): 10 kg o 15 unidades (mazos/cabezas)
        - Salsas/Líquidos: 5 Litros
        - Insumos secos/Especias: 1 kg
        
        INSTRUCCIONES DE ANÁLISIS:
        1. Si un producto NO está explícitamente en la lista de referencia, COMPÁRALO con el producto más similar (ej: si ves 'Hamburguesa Vegana', usa el estándar de 'Carne/Hamburguesa').
        2. Ten mucho cuidado con las UNIDADES: no confundas Kg con Unidades (100 gramos es crítico, 100 kg es mucho).
        3. Identifica el insumo MÁS crítico basándote en la distancia negativa respecto a su ideal.
        4. Escribe una alerta de pánico corta (max 15 palabras).
        5. FORMATO OBLIGATORIO: NOMBRE_INSUMO|ALERTA
        """

        res = self._generar_respuesta(prompt)

        if "|" in res:
            try:
                n, f = res.split("|", 1)
                return n.strip(), f.strip()
            except ValueError: pass

        min_item = min(lista_items, key=lambda x: x.cantidad)
        return min_item.nombre, res

    # ---------------------------------------------------------
    # 5. ANÁLISIS GENERAL INVENTARIO (MODIFICADO)
    # ---------------------------------------------------------
    def analizar_inventario_bajo(self):
        try:
            inventario = self.fs.get_inventario()
            if not inventario: return "No hay datos de inventario."

            items = "\n".join([f"- {i.nombre}: {i.cantidad} {i.unidad}" for i in inventario])

            prompt = f"""
            Actúa como Auditor de Inventarios. Analiza esta lista actual:
            {items}
            
            USA ESTOS PARÁMETROS DE STOCK SALUDABLE PARA TU JUICIO:
            - Carnes/Hamburguesas: Ideal 100 unid.
            - Pan: Ideal 100 unid.
            - Queso: Ideal 5 kg.
            - Verduras (Lechuga/Tomate): Ideal 10 kg o 15 unidades.
            - Bebidas/Otros: Ideal 50 unid.

            REGLA DE ORO: 
            Si aparece un producto nuevo o desconocido, asócialo a la categoría más cercana de la lista anterior para juzgar si su stock es bajo o alto.
            
            Detecta ineficiencias y riesgos de quiebre. Sé conciso (máximo 4 líneas). 
            Presta atención estricta a las unidades (Kg vs Unid vs Litros) para no generar alertas falsas.
            """
            return self._generar_respuesta(prompt)
        except Exception as e:
            return f"Error al leer inventario: {e}"

    def obtener_consejo_productivo(self):
        """Genera un consejo de gestión para el restaurante."""
        try:
            prompt = """
            Actúa como un Coach de Negocios Gastronómicos exitoso.
            Dame UN SOLO consejo corto, práctico y de alto impacto para el gerente hoy.
            Temas: Liderazgo, Ventas, Eficiencia o Calidad.
            
            Reglas:
            - Máximo 15 palabras.
            - Tono motivador e imperativo.
            - Sin saludos.
            """
            return self._generar_respuesta(prompt)
            
        except Exception as e:
            print(f"Error IA consejo: {e}")
            return "Reúne al equipo para mejorar la comunicación."