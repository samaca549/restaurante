from domain.models import Plato, Cliente, InventarioItem
from domain.restaurante import Pedido
from typing import List

class FirestoreService:
    """
    Maneja todas las operaciones de la base de datos Firestore.
    """
    def __init__(self, firestore_client, auth_client):
        self.db = firestore_client
        self.auth = auth_client
        self.platos_col = self.db.collection("platos")
        self.pedidos_col = self.db.collection("pedidos")
        self.clientes_col = self.db.collection("clientes")
        self.inventario_col = self.db.collection("inventario")

    # --- Platos (Menú) ---
    def get_platos(self) -> List[Plato]:
        platos = []
        for doc in self.platos_col.stream():
            platos.append(Plato.from_dict(doc.to_dict(), doc.id))
        return platos

    # --- Inventario ---
    def get_inventario(self) -> List[InventarioItem]:
        items = []
        for doc in self.inventario_col.stream():
            items.append(InventarioItem.from_dict(doc.to_dict(), doc.id))
        return items

    def update_inventario_item(self, item: InventarioItem):
        self.inventario_col.document(item.id).set(item.to_dict())

    # --- Clientes ---
    def get_or_create_cliente(self, email: str, nombre: str) -> Cliente:
        """Busca un cliente por email. Si no existe, lo crea."""
        query = self.clientes_col.where("email", "==", email).limit(1).stream()
        existing = next(query, None)
        
        if existing:
            print(f"Cliente encontrado: {email}")
            return Cliente.from_dict(existing.to_dict(), existing.id)
        else:
            print(f"Cliente nuevo, creando: {email}")
            nuevo_cliente = Cliente(id=None, nombre=nombre, email=email)
            # Firestore genera el ID
            _, doc_ref = self.clientes_col.add(nuevo_cliente.to_dict())
            nuevo_cliente.id = doc_ref.id
            return nuevo_cliente

    def add_pedido_to_cliente(self, cliente_id: str, pedido_id: str):
        """Agrega un ID de pedido al historial del cliente."""
        cliente_ref = self.clientes_col.document(cliente_id)

        from google.cloud.firestore_v1.field_path import FieldPath
        from google.cloud import firestore
        cliente_ref.update({"historial_pedidos": firestore.ArrayUnion([pedido_id])})

    # --- Pedidos ---
    def save_pedido(self, pedido: Pedido) -> str:
        """Guarda un nuevo pedido en Firestore."""
        pedido_dict = pedido.to_dict()
        _, doc_ref = self.pedidos_col.add(pedido_dict)
        print(f"Pedido guardado con ID: {doc_ref.id}")
        return doc_ref.id
    
    def get_all_pedidos(self) -> List[dict]:
        """Obtiene todos los pedidos (como dicts) para la IA."""
        return [doc.to_dict() for doc in self.pedidos_col.stream()]
    def create_inventario_item(self, nombre: str, cantidad: float, unidad: str):
        """Crea un nuevo ítem de inventario."""
        from domain.models import InventarioItem
        
        # El ID se generará automáticamente por Firestore
        nuevo_item = InventarioItem(id=None, nombre=nombre, cantidad=cantidad, unidad=unidad)
        
        _, doc_ref = self.inventario_col.add(nuevo_item.to_dict())
        print(f"Nuevo ítem de inventario creado con ID: {doc_ref.id}")


    def get_all_pedidos_with_ids(self) -> List[dict]:
        """Obtiene todos los pedidos, incluyendo su ID de documento."""
        pedidos = []
        for doc in self.pedidos_col.stream():
            data = doc.to_dict()
            data["id"] = doc.id  # <-- Importante: añadimos el ID
            pedidos.append(data)
        # Ordenar por fecha, más nuevos primero
        pedidos.sort(key=lambda p: p.get("fecha_creacion", 0), reverse=True)
        return pedidos

    def delete_pedido(self, pedido_id: str) -> None:
        """Elimina un pedido por su ID."""
        try:
            self.pedidos_col.document(pedido_id).delete()
            print(f"Pedido {pedido_id} eliminado.")
            

            
        except Exception as e:
            print(f"Error al eliminar pedido {pedido_id}: {e}")
            raise  # Relanzar la excepción para que el VM la maneje
