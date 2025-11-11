from typing import List, Dict, Any
from domain.models import Plato, Cliente
import datetime

class Pedido:
    """
    Esta es una clase de "dominio rico", como tu ejemplo de Cuenta_Bancaria.
    Contiene la lógica de negocio para manejar un pedido.
    """
    def __init__(self, cliente: Cliente, id: str = None):
        self.id = id
        self.cliente = cliente
        self.creado_en = datetime.datetime.now()
        # Guardamos una lista de tuplas: (Plato, cantidad)
        self._items: List[Dict[str, Any]] = []
        self.total = 0.0

    def agregar_plato(self, plato: Plato, cantidad: int):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva.")
        
        # Guardamos los datos necesarios para el recibo
        self._items.append({
            "plato_id": plato.id,
            "nombre": plato.nombre,
            "precio_unitario": plato.precio,
            "cantidad": cantidad
        })
        self._calcular_total()
        print(f"Plato '{plato.nombre}' agregado. Nuevo total: {self.total}")

    def _calcular_total(self):
        """Método privado para recalcular el total del pedido."""
        self.total = sum(item["precio_unitario"] * item["cantidad"] for item in self._items)
    
    @property
    def items(self):
        return self._items

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el pedido a un diccionario simple para guardar en Firestore."""
        return {
            "cliente_id": self.cliente.id,
            "cliente_nombre": self.cliente.nombre,
            "creado_en": self.creado_en, # Firestore maneja objetos datetime
            "items": self._items, # Lista de diccionarios
            "total": self.total
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], doc_id: str, cliente: Cliente):
        """Reconstruye un pedido. Nota: Requiere que el cliente ya esté cargado."""
        pedido = cls(cliente, id=doc_id)
        pedido._items = data.get("items", [])
        pedido.total = data.get("total", 0.0)
        pedido.creado_en = data.get("creado_en", datetime.datetime.now())
        return pedido