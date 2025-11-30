from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Plato:
    id: Optional[str] # <--- Arreglado: Puede ser texto o None
    nombre: str
    precio: float
    descripcion: str = ""
    insumos: Dict[str, float] = field(default_factory=dict)
    imagen_path: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], doc_id: str):
        return cls(
            id=doc_id,
            nombre=data.get("nombre", "N/A"),
            precio=float(data.get("precio", 0.0)),
            descripcion=data.get("descripcion", ""),
            insumos=data.get("insumos", {}),
            imagen_path=data.get("imagen_path", None)
        )

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "precio": self.precio,
            "descripcion": self.descripcion,
            "insumos": self.insumos,
            "imagen_path": self.imagen_path
        }

@dataclass
class Cliente:
    id: Optional[str] # <--- Arreglado
    nombre: str
    email: str
    historial_pedidos: List[str] = field(default_factory=list)

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
class InventarioItem:
    id: Optional[str] # <--- Arreglado
    nombre: str
    cantidad: float
    unidad: str 

    @classmethod
    def from_dict(cls, data: Dict[str, Any], doc_id: str):
        return cls(
            id=doc_id,
            nombre=data.get("nombre", "N/A"),
            cantidad=float(data.get("cantidad", 0.0)),
            unidad=data.get("unidad", "unidad")
        )

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "cantidad": self.cantidad,
            "unidad": self.unidad
        }

@dataclass
class Empleado:
    uid: str
    email: str
    rol: str 

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