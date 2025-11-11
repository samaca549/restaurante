from dataclasses import dataclass, field
from typing import List, Dict, Any

# Usamos dataclasses para modelos de datos simples
@dataclass
class Plato:
    id: str
    nombre: str
    precio: float
    # Qué insumos y cuánto gasta este plato
    insumos: Dict[str, float] = field(default_factory=dict) # ej: {"harina": 0.5, "queso": 0.2}

    @classmethod
    def from_dict(cls, data: Dict[str, Any], doc_id: str):
        return cls(
            id=doc_id,
            nombre=data.get("nombre", "N/A"),
            precio=data.get("precio", 0.0),
            insumos=data.get("insumos", {})
        )

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "precio": self.precio,
            "insumos": self.insumos
        }

@dataclass
class Cliente:
    id: str
    nombre: str
    email: str
    historial_pedidos: List[str] = field(default_factory=list) # Lista de IDs de Pedidos

    @classmethod
    def from_dict(cls, data: Dict[str, Any], doc_id: str):
        return cls(
            id=doc_id,
            nombre=data.get("nombre", "N/A"),
            email=data.get("email", "N/A"),
            historial_pedidos=data.get("historial_pedidos", [])
        )
    
    def to_dict(self):
        return {
            "nombre": self.nombre,
            "email": self.email,
            "historial_pedidos": self.historial_pedidos
        }

@dataclass
class Empleado:
    uid: str
    email: str
    rol: str  # 'gerente' o 'mesero'

    @classmethod
    def from_dict(cls, data: Dict[str, Any], uid: str):
        return cls(
            uid=uid,
            email=data.get("email", "N/A"),
            rol=data.get("rol", "mesero")
        )
    
    def to_dict(self):
        return {
            "email": self.email,
            "rol": self.rol
        }

@dataclass
class InventarioItem:
    id: str
    nombre: str
    cantidad: float
    unidad: str # "kg", "litros", "unidades"

    @classmethod
    def from_dict(cls, data: Dict[str, Any], doc_id: str):
        return cls(
            id=doc_id,
            nombre=data.get("nombre", "N/A"),
            cantidad=data.get("cantidad", 0.0),
            unidad=data.get("unidad", "N/A")
        )

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "cantidad": self.cantidad,
            "unidad": self.unidad
        }