# application/viewmodels/historial_vm.py

from data.firestore_service import FirestoreService
from presentation.observable import Observable

class HistorialPedidosViewModel:
    def __init__(self, firestore_service: FirestoreService):
        self.db = firestore_service
        
        # --- Observables ---
        
        # Lista de todos los pedidos (como diccionarios)
        self.lista_pedidos = Observable([])
        
        # Los items del pedido que esté seleccionado en la lista
        self.detalle_pedido_seleccionado = Observable([])
        
        # El ID del pedido seleccionado (para saber cuál borrar)
        self.selected_pedido_id = None
        
        # Mensajes para la vista
        self.mensaje = Observable("")

    def cargar_historial_pedidos(self):
        """Carga todos los pedidos desde Firestore."""
        try:
            pedidos = self.db.get_all_pedidos_with_ids()
            self.lista_pedidos.value = pedidos
            
            # Limpiar la selección anterior
            self.detalle_pedido_seleccionado.value = []
            self.selected_pedido_id = None
            
        except Exception as e:
            self.mensaje.value = f"Error al cargar historial: {e}"

    def seleccionar_pedido_por_indice(self, idx: int):
        """
        Llamado por la vista cuando el usuario hace clic en un pedido de la lista.
        """
        try:
            pedido_seleccionado = self.lista_pedidos.value[idx]
            
            self.selected_pedido_id = pedido_seleccionado.get("id")
            
            # Actualizar la lista de detalles
            items = pedido_seleccionado.get("items", [])
            self.detalle_pedido_seleccionado.value = items
            
        except IndexError:
            # El usuario hizo clic en un espacio vacío
            self.detalle_pedido_seleccionado.value = []
            self.selected_pedido_id = None
        except Exception as e:
            self.mensaje.value = f"Error al seleccionar pedido: {e}"

    def eliminar_pedido_seleccionado(self):
        """Elimina el pedido que está actualmente seleccionado."""
        if not self.selected_pedido_id:
            self.mensaje.value = "Por favor, seleccione un pedido para eliminar."
            return

        try:
            # Pedir al servicio que lo borre
            self.db.delete_pedido(self.selected_pedido_id)
            
            self.mensaje.value = f"Pedido {self.selected_pedido_id} eliminado con éxito."
            
            # Importante: Volver a cargar la lista para que desaparezca
            self.cargar_historial_pedidos()
            
        except Exception as e:
            self.mensaje.value = f"Error al eliminar el pedido: {e}"