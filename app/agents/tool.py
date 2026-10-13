from dataclasses import dataclass
from typing import Callable


SEGURO = "seguro"
PELIGROSO = "peligroso"
# Herramientas internas de la red (delegar): nunca piden confirmación
INTERNO = "interno"


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    func: Callable
    risk: str = SEGURO

    @property
    def dangerous(self):
        return self.risk == PELIGROSO


def params(propiedades=None, requeridos=None):
    """Atajo para escribir el esquema JSON de los parámetros."""
    return {
        "type": "object",
        "properties": propiedades or {},
        "required": requeridos or [],
    }


def texto(descripcion):
    return {"type": "string", "description": descripcion}


def entero(descripcion):
    return {"type": "integer", "description": descripcion}


def tool(name, description, parameters=None, risk=SEGURO):
    """Decorador que convierte una función en Tool."""

    def wrap(func):
        return Tool(
            name=name,
            description=description,
            parameters=parameters or params(),
            func=func,
            risk=risk,
        )

    return wrap
