from typing import List, Dict, Any, Optional
from domain.models import Cliente
import datetime

class Pedido:
    # Usamos Optional[str] para permitir que el ID sea None al principio
    def __init__(self, cliente: Cliente, id: Optional[str] = None):
        self.id = id
        self.cliente = cliente
        self.creado_en = datetime.datetime.now()
        self._items: List[Dict[str, Any]] = []
        self.total = 0.0

    def agregar_item(self, plato_id: str, nombre: str, precio_unitario: float, cantidad: int):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva.")
        
        self._items.append({
            "plato_id": plato_id,
            "nombre": nombre,
            "precio_unitario": precio_unitario,
            "cantidad": cantidad
        })
        self._calcular_total()

    def _calcular_total(self):
        self.total = sum(item["precio_unitario"] * item["cantidad"] for item in self._items)
    
    @property
    def items(self):
        return self._items

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cliente_id": self.cliente.id,
            "cliente_nombre": self.cliente.nombre,
            "creado_en": self.creado_en,
            "items": self._items,
            "total": self.total
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], doc_id: str, cliente: Cliente):
        pedido = cls(cliente, id=doc_id)
        pedido._items = data.get("items", [])
        pedido.total = data.get("total", 0.0)
        fecha = data.get("creado_en")
        if fecha:
             pedido.creado_en = fecha
        return pedido