from presentation.observable import Observable
from data.firestore_service import FirestoreService
from data.gemini_service import GeminiService
from domain.models import Plato, Cliente
from domain.restaurante import Pedido
from typing import List

class PedidosViewModel:
    def __init__(self, firestore_service: FirestoreService, ia_service: GeminiService):
        self.fs = firestore_service
        self.ia = ia_service
        
        self.platos_menu = Observable([]) # Lista[Plato]
        self.pedido_actual = Observable(None) # Tipo: Pedido
        self.mensaje = Observable(None)
        self.reporte_ia = Observable(None)
        
    def iniciar_nuevo_pedido(self, cliente_email, cliente_nombre):
        """Crea un cliente (o lo obtiene) y un nuevo objeto Pedido."""
        if not cliente_email or not cliente_nombre:
            self.mensaje.value = "Error: Se necesita email y nombre de cliente."
            return
        try:
            cliente = self.fs.get_or_create_cliente(cliente_email, cliente_nombre)
            self.pedido_actual.value = Pedido(cliente=cliente)
            self.mensaje.value = f"Pedido iniciado para {cliente.nombre}."
        except Exception as e:
            self.mensaje.value = f"Error iniciando pedido: {e}"

    def cargar_platos(self):
        try:
            platos = self.fs.get_platos()
            self.platos_menu.value = platos
        except Exception as e:
            self.mensaje.value = f"Error cargando menú: {e}"
            
    def agregar_plato_al_pedido(self, plato: Plato, cantidad: int):
        pedido = self.pedido_actual.value
        if not pedido:
            self.mensaje.value = "Error: Inicie un pedido primero."
            return
        try:
            pedido.agregar_plato(plato, cantidad)
            # Re-asignamos el valor para notificar a los suscriptores
            self.pedido_actual.value = pedido
        except ValueError as e:
            self.mensaje.value = f"Error: {e}"

    def finalizar_pedido(self):
        pedido = self.pedido_actual.value
        if not pedido or not pedido.items:
            self.mensaje.value = "Error: No hay items en el pedido."
            return
            
        try:
            # 1. Guardar el pedido en Firestore
            pedido_id = self.fs.save_pedido(pedido)
            
            # 2. Actualizar el historial del cliente
            self.fs.add_pedido_to_cliente(pedido.cliente.id, pedido_id)
            
            # 3. (Lógica de inventario iría aquí)
            # self.fs.descontar_inventario(pedido.items)
            
            self.mensaje.value = f"Pedido {pedido_id} guardado con éxito. Total: ${pedido.total}"
            self.pedido_actual.value = None # Limpiar pedido
        except Exception as e:
            self.mensaje.value = f"Error finalizando pedido: {e}"

    def pedir_analisis_ia(self):
        self.reporte_ia.value = "Generando reporte de IA..."
        try:
            reporte = self.ia.analizar_plato_mas_vendido()
            self.reporte_ia.value = reporte
        except Exception as e:
            self.reporte_ia.value = f"Error de IA: {e}"