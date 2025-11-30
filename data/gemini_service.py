import os
import sys

# --- IMPORTACIÓN SEGURA DE LA LIBRERÍA ---
try:
    import google.generativeai as genai
except ImportError:
    print(" ERROR: La librería google-generativeai no está instalada.")
    genai = None

from data.firestore_service import FirestoreService

class GeminiService:
    # Modelo recomendado por velocidad y costo
    DEFAULT_MODEL = "gemini-2.5-flash" 

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
            config = genai.GenerationConfig(temperature=0.7)
            response = self.model.generate_content(prompt, generation_config=config)
            
            if response and response.text:
                return response.text.strip()
            return "La IA no generó una respuesta de texto."
        except Exception as e:
            print(f" Error en generación: {e}")
            return "Ocurrió un error al consultar a la IA."

    # -----------------------------
    #   1. DATOS DE PEDIDOS (LEGACY - Se mantiene por compatibilidad)
    # -----------------------------
    def _obtener_datos_conteo_platos(self):
        """Procesa pedidos para obtener estadísticas simples."""
        try:
            pedidos = self.fs.get_all_pedidos()
            if not pedidos: return {}, "No hay pedidos registrados."

            conteo = {}
            total_dinero = 0

            for pedido in pedidos:
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

    # ---------------------------------------------------------
    #   1.5 ANÁLISIS POTENTE (NUEVO): Historial Detallado
    # ---------------------------------------------------------
    def obtener_contexto_financiero_completo(self):
        """
        Prepara un resumen detallado con FECHAS y ITEMS individuales.
        Esto permite a la IA detectar tendencias (ej: 'vendimos más el viernes').
        Se usa en el Chat de Finanzas.
        """
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

    # -----------------------------------------
    #   2. RECOMENDACIÓN DE MENÚ (FLASH - MEJORADO)
    # -----------------------------------------
    def obtener_recomendacion_flash(self, lista_platos):
        if not lista_platos: return None, "Sin menú disponible."

        nombres = ", ".join([p.nombre for p in lista_platos])

        prompt = f"""
        Eres un experto en Neuromarketing Gastronómico.
        Menú disponible: [{nombres}].

        Tu misión:
        1. Elige el plato que genere más deseo impulsivo.
        2. Crea una frase corta, sensorial y persuasiva (máx 10 palabras).
        3. FORMATO OBLIGATORIO: NOMBRE_DEL_PLATO|FRASE
        
        Ejemplo: Hamburguesa Doble|¡Jugosa, gigante y llena de queso, pídela ya!
        """

        res = self._generar_respuesta(prompt)

        if "|" in res:
            try:
                n, f = res.split("|", 1)
                return n.strip(), f.strip()
            except ValueError: pass 
        
        nombre_default = lista_platos[0].nombre if lista_platos else "Plato"
        return nombre_default, res.replace("|", " ")

    # -----------------------------------------
    #   3. ESTRATEGIA DE VENTAS (MEJORADO)
    # -----------------------------------------
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

    # -----------------------------------------
    #   4. STOCK CRÍTICO (MEJORADO)
    # -----------------------------------------
    def obtener_recomendacion_inventario(self, lista_items):
        if not lista_items: return None, "Inventario vacío."

        items_str = ", ".join(f"{i.nombre} ({i.cantidad} {i.unidad})" for i in lista_items)

        prompt = f"""
        Eres Jefe de Logística. Insumos actuales: [{items_str}].
        
        1. Identifica el insumo MÁS crítico que detendría la operación si falta.
        2. Escribe una alerta de pánico corta (max 15 palabras).
        3. FORMATO OBLIGATORIO: NOMBRE_INSUMO|ALERTA
        """

        res = self._generar_respuesta(prompt)

        if "|" in res:
            try:
                n, f = res.split("|", 1)
                return n.strip(), f.strip()
            except ValueError: pass

        min_item = min(lista_items, key=lambda x: x.cantidad)
        return min_item.nombre, res

    # -----------------------------------------
    #   5. ANÁLISIS GENERAL INVENTARIO (MEJORADO)
    # -----------------------------------------
    def analizar_inventario_bajo(self):
        try:
            inventario = self.fs.get_inventario()
            if not inventario: return "No hay datos de inventario."

            items = "\n".join([f"- {i.nombre}: {i.cantidad} {i.unidad}" for i in inventario])

            prompt = f"""
            Actúa como Auditor de Inventarios. Analiza esta lista:
            {items}
            
            Detecta ineficiencias, riesgos de quiebre de stock y sugiere un plan de compras urgente.
            Sé conciso (máximo 4 líneas).
            """
            return self._generar_respuesta(prompt)
        except Exception as e:
            return f"Error al leer inventario: {e}"

    # -----------------------------------------
    #   6. CONSEJO PRODUCTIVO (WIDGET AZUL - MEJORADO)
    # -----------------------------------------
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