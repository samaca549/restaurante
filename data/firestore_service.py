# data/firestore_service.py
from domain.models import Plato, Cliente, InventarioItem
from domain.restaurante import Pedido
from typing import List, Optional
from google.cloud import firestore 
from google.cloud.firestore_v1.base_query import FieldFilter

class FirestoreService:
    
    def __init__(self, firestore_client, auth_client):
        self.db = firestore_client 
        self.auth = auth_client
        
        # Referencias a colecciones
        self.platos_col = self.db.collection("platos")
        self.pedidos_col = self.db.collection("pedidos")
        self.clientes_col = self.db.collection("clientes")
        self.inventario_col = self.db.collection("inventario")

    # --- 1. PLATOS ---
    def get_platos(self) -> List[Plato]:
        platos = []
        for doc in self.platos_col.stream():
            try:
                platos.append(Plato.from_dict(doc.to_dict(), doc.id))
            except Exception:
                pass
        return platos

    # --- 2. INVENTARIO ---
    def get_inventario(self) -> List[InventarioItem]:
        items = []
        for doc in self.inventario_col.stream():
            items.append(InventarioItem.from_dict(doc.to_dict(), doc.id))
        return items

    def add_inventario_item(self, item: InventarioItem):
        self.inventario_col.add(item.to_dict())

    def update_inventario_cantidad(self, item_id: str, nueva_cantidad: float):
        self.inventario_col.document(item_id).update({"cantidad": nueva_cantidad})

    # --- 3. CLIENTES ---
    def get_or_create_cliente(self, email: str, nombre: str) -> Cliente:
        query = self.clientes_col.where(filter=FieldFilter("email", "==", email)).limit(1).stream()
        existing = next(query, None)
        
        if existing:
            return Cliente.from_dict(existing.to_dict(), existing.id)
        else:
            nuevo_cliente = Cliente(id=None, nombre=nombre, email=email)
            _, doc_ref = self.clientes_col.add(nuevo_cliente.to_dict())
            nuevo_cliente.id = doc_ref.id
            return nuevo_cliente

    def add_pedido_to_cliente(self, cliente_id: str, pedido_id: str):
        cliente_ref = self.clientes_col.document(cliente_id)
        cliente_ref.update({"historial_pedidos": firestore.ArrayUnion([pedido_id])})

    # --- 4. PEDIDOS ---
    def save_pedido(self, pedido: Pedido) -> str:
        pedido_dict = pedido.to_dict()
        _, doc_ref = self.pedidos_col.add(pedido_dict)
        return doc_ref.id
    
    def get_all_pedidos(self) -> List[dict]:
        return [doc.to_dict() for doc in self.pedidos_col.stream()]

    # --- 5. HISTORIAL ---
    def get_all_pedidos_with_ids(self) -> List[dict]:
        pedidos = []
        for doc in self.pedidos_col.stream():
            data = doc.to_dict()
            data["id"] = doc.id
            pedidos.append(data)
        pedidos.sort(key=lambda p: str(p.get("creado_en", "")), reverse=True)
        return pedidos

    def get_pedido_by_id(self, pedido_id: str) -> Optional[dict]:
        try:
            doc_ref = self.pedidos_col.document(pedido_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                return data
            else:
                return None
        except Exception as e:
            print(f"Error obteniendo pedido {pedido_id}: {e}")
            return None

    def delete_pedido(self, pedido_id: str) -> None:
        self.pedidos_col.document(pedido_id).delete()
