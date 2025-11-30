from presentation.observable import Observable
from domain.models import InventarioItem

class InventarioViewModel:
    def __init__(self, firestore_service, ia_service):
        self.db = firestore_service
        self.ia = ia_service
        
        self.inventario_lista = Observable([])
        self.mensaje = Observable("")
        self.recomendacion = Observable("")

    def cargar_inventario(self):
        try:
            items = self.db.get_inventario()
            # Ordenar alfabéticamente
            items.sort(key=lambda x: x.nombre.lower())
            self.inventario_lista.value = items
            self._set_recomendacion()
        except Exception as e:
            self.mensaje.value = f"Error cargando inventario: {e}"

    def _set_recomendacion(self):
        items = self.inventario_lista.value
        if items and self.ia:
            nombre, frase = self.ia.obtener_recomendacion_inventario(items)
            self.recomendacion.value = f"{frase} ({nombre})"
        else:
            self.recomendacion.value = "No hay recomendaciones disponibles."

    def crear_nuevo_item(self, nombre, cantidad, unidad):
        try:
            cant_float = float(cantidad)
            # Creamos objeto temporal (el ID se generará en BD)
            nuevo_item = InventarioItem(id=None, nombre=nombre, cantidad=cant_float, unidad=unidad)
            
            # Guardar en BD
            self.db.add_inventario_item(nuevo_item)
            
            self.mensaje.value = f"✅ Ítem '{nombre}' agregado correctamente."
            self.cargar_inventario() # Recargar lista visual
        except ValueError:
            self.mensaje.value = "Error: La cantidad debe ser numérica."
        except Exception as e:
            self.mensaje.value = f"Error al crear: {e}"

    def actualizar_stock(self, item: InventarioItem, nueva_cantidad: float):
        try:
            # Actualizamos en BD
            self.db.update_inventario_cantidad(item.id, nueva_cantidad)
            
            self.mensaje.value = f"🔄 Stock de '{item.nombre}' actualizado a {nueva_cantidad}."
            self.cargar_inventario()
        except Exception as e:
            self.mensaje.value = f"Error al actualizar: {e}"