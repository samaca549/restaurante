from presentation.observable import Observable

class HistorialPedidosViewModel:

    def __init__(self, firestore_service):
        self.db = firestore_service

        self.lista_pedidos = Observable([])
        self.detalle_pedido_seleccionado = Observable([])
        self.mensaje = Observable("")

        self.selected_pedido_id = None

    # ----------------------------
    # CARGAR PEDIDOS
    # ----------------------------
    def cargar_historial_pedidos(self):
        try:
            pedidos = self.db.get_all_pedidos_with_ids()
            self.lista_pedidos.value = pedidos
            self.detalle_pedido_seleccionado.value = []
            self.selected_pedido_id = None
        except Exception as e:
            self.mensaje.value = f"Error cargando historial: {e}"

    # ----------------------------
    # SELECCIONAR POR ID
    # ----------------------------
    def seleccionar_pedido(self, pedido_id: str):
        try:
            pedido = self.db.get_pedido_by_id(pedido_id)
            if not pedido:
                self.mensaje.value = "Pedido no encontrado."
                return

            self.selected_pedido_id = pedido_id
            self.detalle_pedido_seleccionado.value = pedido.get("items", [])

        except Exception as e:
            self.mensaje.value = f"Error seleccionando: {e}"

    # ----------------------------
    # ELIMINAR
    # ----------------------------
    def eliminar_pedido_seleccionado(self):
        if not self.selected_pedido_id:
            self.mensaje.value = "Debe seleccionar un pedido primero."
            return

        try:
            self.db.delete_pedido(self.selected_pedido_id)
            self.mensaje.value = "Pedido eliminado correctamente."
            self.cargar_historial_pedidos()

        except Exception as e:
            self.mensaje.value = f"Error al eliminar: {e}"