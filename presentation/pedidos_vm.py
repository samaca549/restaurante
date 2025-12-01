from domain.models import Plato
from domain.restaurante import Pedido
from presentation.observable import Observable

class PedidosViewModel:
    def __init__(self, firestore_service, ia_service):
        self.db = firestore_service

        self.ia = ia_service 
        
        self.pedido_actual = Observable(None) 
        self.cliente_actual = Observable(None)
        self.platos_menu = Observable([]) 
        self.mensaje = Observable("")
        self.cantidades_temp = {} 

    def cargar_platos(self):
        try:
            platos_list = self.db.get_platos()
            platos_list.sort(key=lambda p: p.nombre)
            self.platos_menu.value = platos_list
        except Exception as e:
            self.mensaje.value = f"Error al cargar menú: {e}"

    def iniciar_nuevo_pedido(self, email: str, nombre: str):
        if not email or not nombre:
            self.mensaje.value = "Faltan datos del cliente"
            return
        try:
            cliente = self.db.get_or_create_cliente(email, nombre)
            self.cliente_actual.value = cliente
            self.pedido_actual.value = Pedido(cliente=cliente)
            self.cantidades_temp = {} 
            self.mensaje.value = f"Pedido abierto para {nombre}"
        except Exception as e:
            self.mensaje.value = f"Error iniciando: {e}"

    def sumar_unidad(self, plato: Plato):
        cant_actual = self.cantidades_temp.get(plato.id, 0)
        self.actualizar_cantidad_plato(plato, cant_actual + 1)

    def actualizar_cantidad_plato(self, plato: Plato, nueva_cantidad: int):
        if not self.pedido_actual.value:
            self.mensaje.value = "¡Primero ingresa los datos del cliente!"
            return False

        pedido = self.pedido_actual.value
        self.cantidades_temp[plato.id] = nueva_cantidad

        item_existente = next((i for i in pedido.items if i['plato_id'] == plato.id), None)

        if nueva_cantidad <= 0:
            if item_existente:
                pedido.items.remove(item_existente)
            self.cantidades_temp[plato.id] = 0
        else:
            if item_existente:
                item_existente['cantidad'] = nueva_cantidad
            else:
                pedido.agregar_item(plato.id, plato.nombre, plato.precio, nueva_cantidad)
        
        pedido._calcular_total()
        self.pedido_actual.notify() 
        return True

    def finalizar_pedido(self):
        if not self.pedido_actual.value or not self.pedido_actual.value.items:
            self.mensaje.value = "El pedido está vacío."
            return
        
        if not self.cliente_actual.value:
            self.mensaje.value = "No hay cliente asignado."
            return

        try:
            pedido_guardar = self.pedido_actual.value
            pedido_id = self.db.save_pedido(pedido_guardar)
            
            cliente_id = self.cliente_actual.value.id
            self.db.add_pedido_to_cliente(cliente_id, pedido_id)
            
            self.mensaje.value = f"¡Pedido finalizado! ID: {pedido_id}"
            
            self.pedido_actual.value = None
            self.cliente_actual.value = None
            self.cantidades_temp = {}
            
        except Exception as e:
            self.mensaje.value = f"Error guardando: {e}"
