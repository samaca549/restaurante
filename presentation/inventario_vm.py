from presentation.observable import Observable
from data.firestore_service import FirestoreService
from typing import List
from domain.models import InventarioItem

class InventarioViewModel:
    def __init__(self, firestore_service: FirestoreService):
        self.fs = firestore_service
        self.inventario_lista = Observable([]) # Lista[InventarioItem]
        self.mensaje = Observable(None)
    # presentation/viewmodels/inventario_vm.py

# ... (Clase InventarioViewModel)

    # ... (cargar_inventario, actualizar_stock existentes)

    def crear_nuevo_item(self, nombre: str, cantidad: float, unidad: str):
        try:
            cantidad = float(cantidad)
            if cantidad < 0: raise ValueError("La cantidad debe ser positiva.")
            
            self.fs.create_inventario_item(nombre, cantidad, unidad)
            self.mensaje.value = f"Ítem '{nombre}' creado con éxito."
            self.cargar_inventario() # Recargar la lista
        except ValueError as e:
            self.mensaje.value = f"Error de valor: {e}"
        except Exception as e:
            self.mensaje.value = f"Error al crear ítem: {e}"

    def cargar_inventario(self):
        try:
            items = self.fs.get_inventario()
            self.inventario_lista.value = items
        except Exception as e:
            self.mensaje.value = f"Error cargando inventario: {e}"
            
    def actualizar_stock(self, item: InventarioItem, nueva_cantidad: float):
        try:
            item.cantidad = nueva_cantidad
            self.fs.update_inventario_item(item)
            self.mensaje.value = f"Stock de {item.nombre} actualizado a {nueva_cantidad}."
            # Recargamos la lista para que la UI se refresque
            self.cargar_inventario()
        except Exception as e:
            self.mensaje.value = f"Error actualizando stock: {e}"