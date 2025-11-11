# application/viewmodels/pedidos_vm.py

from domain.models import Plato, Cliente
from domain.restaurante import Pedido
from data.firestore_service import FirestoreService
# Asumiendo que tienes un servicio de IA
# from services.ia_service import IAService 
from data.gemini_service import GeminiService
from presentation.observable import Observable # Importa la clase Observable de arriba

class PedidosViewModel:
    def __init__(self, firestore_service: FirestoreService, ia_service: GeminiService): #, ia_service: IAService):
        
        self.db = firestore_service
        # self.ia = ia_service # Descomenta cuando tengas tu servicio de IA
        
        # --- Estado y Observables ---
        
        # El pedido que se está construyendo activamente
        self.pedido_actual = Observable(None) 
        
        # El cliente asociado a este pedido
        self.cliente_actual = Observable(None)
        
        # La lista de platos disponibles en el menú
        self.platos_menu = Observable([]) 
        
        # Mensajes para mostrar en pop-ups (ej: "Pedido guardado")
        self.mensaje = Observable("")
        
        # Reportes generados por la IA
        self.reporte_ia = Observable("")

    def cargar_platos(self):
        """Carga la lista de platos desde Firestore y actualiza el observable."""
        try:
            platos_list = self.db.get_platos()
            # Ordenar alfabéticamente para la vista
            platos_list.sort(key=lambda p: p.nombre)
            self.platos_menu.value = platos_list
        except Exception as e:
            self.mensaje.value = f"Error al cargar el menú: {e}"

    def iniciar_nuevo_pedido(self, email: str, nombre: str):
        """Busca o crea un cliente y prepara un nuevo pedido vacío."""
        if not email or not nombre:
            self.mensaje.value = "Email y Nombre son requeridos para iniciar."
            return

        try:
            # 1. Obtener o crear el cliente
            cliente = self.db.get_or_create_cliente(email, nombre)
            self.cliente_actual.value = cliente
            
            # 2. Crear un nuevo objeto Pedido (en memoria)
            nuevo_pedido = Pedido(cliente_id=cliente.id)
            
            # 3. Establecer como el pedido activo
            self.pedido_actual.value = nuevo_pedido
            
            self.mensaje.value = f"Pedido iniciado para {cliente.nombre}."
            
        except Exception as e:
            self.mensaje.value = f"Error al iniciar pedido: {e}"
            self.pedido_actual.value = None
            self.cliente_actual.value = None

    def agregar_plato_al_pedido(self, plato: Plato, cantidad: int):
        """Agrega un ítem al pedido actual en memoria."""
        if not self.pedido_actual.value:
            self.mensaje.value = "Error: Inicie un pedido antes de añadir platos."
            return
        
        if cantidad <= 0:
            self.mensaje.value = "Error: La cantidad debe ser mayor a cero."
            return

        try:
            # La lógica de 'agregar_item' está en tu clase Pedido
            self.pedido_actual.value.agregar_item(
                plato_id=plato.id,
                nombre=plato.nombre,
                precio_unitario=plato.precio,
                cantidad=cantidad
            )
            
            # Notificar a la vista que el pedido cambió (para actualizar el total)
            # Asignar el mismo valor fuerza la notificación
            self.pedido_actual.value = self.pedido_actual.value
            
        except Exception as e:
            self.mensaje.value = f"Error al agregar plato: {e}"

    def finalizar_pedido(self):
        """Guarda el pedido actual en Firestore y lo limpia."""
        if not self.pedido_actual.value or not self.pedido_actual.value.items:
            self.mensaje.value = "No hay nada en el pedido para finalizar."
            return
            
        try:
            pedido_a_guardar = self.pedido_actual.value
            
            # 1. Guardar el Pedido en la colección 'pedidos'
            pedido_id = self.db.save_pedido(pedido_a_guardar)
            
            # 2. (Importante) Registrar el ID de este pedido en el historial del cliente
            self.db.add_pedido_to_cliente(
                cliente_id=self.cliente_actual.value.id,
                pedido_id=pedido_id
            )
            
            # 3. (Opcional pero recomendado) Actualizar el inventario
            # self._actualizar_inventario_por_pedido(pedido_a_guardar)

            self.mensaje.value = f"¡Pedido {pedido_id} finalizado y guardado con éxito!"
            
            # 4. Limpiar el estado para el siguiente pedido
            self.pedido_actual.value = None
            self.cliente_actual.value = None
            
        except Exception as e:
            self.mensaje.value = f"Error al finalizar el pedido: {e}"

    def pedir_analisis_ia(self):
        """Llama al servicio de IA para obtener un reporte."""
        self.reporte_ia.value = "Procesando... por favor espere."
        try:
            # 1. Obtener todos los pedidos de la BD
            todos_los_pedidos_dict = self.db.get_all_pedidos()
            
            # 2. (Aquí iría tu servicio de IA)
            # report = self.ia.analizar_platos_mas_vendidos(todos_los_pedidos_dict)
            
            # --- Simulación mientras no hay IA ---
            if not todos_los_pedidos_dict:
                 report = "No hay pedidos para analizar."
            else:
                # Lógica simple de ejemplo:
                contador = {}
                for p in todos_los_pedidos_dict:
                    for item in p.get('items', []):
                        nombre = item.get('nombre')
                        cant = item.get('cantidad')
                        if nombre and cant:
                            contador[nombre] = contador.get(nombre, 0) + cant
                
                if not contador:
                    report = "No se encontraron items en los pedidos."
                else:
                    mas_vendido = max(contador, key=contador.get)
                    report = f"Reporte simple: El plato más vendido es '{mas_vendido}' con {contador[mas_vendido]} unidades."
            # --- Fin Simulación ---

            self.reporte_ia.value = report
            
        except Exception as e:
            self.reporte_ia.value = f"Error al generar reporte: {e}"